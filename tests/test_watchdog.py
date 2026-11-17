import unittest
from datetime import datetime, timezone

from comex_gold.watchdog import snapshot_is_fresh


class WatchdogTests(unittest.TestCase):
    def setUp(self):
        self.now = datetime(2026, 11, 17, 4, 30, tzinfo=timezone.utc)  # 12:30 MYT
        self.latest = {
            "available": True,
            "update_status": "OK",
            "freshness": "WITHIN_AGE_LIMIT",
            "last_update": {"attempted_at_utc": "2026-11-17T03:00:00+00:00"},
        }

    def test_valid_today_snapshot_skips_duplicate_collection(self):
        fresh, _ = snapshot_is_fresh(self.latest, self.now)
        self.assertTrue(fresh)

    def test_previous_local_day_triggers_retry(self):
        self.latest["last_update"]["attempted_at_utc"] = "2026-11-16T15:30:00+00:00"
        fresh, _ = snapshot_is_fresh(self.latest, self.now)
        self.assertFalse(fresh)

    def test_attempt_before_five_myt_triggers_retry(self):
        self.latest["last_update"]["attempted_at_utc"] = "2026-11-16T20:59:00+00:00"
        fresh, _ = snapshot_is_fresh(self.latest, self.now)
        self.assertFalse(fresh)

    def test_failed_or_unavailable_snapshot_triggers_retry(self):
        for key, value in (("update_status", "FAILED"), ("available", False)):
            candidate = dict(self.latest)
            candidate[key] = value
            fresh, _ = snapshot_is_fresh(candidate, self.now)
            self.assertFalse(fresh)

    def test_stale_report_triggers_retry(self):
        self.latest["freshness"] = "STALE"
        fresh, _ = snapshot_is_fresh(self.latest, self.now)
        self.assertFalse(fresh)

    def test_missing_or_naive_timestamp_triggers_retry(self):
        for stamp in (None, "2026-11-17T03:00:00"):
            self.latest["last_update"]["attempted_at_utc"] = stamp
            fresh, _ = snapshot_is_fresh(self.latest, self.now)
            self.assertFalse(fresh)

    def test_latest_confirmation_flag_does_not_get_overwritten_or_used_as_success(self):
        self.latest["is_latest_confirmed"] = False
        fresh, _ = snapshot_is_fresh(self.latest, self.now)
        self.assertTrue(fresh)
        self.assertFalse(self.latest["is_latest_confirmed"])


if __name__ == "__main__":
    unittest.main()
