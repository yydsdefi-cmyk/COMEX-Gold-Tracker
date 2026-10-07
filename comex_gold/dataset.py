"""Auditable observations, conservative change windows, and daily-chat output."""
import csv
import hashlib
import io
import json
import os
from pathlib import Path
from datetime import date, datetime, timedelta, timezone
from decimal import Decimal
from uuid import uuid4

from .parser import SOURCE_PAGE, SOURCE_URL, ReportError, parse_report

KL = timezone(timedelta(hours=8))
SERIES = {"total": "total_oz", "registered": "registered_oz", "eligible": "eligible_oz"}


def now_utc():
    return datetime.now(timezone.utc).isoformat()


def local_today():
    return datetime.now(KL).date()


def atomic_write(path, text):
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    temp = path.with_name(path.name + "." + uuid4().hex + ".tmp")
    try:
        with temp.open("w", encoding="utf-8", newline="") as handle:
            handle.write(text)
            handle.flush()
            os.fsync(handle.fileno())
        os.replace(temp, path)
    finally:
        if temp.exists():
            temp.unlink()


def write_json(path, obj):
    atomic_write(path, json.dumps(obj, ensure_ascii=False, indent=2, allow_nan=False) + "\n")


def candidate_weekdays(start, end):
    """Conservative candidates, NOT an assertion of CME's reporting calendar."""
    result = []
    d = start
    while d <= end:
        if d.weekday() < 5:
            result.append(d.isoformat())
        d += timedelta(days=1)
    return result


def recent_candidates(end, count):
    values = []
    d = end
    while len(values) < count:
        if d.weekday() < 5:
            values.append(d.isoformat())
        d -= timedelta(days=1)
    return list(reversed(values))


def oz(n):
    return float(Decimal(n) / 1000) if n is not None else None


def pct(change, base):
    return float((Decimal(change) / Decimal(base) * 100).quantize(Decimal("0.000001"))) if base else None


def totals(observation, field="today"):
    return {k: observation["summary"][k]["balances"][field] for k in SERIES}


def store_observation(data_dir, blob, transport):
    parsed = parse_report(blob)
    if date.fromisoformat(parsed["report_date"]) > local_today():
        raise ReportError("Report Date is in the future")
    digest = hashlib.sha256(blob).hexdigest()
    data_dir = Path(data_dir)
    raw_relative = f"raw/{parsed['date']}/{digest}.{parsed['file_type']}"
    raw = data_dir / raw_relative
    raw.parent.mkdir(parents=True, exist_ok=True)
    if not raw.exists():
        raw.write_bytes(blob)
    elif hashlib.sha256(raw.read_bytes()).hexdigest() != digest:
        raise ReportError("Existing raw archive hash mismatch")
    observation = {**parsed, "provenance": {
        "source": "CME", "source_url": SOURCE_URL, "source_page": SOURCE_PAGE,
        "captured_at_utc": now_utc(), "raw_path": raw_relative, "sha256": digest,
        "bytes": len(blob), **transport,
    }}
    path = data_dir / "observations" / (parsed["date"] + "_" + digest + ".json")
    existed = path.exists()
    if not existed:
        write_json(path, observation)
    elif transport["method"] == "official_https_download":
        # Preserve first-seen time but strengthen browser/manual provenance with a
        # real HTTP capture, and retain each retrieval separately for audit.
        saved = json.loads(path.read_text(encoding="utf-8"))
        observation["provenance"]["captured_at_utc"] = saved["provenance"]["captured_at_utc"]
        observation["provenance"]["last_verified_at_utc"] = now_utc()
        write_json(path, observation)
    write_json(data_dir / "captures" / (uuid4().hex + ".json"), {
        "captured_at_utc": now_utc(), "date": parsed["date"], "report_date": parsed["report_date"],
        "sha256": digest, "source_url": SOURCE_URL, **transport,
    })
    return parsed["date"], digest, existed


def load_observations(data_dir):
    """Reparse archived bytes; normalized JSON is never an unchecked authority."""
    by_date = {}
    for path in sorted((Path(data_dir) / "observations").glob("*.json")):
        saved = json.loads(path.read_text(encoding="utf-8"))
        provenance = saved["provenance"]
        raw = (Path(data_dir) / provenance["raw_path"]).resolve()
        if not raw.is_relative_to((Path(data_dir) / "raw").resolve()):
            raise ReportError("Archive path leaves raw directory")
        blob = raw.read_bytes()
        if hashlib.sha256(blob).hexdigest() != provenance["sha256"]:
            raise ReportError(f"Archive hash mismatch: {raw.name}")
        parsed = parse_report(blob)
        if parsed["date"] != saved["date"]:
            raise ReportError("Observation date differs from archived source")
        item = {**parsed, "provenance": provenance}
        old = by_date.get(item["date"])
        priority = lambda x: (x["provenance"]["method"] == "official_https_download",
                              x["report_date"], x["provenance"].get("last_verified_at_utc", x["provenance"]["captured_at_utc"]))
        if old is None or priority(item) > priority(old):
            by_date[item["date"]] = item
    return [by_date[k] for k in sorted(by_date)]


