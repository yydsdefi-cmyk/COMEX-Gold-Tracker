"""Scheduled COMEX retry guard.

A scheduled run skips downloading only when today's snapshot is already a
validated, successful collection made at/after 05:00 Asia/Kuala_Lumpur.
Manual dispatches and code pushes intentionally bypass this guard.
"""
import argparse
import json
from datetime import datetime, time, timedelta, timezone
from pathlib import Path
from zoneinfo import ZoneInfo

MYT = ZoneInfo("Asia/Kuala_Lumpur")
MIN_VALID_LOCAL_TIME = time(5, 0)


def snapshot_is_fresh(latest, now=None):
    """Return (fresh, reason); never infer freshness from generated_at_utc."""
    now = now or datetime.now(timezone.utc)
    attempt = latest.get("last_update") or {}
    stamp = attempt.get("attempted_at_utc")
    try:
        attempted = datetime.fromisoformat(stamp.replace("Z", "+00:00"))
        if attempted.tzinfo is None:
            return False, "attempted_at_utc has no timezone"
        attempted = attempted.astimezone(timezone.utc)
    except (AttributeError, TypeError, ValueError):
        return False, "attempted_at_utc is missing or invalid"

    age = now.astimezone(timezone.utc) - attempted
    if age < -timedelta(minutes=5):
        return False, "attempted_at_utc is in the future"
    if age > timedelta(hours=26):
        return False, "snapshot is older than 26 hours"
    local_attempt = attempted.astimezone(MYT)
    local_now = now.astimezone(MYT)
    if local_attempt.date() != local_now.date():
        return False, "no successful collection attempt for today's MYT date"
    if local_attempt.time().replace(tzinfo=None) < MIN_VALID_LOCAL_TIME:
        return False, "today's collection attempt was before 05:00 MYT"
    if latest.get("available") is not True:
        return False, "latest snapshot is unavailable"
    if latest.get("update_status") not in ("OK", "UNCHANGED"):
        return False, "latest update status is not successful"
    if latest.get("freshness") == "STALE":
        return False, "official report is marked STALE"
    return True, "today's snapshot is already valid"


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--data-dir", type=Path, default=Path("data"))
    args = parser.parse_args(argv)
    try:
        latest = json.loads((args.data_dir / "latest.json").read_text(encoding="utf-8"))
    except (OSError, ValueError):
        fresh, reason = False, "latest.json is missing or invalid"
    else:
        fresh, reason = snapshot_is_fresh(latest)
    print(json.dumps({"collect": not fresh, "reason": reason}, ensure_ascii=False))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
