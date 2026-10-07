from datetime import datetime, timedelta, timezone
import hashlib
import json
from pathlib import Path
import tempfile
import unittest

from comex_gold.__main__ import publish_unavailable, run_update
from comex_gold.cloud import consumer_health, export_public
from comex_gold.parser import ReportError
from tests.test_tracker import FIXTURE, LOCAL_METHOD


class CloudTests(unittest.TestCase):
    def test_export_only_public_outputs_and_matching_raw(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            data, out = root / "data", root / "public"
            run_update(data, lambda: [(FIXTURE.read_bytes(), LOCAL_METHOD)])
            (data / "secret.txt").write_text("DO NOT PUBLISH")
            export_public(data, out)
            self.assertFalse((out / "secret.txt").exists())
            latest = json.loads((out / "latest.json").read_text(encoding="utf-8"))
            self.assertEqual(hashlib.sha256((out / latest["provenance"]["raw_path"]).read_bytes()).hexdigest(),
                             latest["provenance"]["sha256"])
            manifest = json.loads((out / "manifest.json").read_text())
            self.assertEqual(manifest["sha256"]["latest.json"], hashlib.sha256((out / "latest.json").read_bytes()).hexdigest())
            self.assertIn("23,479,618.522", (out / "index.html").read_text(encoding="utf-8"))

    def test_failure_snapshot_does_not_publish_invalid_history(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            data = root / "data"
            run_update(data, lambda: [(FIXTURE.read_bytes(), LOCAL_METHOD)])
            publish_unavailable(data, {"status": "FAILED", "error": "corrupt archive"})
            export_public(data, root / "out")
            self.assertFalse((root / "out" / "history.csv").exists())
            self.assertFalse((root / "out" / "raw").exists())
            self.assertFalse(json.loads((root / "out" / "latest.json").read_text())["available"])

    def test_corrupt_archive_cannot_export_success_snapshot(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            run_update(root / "data", lambda: [(FIXTURE.read_bytes(), LOCAL_METHOD)])
            next((root / "data" / "raw").rglob("*.xls")).write_bytes(b"corrupt")
            with self.assertRaises(ReportError):
                export_public(root / "data", root / "out")

    def test_stale_static_success_expires_at_read_time(self):
        now = datetime.now(timezone.utc)
        latest = {"available": True, "update_status": "OK", "freshness": "WITHIN_AGE_LIMIT",
                  "last_update": {"attempted_at_utc": now.isoformat()}}
        self.assertEqual(consumer_health(latest, now), "RECENT_SUCCESS_SNAPSHOT")
        self.assertEqual(consumer_health(latest, now + timedelta(hours=27)), "SCHEDULER_OVERDUE")
        latest["update_status"] = "FAILED"
        self.assertEqual(consumer_health(latest, now), "UPDATE_FAILED_OR_UNCONFIRMED")
        latest["last_update"]["attempted_at_utc"] = now.replace(tzinfo=None).isoformat()
        self.assertEqual(consumer_health(latest, now), "UNCONFIRMED_UPDATE_TIME")

    def test_nonempty_export_rejected(self):
        with tempfile.TemporaryDirectory() as tmp:
            out = Path(tmp) / "out"
            out.mkdir()
            (out / "leak.txt").write_text("old")
            with self.assertRaises(ReportError):
                export_public(Path(tmp) / "data", out)