def window_change(observations, n):
    if len(observations) <= n:
        return None, "INSUFFICIENT_HISTORY"
    window = observations[-n - 1:]
    dates = [o["date"] for o in window]
    candidates = candidate_weekdays(date.fromisoformat(dates[0]), date.fromisoformat(dates[-1]))
    if dates != candidates:
        return None, "MISSING_WEEKDAY_OR_UNCONFIRMED_HOLIDAY"
    for prior, current in zip(window, window[1:]):
        if totals(prior) != totals(current, "previous"):
            return None, "PREVIOUS_BALANCE_MISMATCH_OR_REVISION"
    return {"baseline_date": dates[0], "baseline": totals(window[0]),
            "current": totals(window[-1])}, "AVAILABLE_CONSECUTIVE_WEEKDAYS"


def continuity_issues(observations):
    issues = []
    for prior, current in zip(observations, observations[1:]):
        before, previous = totals(prior), totals(current, "previous")
        mismatches = {key: {"prior_total_today_oz": oz(before[key]),
                            "next_prev_total_oz": oz(previous[key])}
                      for key in SERIES if before[key] != previous[key]}
        if mismatches:
            issues.append({"prior_activity_date": prior["date"],
                           "next_activity_date": current["date"],
                           "status": "PREVIOUS_BALANCE_MISMATCH_OR_REVISION",
                           "series": mismatches,
                           "interpretation": "Do not treat the difference between reports as physical withdrawal; cause is not confirmed."})
    return issues


def inventory_alert(current, previous):
    if previous == 0:
        return "UNKNOWN"
    change = Decimal(current - previous) / Decimal(previous) * 100
    for threshold, level in [(-5, "RED"), (-3, "ORANGE"), (-1, "YELLOW")]:
        if change < threshold:
            return level
    return "NORMAL"


def make_latest(observations, fetch, as_of=None):
    as_of = as_of or local_today()
    out = {"schema_version": 1, "source": "CME", "as_of_local_date": as_of.isoformat(),
           "as_of_timezone": "Asia/Kuala_Lumpur", "generated_at_utc": now_utc(),
           "update_status": fetch.get("status", "NOT_RUN"), "last_update": fetch,
           "available": bool(observations), "status": "UNKNOWN"}
    if not observations:
        out.update(date=None, report_date=None, total_oz=None, registered_oz=None,
                   eligible_oz=None, registered_ratio=None, freshness="UNAVAILABLE")
        return out
    last = observations[-1]
    current, previous = totals(last), totals(last, "previous")
    out.update(date=last["date"], activity_date=last["date"], report_date=last["report_date"],
               unit=last["unit"], scope=last["scope"],
               **{field: oz(current[k]) for k, field in SERIES.items()},
               registered_ratio=pct(current["registered"], current["total"]),
               pledged_oz=oz(last["summary"]["pledged"]["balances"]["today"]) if "pledged" in last["summary"] else None,
               pledged_accounting=last["pledged_accounting"],
               provenance=last["provenance"], observation_count=len(observations),
               reconciliation_checks_passed=len(last["checks"]))
    out["history_continuity_issues"] = continuity_issues(observations)
    report_date = date.fromisoformat(last["report_date"])
    age = len(candidate_weekdays(report_date + timedelta(days=1), as_of))
    out.update(report_age_weekdays=age,
               freshness="STALE" if age > 1 else "WITHIN_AGE_LIMIT",
               freshness_rule="Report Date age <= 1 weekday; conservative, not a confirmed CME publication calendar",
               is_latest_confirmed=False)
    windows = {}
    for n in (1, 5, 10, 20):
        if n == 1:
            baseline, reason = {"baseline": previous, "current": current, "baseline_date": None}, "CME_PREV_TOTAL"
        else:
            baseline, reason = window_change(observations, n)
        windows[f"{n}d"] = {"status": reason, "baseline_date": baseline["baseline_date"] if baseline else None}
        for key in SERIES:
            prefix = "" if key == "total" else key + "_"
            delta = baseline["current"][key] - baseline["baseline"][key] if baseline else None
            out[f"{prefix}change_{n}d_oz"] = oz(delta)
            out[f"{prefix}change_{n}d_pct"] = pct(delta, baseline["baseline"][key]) if baseline else None
    out["change_windows"] = windows
    out["status"] = inventory_alert(current["total"], previous["total"])
    movement = {}
    for key, item in last["summary"].items():
        movement[key] = {field + "_oz": oz(item["balances"][field])
                         for field in ("previous", "received", "withdrawn", "net_change", "adjustment")}
    out["movements"] = movement
    # Transparent user heuristics, not CME shortage criteria.
    registered_fast = (Decimal(current["registered"] - previous["registered"]) /
                       Decimal(previous["registered"]) * 100 < -3) if previous["registered"] else False
    five_window, five_reason = window_change(observations, 5)
    persistent = None if five_window is None else all(
        totals(o)["registered"] < totals(o, "previous")["registered"] for o in observations[-5:])
    out["registered_alert"] = {
        "rapid_decline_1d": registered_fast, "persistent_decline_5_consecutive_days": persistent,
        "persistent_check_status": five_reason,
        "rule": "Rapid: Registered 1D < -3%; persistent: declines on each of 5 consecutive verified weekdays",
        "shortage_inference": False,
    }
    out["interpretation"] = "Inventory movements only. Eligible-only declines do not establish deliverable-gold shortage. Pledged is already inside Registered."
    return out


