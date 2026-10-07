import argparse
from contextlib import contextmanager
from datetime import date
import hashlib
import json
from pathlib import Path
import sys

from .collector import fetch_report
from .dataset import local_today, now_utc, publish, store_observation, write_json
from .parser import ReportError, SOURCE_URL


def publish_unavailable(data_dir, attempt):
    latest = {"schema_version": 1, "source": "CME", "available": False,
              "status": "UNKNOWN", "update_status": "FAILED", "freshness": "UNAVAILABLE",
              "date": None, "report_date": None, "total_oz": None,
              "registered_oz": None, "eligible_oz": None, "registered_ratio": None,
              "last_update": attempt}
    write_json(data_dir / "fetch_status.json", attempt)
    write_json(data_dir / "latest.json", latest)
    from .dataset import atomic_write
    atomic_write(data_dir / "daily_brief.md", "COMEX Gold 数据不可用：" + attempt["error"] + "\n旧输出不得作为本次已核验数据使用。\n")
    return latest


@contextmanager
def update_lock(data_dir):
    data_dir.mkdir(parents=True, exist_ok=True)
    lock = data_dir / ".update.lock"
    try:
        handle = lock.open("x", encoding="utf-8")
    except FileExistsError as exc:
        raise ReportError("Another update holds data/.update.lock; check that process before removing a stale lock") from exc
    try:
        with handle:
            handle.write(now_utc())
        yield
    finally:
        lock.unlink()


def run_update(data_dir, operation, as_of=None):
    """On failure retain validated data and explicitly publish the failed attempt."""
    attempt = {"attempted_at_utc": now_utc(), "source_url": SOURCE_URL}
    with update_lock(data_dir):
        try:
            files = operation()
            results = [store_observation(data_dir, blob, metadata) for blob, metadata in files]
            attempt.update(status="UNCHANGED" if all(r[2] for r in results) else "OK",
                           imported_reports=len(results), observations=[{"date": r[0], "sha256": r[1]} for r in results])
            return publish(data_dir, attempt, as_of), 0
        except (ReportError, OSError, ValueError, KeyError, ImportError) as exc:
            attempt.update(status="FAILED", error=str(exc))
            try:
                latest = publish(data_dir, attempt, as_of)
            except (ReportError, OSError, ValueError, KeyError, ImportError) as archive_exc:
                # An archive failure must not leave a consumer believing all is well.
                attempt["error"] += f"; archive validation failed: {archive_exc}"
                latest = publish_unavailable(data_dir, attempt)
            return latest, 1


def main(argv=None):
    parser = argparse.ArgumentParser(description="COMEX-Gold-Tracker: official CME stocks, reconciled and archived")
    parser.add_argument("--data-dir", type=Path, default=Path(__file__).resolve().parents[1] / "data")
    parser.add_argument("--as-of", type=date.fromisoformat, help="ISO local date for replay/status; does not change report dates")
    subs = parser.add_subparsers(dest="command", required=True)
    update = subs.add_parser("update", help="Download current official CME XLS and refresh outputs")
    update.add_argument("--timeout", type=int, default=20)
    update.add_argument("--attempts", type=int, choices=range(1, 4), default=2)
    imp = subs.add_parser("import", help="Import downloaded official reports without network")
    imp.add_argument("files", type=Path, nargs="+")
    imp.add_argument("--method", choices=["local_import_origin_unverified", "official_browser_download"], default="local_import_origin_unverified")
    subs.add_parser("status", help="Recheck archives and refresh current freshness/validation status")
    args = parser.parse_args(argv)
    if args.command == "update" and args.timeout <= 0:
        parser.error("timeout must be positive")
    try:
        if args.command == "status":
            with update_lock(args.data_dir):
                try:
                    latest = publish(args.data_dir, as_of=args.as_of)
                except (ReportError, OSError, ValueError, KeyError, ImportError) as exc:
                    latest = publish_unavailable(args.data_dir, {
                        "attempted_at_utc": now_utc(), "source_url": SOURCE_URL,
                        "status": "FAILED", "error": "Archive validation failed: " + str(exc)})
            code = 0 if latest["available"] and latest["freshness"] != "STALE" and latest["update_status"] != "FAILED" else 2
        else:
            if args.command == "update":
                operation = lambda: [fetch_report(args.timeout, args.attempts)]
            else:
                operation = lambda: [(p.read_bytes(), {"method": args.method, "import_filename": p.name,
                                                       "http_status": None,
                                                       "origin_note": "Browser source declared by caller" if args.method == "official_browser_download" else "Local file origin not independently verified"}) for p in args.files]
            latest, code = run_update(args.data_dir, operation, args.as_of)
        print(json.dumps({k: latest.get(k) for k in ("available", "date", "report_date", "total_oz", "registered_oz",
                          "eligible_oz", "registered_ratio", "change_1d_pct", "status", "freshness", "update_status")}, ensure_ascii=False, indent=2))
        if code:
            print(latest.get("last_update", {}).get("error", "Unavailable or stale data; inspect latest.json"), file=sys.stderr)
        return code
    except (ReportError, OSError, ValueError, KeyError, ImportError) as exc:
        print(str(exc), file=sys.stderr)
        return 1


if __name__ == "__main__":
    sys.exit(main())
