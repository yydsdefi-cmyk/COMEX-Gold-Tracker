"""Export a small public data package without copying arbitrary local files."""
import argparse
import hashlib
import html
import json
from pathlib import Path
from datetime import datetime, timedelta, timezone

from .dataset import atomic_write, load_observations, now_utc, write_json
from .parser import ReportError


def consumer_health(latest, now=None):
    """Re-evaluate timestamps at consumption time; a static success can expire."""
    now = now or datetime.now(timezone.utc)
    attempt = latest.get("last_update", {})
    stamp = attempt.get("attempted_at_utc")
    try:
        attempted = datetime.fromisoformat(stamp)
        if attempted.tzinfo is None:
            raise ValueError("timezone missing")
        age = (now - attempted).total_seconds()
    except (TypeError, ValueError):
        return "UNCONFIRMED_UPDATE_TIME"
    if age < -300:
        return "FUTURE_UPDATE_TIME"
    if age > timedelta(hours=26).total_seconds():
        return "SCHEDULER_OVERDUE"
    if not latest.get("available"):
        return "UNAVAILABLE"
    if latest.get("update_status") not in ("OK", "UNCHANGED"):
        return "UPDATE_FAILED_OR_UNCONFIRMED"
    if latest.get("freshness") == "STALE":
        return "REPORT_STALE"
    return "RECENT_SUCCESS_SNAPSHOT"


def export_public(data_dir, output_dir):
    data_dir, output_dir = Path(data_dir).resolve(), Path(output_dir).resolve()
    if output_dir == data_dir or output_dir.is_relative_to(data_dir) or data_dir.is_relative_to(output_dir):
        raise ReportError("Export and archive directories must be separate")
    if output_dir.exists() and any(output_dir.iterdir()):
        raise ReportError("Use a new empty export directory; stale files must not leak into publication")
    latest = json.loads((data_dir / "latest.json").read_text(encoding="utf-8"))
    # A failed archive-validation snapshot deliberately publishes no historical files.
    if latest.get("available"):
        load_observations(data_dir)
    output_dir.mkdir(parents=True, exist_ok=True)
    names = ["latest.json", "fetch_status.json", "daily_brief.md"]
    if latest.get("available"):
        names += ["history.csv", "validation.json"]
    for name in names:
        atomic_write(output_dir / name, (data_dir / name).read_text(encoding="utf-8"))
    if latest.get("available"):
        provenance = latest["provenance"]
        raw = (data_dir / provenance["raw_path"]).resolve()
        if not raw.is_relative_to(data_dir / "raw"):
            raise ReportError("Raw path leaves archive")
        blob = raw.read_bytes()
        if hashlib.sha256(blob).hexdigest() != provenance["sha256"]:
            raise ReportError("Published report hash mismatch")
        dest = output_dir / provenance["raw_path"]
        dest.parent.mkdir(parents=True, exist_ok=True)
        dest.write_bytes(blob)
    health = {"published_at_utc": now_utc(), "snapshot_health": consumer_health(latest),
              "consumer_must_recheck_time": True,
              "maximum_update_age_hours": 26,
              "update_status": latest.get("update_status"),
              "last_update": latest.get("last_update"),
              "note": "Static health expires. Compare attempted_at_utc with the current time on EVERY read."}
    write_json(output_dir / "health.json", health)
    brief = (data_dir / "daily_brief.md").read_text(encoding="utf-8")
    atomic_write(output_dir / "latest.txt", brief + "\n消费时必须检查 last_update.attempted_at_utc：距当前时间超过 26 小时应标记云端更新逾期。\n")
    # Plain HTML mirrors the text for browsing tools that cannot open JSON/text.
    atomic_write(output_dir / "index.html", '<!doctype html><meta charset="utf-8"><title>COMEX Gold data</title>'
                 '<p><a href="latest.json">JSON</a> | <a href="latest.txt">Text</a> | '
                 '<a href="health.json">Health</a></p><pre>' + html.escape(brief) + '</pre>')
    manifest = {p.relative_to(output_dir).as_posix(): hashlib.sha256(p.read_bytes()).hexdigest()
                for p in sorted(output_dir.rglob("*")) if p.is_file()}
    write_json(output_dir / "manifest.json", {"sha256": manifest})
    return health


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--data-dir", type=Path, default=Path("data"))
    parser.add_argument("--output-dir", type=Path, required=True)
    args = parser.parse_args()
    print(json.dumps(export_public(args.data_dir, args.output_dir), ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