def validation_report(observations, as_of=None):
    end = date.fromisoformat(observations[-1]["date"]) if observations else (as_of or local_today())
    expected = recent_candidates(end, 20)
    by_date = {o["date"]: o for o in observations}
    verified = [{"activity_date": d, "report_date": by_date[d]["report_date"],
                 "sha256": by_date[d]["provenance"]["sha256"],
                 "source_url": by_date[d]["provenance"]["source_url"],
                 "archive_url": by_date[d]["provenance"].get("archive_url"),
                 "archive_timestamp_utc": by_date[d]["provenance"].get("archive_timestamp_utc"),
                 "cdx_digest_verified": by_date[d]["provenance"].get("cdx_digest_verified"),
                 "checks_passed": len(by_date[d]["checks"]),
                 "verified_values_oz": {k: oz(v) for k, v in totals(by_date[d]).items()},
                 "provenance_method": by_date[d]["provenance"]["method"]}
                for d in expected if d in by_date]
    missing = [d for d in expected if d not in by_date]
    return {"status": "COMPLETE_20_OBSERVATIONS" if not missing else "INCOMPLETE",
            "target_count": 20, "verified_report_count": len(verified),
            "candidate_dates": expected, "verified": verified, "not_obtained_dates": missing,
            "total_observation_count": len(observations),
            "history_continuity_issues": continuity_issues(observations),
            "calendar_note": "Weekday candidates, not a verified CME trading/reporting calendar; holidays remain unclassified, never filled with guessed data.",
            "verification_note": "Source bytes are reparsed and balances/detail reconciled. This is not an independent CME audit. Local imports retain their declared provenance.",
            "twenty_day_change_requires": "21 consecutive dated observations, with no unclassified gaps"}


def chat_report(latest, validation):
    lines = ["# COMEX Gold — 官方库存数据", "",
             f"数据生成时间：{latest['generated_at_utc']}",
             f"更新状态：{latest['update_status']}；数据时效：{latest['freshness']}"]
    if latest.get("last_update", {}).get("error"):
        lines.append("本次更新失败：" + latest["last_update"]["error"] + "。以下为上次核验数据，不能写成今日新数据。")
    if latest["available"]:
        lines += [f"库存日期（Activity Date）：**{latest['date']}**；报告日期：{latest['report_date']}",
                  "", "单位：troy oz（金衡盎司）；保持 CME Gold Stocks 原始 Combined Total 口径（GC/4GC）。", "",
                  "| 项目 | 库存 | 单日变化 | 单日变化 % |", "|---|---:|---:|---:|"]
        for key, title in [("total", "Combined Total"), ("registered", "Registered"), ("eligible", "Eligible")]:
            prefix = "" if key == "total" else key + "_"
            p = latest[f"{prefix}change_1d_pct"]
            p_text = "不可计算" if p is None else f"{p:.6f}%"
            lines.append(f"| {title} | {latest[SERIES[key]]:,.3f} | {latest[f'{prefix}change_1d_oz']:+,.3f} | {p_text} |")
        ratio = latest['registered_ratio']
        lines += ["", "Registered Ratio：" + (f"{ratio:.6f}%" if ratio is not None else "不可计算"),
                  f"库存变化分级：{latest['status']}（用户阈值，非 CME 风险评级）。", "",
                  "单日变化直接核对 CME PREV TOTAL 与 TOTAL TODAY；不补造前一个日期的历史记录。"]
        for n in (5, 10, 20):
            value = latest[f"change_{n}d_pct"]
            lines.append(f"{n}D 变化：" + (f"{value:+.6f}%" if value is not None else "暂不可计算") +
                         f"（{latest['change_windows'][f'{n}d']['status']}）。")
        lines += ["", "| 库存分类 | 5D 变化 | 10D 变化 | 20D 变化 |",
                  "|---|---:|---:|---:|"]
        for key, title in [("registered", "Registered"), ("eligible", "Eligible")]:
            values = []
            for n in (5, 10, 20):
                absolute = latest[f"{key}_change_{n}d_oz"]
                percentage = latest[f"{key}_change_{n}d_pct"]
                values.append("暂不可计算" if absolute is None else
                              f"{absolute:+,.3f} oz / " +
                              (f"{percentage:+.6f}%" if percentage is not None else "百分比不可计算"))
            lines.append("| " + title + " | " + " | ".join(values) + " |")
        if latest.get("history_continuity_issues"):
            lines.append("历史余额衔接异常：" + "；".join(
                f"{item['prior_activity_date']} → {item['next_activity_date']}"
                for item in latest["history_continuity_issues"]) +
                "。相邻报告前后余额不一致，原因未确认，不能解读为同量实物出库。")
        lines += ["", "Pledged 已在 Registered 内，不另加；Eligible 单独下降不等于交割黄金短缺。",
                  "Registered 快速下降标记：" + str(latest['registered_alert']['rapid_decline_1d']) +
                  "；连续下降标记：" + str(latest['registered_alert']['persistent_decline_5_consecutive_days']),
                  f"原始报告 SHA-256：`{latest['provenance']['sha256']}`",
                  f"原始文件：`{latest['provenance']['raw_path']}`"]
    else:
        lines += ["", "目前没有通过校验的官方库存报告。所有库存值缺失，不能写成 0。"]
    lines += ["", f"20 日核验进度：{validation['verified_report_count']}/20（{validation['status']}）。",
              "未取得日期只是工作日候选，不代表已确认的 CME 交易日。",
              f"来源：[CME Gold Stocks 原始文件]({SOURCE_URL})；[官方入口]({SOURCE_PAGE})。", "",
              "## 交给日报对话的约束", "",
              "请引用上面的真实数值，并同时保留 Activity Date 与 Report Date。若更新失败或数据过旧，明确写上次可得数据及日期；",
              "5D/10D/20D 按已核验的连续工作日候选报告计算，不是自然日；每个窗口保留实际基准日期。缺失的变化不估算、不写成 0；NORMAL 仅表示本报告总库存单日变化未触发用户阈值，不能表示不存在市场风险。",
              "这份文件是一次数据快照，未来日报需要新下载并核验的版本。"]
    return "\n".join(lines) + "\n"


def publish(data_dir, fetch=None, as_of=None):
    data_dir = Path(data_dir)
    fetch_path = data_dir / "fetch_status.json"
    if fetch is None:
        fetch = json.loads(fetch_path.read_text(encoding="utf-8")) if fetch_path.exists() else {"status": "NOT_RUN"}
    else:
        write_json(fetch_path, fetch)
    observations = load_observations(data_dir)
    latest = make_latest(observations, fetch, as_of)
    validation = validation_report(observations, as_of)
    buffer = io.StringIO(newline="")
    fields = ["date", "report_date", "total_oz", "registered_oz", "eligible_oz", "registered_ratio", "pledged_oz",
              "total_previous_oz", "received_oz", "withdrawn_oz", "net_change_oz", "adjustment_oz",
              "source", "source_url", "captured_at_utc", "sha256", "raw_path", "provenance_method"]
    fields += ["archive_url", "archive_timestamp_utc", "cdx_sha1_base32", "cdx_digest_verified"]
    writer = csv.DictWriter(buffer, fieldnames=fields)
    writer.writeheader()
    for o in observations:
        v = totals(o)
        row = {"date": o["date"], "report_date": o["report_date"],
               **{f: f"{oz(v[k]):.3f}" for k, f in SERIES.items()},
               "registered_ratio": pct(v["registered"], v["total"]),
               "pledged_oz": oz(o["summary"]["pledged"]["balances"]["today"]) if "pledged" in o["summary"] else None,
               "source": "CME", "provenance_method": o["provenance"]["method"],
               **{k: o["provenance"][k] for k in ("source_url", "captured_at_utc", "sha256", "raw_path")}}
        row.update({k: o["provenance"].get(k, "") for k in
                    ("archive_url", "archive_timestamp_utc", "cdx_sha1_base32", "cdx_digest_verified")})
        movement = o["summary"]["total"]["balances"]
        row["total_previous_oz"] = oz(movement["previous"])
        for k in ("received", "withdrawn", "net_change", "adjustment"):
            row[k + "_oz"] = oz(movement[k])
        writer.writerow(row)
    atomic_write(data_dir / "history.csv", buffer.getvalue())
    write_json(data_dir / "validation.json", validation)
    atomic_write(data_dir / "daily_brief.md", chat_report(latest, validation))
    write_json(data_dir / "latest.json", latest)  # Consumer-facing commit is written last.
    return latest
