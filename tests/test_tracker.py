"""Real CME fixture + synthetic regressions; synthetic days are NOT CME validation."""
from copy import deepcopy
from datetime import date, timedelta
from io import BytesIO
import csv
import json
from pathlib import Path
import tempfile
import unittest
from unittest.mock import patch, MagicMock
from urllib.error import HTTPError, URLError

import openpyxl

from comex_gold.__main__ import main, run_update, update_lock
from comex_gold.collector import fetch_report, OfficialRedirects
from comex_gold.dataset import (load_observations, make_latest, publish, store_observation,
                                validation_report, window_change, inventory_alert)
from comex_gold.parser import ReportError, milli_oz, parse_report, parse_rows, read_workbook

FIXTURE = Path(__file__).resolve().parent / "fixtures" / "Gold_Stocks_report_2026-10-06.xls"
LOCAL_METHOD = {"method": "local_import_origin_unverified"}


def synthetic_rows(activity="2026-09-01", previous_reg=100, previous_elig=200, reg=100, elig=200,
                   received=0, withdrawn=0, pledged=10):
    activity_date = date.fromisoformat(activity)
    report_date = activity_date + timedelta(days=1)
    def category(label, previous, today, r=0, w=0):
        return [label, previous, r, w, r - w, today - previous - r + w, today]
    return [["COMMODITY EXCHANGE, INC."], ["METAL DEPOSITORY STATISTICS"],
            ["GOLD", "Report Date: " + report_date.strftime("%m/%d/%Y")],
            ["Troy Ounce", "Activity Date: " + activity_date.strftime("%m/%d/%Y")],
            ["DEPOSITORY", "PREV TOTAL", "RECEIVED", "WITHDRAWN", "NET CHANGE", "ADJUSTMENT", "TOTAL TODAY"],
            ["SYNTHETIC TEST VAULT"],
            category("Registered", previous_reg, reg),
            ["Pledged", pledged, "", "", "", "", pledged],
            category("Eligible", previous_elig, elig, received, withdrawn),
            category("Total", previous_reg + previous_elig, reg + elig, received, withdrawn),
            category("TOTAL REGISTERED", previous_reg, reg),
            ["TOTAL PLEDGED", pledged, "", "", "", "", pledged],
            category("TOTAL ELIGIBLE", previous_elig, elig, received, withdrawn),
            category("COMBINED TOTAL", previous_reg + previous_elig, reg + elig, received, withdrawn)]


def workbook_bytes(rows):
    book = openpyxl.Workbook()
    for row in rows:
        book.active.append(row)
    stream = BytesIO()
    book.save(stream)
    book.close()
    return stream.getvalue()


def observation_sequence(count=21):
    out = []
    d = date(2026, 8, 3)
    previous_reg = 100
    while len(out) < count:
        if d.weekday() < 5:
            reg = previous_reg - 1
            o = parse_rows(synthetic_rows(d.isoformat(), previous_reg=previous_reg, reg=reg))
            o["provenance"] = {"method": "SYNTHETIC_TEST", "source_url": "test-only",
                               "sha256": "test-only", "captured_at_utc": "2026-09-01T00:00:00+00:00", "raw_path": "test-only"}
            out.append(o)
            previous_reg = reg
        d += timedelta(days=1)
    return out


class ParserTests(unittest.TestCase):
    def test_actual_official_xls_exact_values_and_detail(self):
        p = parse_report(FIXTURE.read_bytes())
        self.assertEqual(p["date"], "2026-10-05")
        self.assertEqual(p["report_date"], "2026-10-06")
        self.assertEqual(p["summary"]["registered"]["balances"]["today"], 15086528079)
        self.assertEqual(p["summary"]["eligible"]["balances"]["today"], 8393090443)
        self.assertEqual(p["summary"]["total"]["balances"]["today"], 23479618522)
        self.assertEqual(p["summary"]["pledged"]["balances"]["today"], 1721684952)
        self.assertEqual(len(p["depositories"]), 11)
        self.assertEqual(p["summary"]["total"]["row"], 80)

    def test_xlsx_signature_not_extension(self):
        p = parse_report(workbook_bytes(synthetic_rows()))
        self.assertEqual(p["file_type"], "xlsx")
        self.assertEqual(p["summary"]["total"]["balances"]["today"], 300000)

    def test_pledged_never_double_counted(self):
        p = parse_rows(synthetic_rows())
        self.assertEqual(p["summary"]["total"]["balances"]["today"], 300000)

    def test_pledged_cannot_exceed_registered(self):
        with self.assertRaises(ReportError):
            parse_rows(synthetic_rows(pledged=101))

    def test_adjustment_is_separate_from_physical_movement(self):
        p = parse_rows(synthetic_rows(reg=90, elig=230, received=30, withdrawn=10))
        self.assertEqual(p["summary"]["total"]["balances"]["net_change"], 20000)
        self.assertEqual(p["summary"]["registered"]["balances"]["adjustment"], -10000)
        self.assertEqual(p["summary"]["eligible"]["balances"]["adjustment"], 10000)

    def test_header_columns_can_move(self):
        rows = synthetic_rows()
        for row in rows:
            row.insert(1, "")
        self.assertEqual(parse_rows(rows)["summary"]["total"]["balances"]["today"], 300000)

    def test_duplicate_summary_rejected(self):
        rows = synthetic_rows()
        rows.append(rows[-1])
        with self.assertRaises(ReportError):
            parse_rows(rows)

    def test_incomplete_warehouse_rejected(self):
        rows = synthetic_rows()
        del rows[8]
        with self.assertRaises(ReportError):
            parse_rows(rows)

    def test_corrupt_summary_rejected(self):
        rows = synthetic_rows()
        rows[-1][-1] += 1
        with self.assertRaises(ReportError):
            parse_rows(rows)

    def test_balanced_but_wrong_summary_rejected_against_warehouses(self):
        rows = synthetic_rows(reg=90, elig=210)
        rows[10] = ["TOTAL REGISTERED", 100, 0, 0, 0, 0, 100]
        rows[12] = ["TOTAL ELIGIBLE", 200, 0, 0, 0, 0, 200]
        with self.assertRaises(ReportError):
            parse_rows(rows)

    def test_blank_is_not_zero(self):
        rows = synthetic_rows()
        rows[6][2] = ""
        with self.assertRaises(ReportError):
            parse_rows(rows)

    def test_html_response_rejected(self):
        with self.assertRaises(ReportError):
            parse_report(b"<html>Access denied</html>")

    def test_other_metal_units_and_dates_rejected(self):
        for value, row, column in [("SILVER", 2, 0), ("Kilograms", 3, 0), ("Activity Date: 12/31/2026", 3, 1)]:
            rows = synthetic_rows()
            rows[row][column] = value
            with self.assertRaises(ReportError):
                parse_rows(rows)

    def test_millioz_precision_and_invalid_values(self):
        self.assertEqual(milli_oz(15086528.079000002), 15086528079)
        self.assertEqual(milli_oz("(1,200.125)"), -1200125)
        for value in ["", None, True, "NaN", "Infinity", "0.0005"]:
            with self.assertRaises(ReportError):
                milli_oz(value)


class DatasetTests(unittest.TestCase):
    def test_single_report_has_1d_but_not_fabricated_history(self):
        observations = observation_sequence(1)
        latest = make_latest(observations, {"status": "OK"}, date(2026, 8, 5))
        self.assertEqual(latest["registered_change_1d_oz"], -1.0)
        self.assertIsNone(latest["change_5d_pct"])
        self.assertIsNone(latest["change_windows"]["1d"]["baseline_date"])

    def test_20d_needs_21_reports_and_exact_known_changes(self):
        observations = observation_sequence(21)
        latest = make_latest(observations, {"status": "OK"})
        self.assertEqual(latest["registered_change_20d_oz"], -20.0)
        self.assertEqual(latest["change_20d_oz"], -20.0)
        self.assertEqual(latest["eligible_change_20d_oz"], 0.0)
        self.assertEqual(latest["registered_change_5d_oz"], -5.0)
        self.assertTrue(latest["registered_alert"]["persistent_decline_5_consecutive_days"])
        self.assertIsNone(make_latest(observations[:20], {"status": "OK"})["change_20d_pct"])

    def test_gap_never_treated_as_consecutive_trading_days(self):
        observations = observation_sequence(22)
        del observations[-3]
        result, reason = window_change(observations, 20)
        self.assertIsNone(result)
        self.assertEqual(reason, "MISSING_WEEKDAY_OR_UNCONFIRMED_HOLIDAY")

    def test_cross_report_balance_revision_suppresses_window(self):
        observations = observation_sequence(21)
        observations[-1]["summary"]["registered"]["balances"]["previous"] += 1000
        result, reason = window_change(observations, 20)
        self.assertIsNone(result)
        self.assertEqual(reason, "PREVIOUS_BALANCE_MISMATCH_OR_REVISION")

    def test_thresholds_use_unrounded_percent_and_strict_less_than(self):
        for today, level in [(1000, "NORMAL"), (990, "NORMAL"), (989, "YELLOW"),
                             (970, "YELLOW"), (969, "ORANGE"), (950, "ORANGE"), (949, "RED")]:
            self.assertEqual(inventory_alert(today, 1000), level)
        self.assertEqual(inventory_alert(0, 0), "UNKNOWN")

    def test_zero_denominator_and_unavailable_are_not_normal(self):
        observations = observation_sequence(1)
        for item in observations[0]["summary"].values():
            item["balances"]["previous"] = 0
        latest = make_latest(observations, {"status": "OK"})
        self.assertIsNone(latest["change_1d_pct"])
        self.assertEqual(latest["status"], "UNKNOWN")
        latest = make_latest([], {"status": "FAILED"})
        self.assertFalse(latest["available"])
        self.assertIsNone(latest["total_oz"])

    def test_stale_snapshot_explicit(self):
        latest = make_latest(observation_sequence(1), {"status": "OK"}, date(2026, 10, 7))
        self.assertEqual(latest["freshness"], "STALE")
        self.assertEqual(latest["date"], "2026-08-03")

    def test_idempotent_archival_csv_and_provenance(self):
        with tempfile.TemporaryDirectory() as temp:
            folder = Path(temp)
            blob = FIXTURE.read_bytes()
            self.assertFalse(store_observation(folder, blob, LOCAL_METHOD)[2])
            self.assertTrue(store_observation(folder, blob, LOCAL_METHOD)[2])
            self.assertEqual(len(list((folder / "raw").rglob("*.xls"))), 1)
            self.assertEqual(len(load_observations(folder)), 1)
            latest = publish(folder, {"status": "OK"}, date(2026, 10, 7))
            self.assertEqual(latest["total_oz"], 23479618.522)
            self.assertEqual(len((folder / "history.csv").read_text().splitlines()), 2)
            self.assertEqual(json.loads((folder / "validation.json").read_text())["verified_report_count"], 1)

    def test_official_http_capture_strengthens_manual_provenance(self):
        with tempfile.TemporaryDirectory() as temp:
            folder = Path(temp)
            blob = FIXTURE.read_bytes()
            store_observation(folder, blob, LOCAL_METHOD)
            store_observation(folder, blob, {"method": "official_https_download", "http_status": 200})
            self.assertEqual(load_observations(folder)[0]["provenance"]["method"], "official_https_download")
            self.assertEqual(len(list((folder / "captures").glob("*.json"))), 2)

    def test_failed_download_retains_last_good_with_failure_marker(self):
        with tempfile.TemporaryDirectory() as temp:
            folder = Path(temp)
            run_update(folder, lambda: [(FIXTURE.read_bytes(), LOCAL_METHOD)])
            def failed():
                raise ReportError("HTTP 403")
            latest, code = run_update(folder, failed)
            self.assertEqual(code, 1)
            self.assertTrue(latest["available"])
            self.assertEqual(latest["total_oz"], 23479618.522)
            self.assertEqual(latest["update_status"], "FAILED")
            self.assertIn("上次核验数据", (folder / "daily_brief.md").read_text(encoding="utf-8"))

    def test_same_date_revision_retains_both_sources(self):
        with tempfile.TemporaryDirectory() as temp:
            folder = Path(temp)
            store_observation(folder, workbook_bytes(synthetic_rows(reg=90)), LOCAL_METHOD)
            store_observation(folder, workbook_bytes(synthetic_rows(reg=80)), LOCAL_METHOD)
            observations = load_observations(folder)
            self.assertEqual(len(observations), 1)
            self.assertEqual(observations[0]["summary"]["registered"]["balances"]["today"], 80000)
            self.assertEqual(len(list((folder / "raw").rglob("*.xlsx"))), 2)

    def test_tampered_raw_fails_closed(self):
        with tempfile.TemporaryDirectory() as temp:
            folder = Path(temp)
            run_update(folder, lambda: [(FIXTURE.read_bytes(), LOCAL_METHOD)])
            next((folder / "raw").rglob("*.xls")).write_bytes(b"tampered")
            latest, code = run_update(folder, lambda: [(b"bad", LOCAL_METHOD)])
            self.assertEqual(code, 1)
            self.assertFalse(latest["available"])
            self.assertIsNone(latest["total_oz"])

    def test_update_lock_prevents_parallel_writes(self):
        with tempfile.TemporaryDirectory() as temp:
            with update_lock(Path(temp)):
                with self.assertRaises(ReportError):
                    with update_lock(Path(temp)):
                        pass

    def test_status_check_corruption_publishes_unavailable(self):
        with tempfile.TemporaryDirectory() as temp:
            folder = Path(temp)
            run_update(folder, lambda: [(FIXTURE.read_bytes(), LOCAL_METHOD)])
            next((folder / "raw").rglob("*.xls")).write_bytes(b"tampered")
            with patch("builtins.print"):
                code = main(["--data-dir", str(folder), "status"])
            self.assertEqual(code, 2)
            self.assertFalse(json.loads((folder / "latest.json").read_text())["available"])

    def test_validation_lists_missing_candidates(self):
        result = validation_report(observation_sequence(1))
        self.assertEqual(result["status"], "INCOMPLETE")
        self.assertEqual(result["verified_report_count"], 1)
        self.assertEqual(len(result["not_obtained_dates"]), 19)

    def test_old_balance_break_is_disclosed_without_poisoning_valid_five_day_window(self):
        observations = observation_sequence(21)
        observations[1]["summary"]["eligible"]["balances"]["previous"] -= 1000
        latest = make_latest(observations, {"status": "OK"}, date(2026, 9, 1))
        self.assertIsNone(latest["change_20d_pct"])
        self.assertEqual(latest["change_windows"]["20d"]["status"], "PREVIOUS_BALANCE_MISMATCH_OR_REVISION")
        self.assertIsNotNone(latest["change_5d_pct"])
        self.assertIsNotNone(latest["change_10d_pct"])
        self.assertEqual(latest["change_1d_pct"], -0.357143)
        self.assertEqual(latest["history_continuity_issues"][0]["series"]["eligible"],
                         {"prior_total_today_oz": 200.0, "next_prev_total_oz": 199.0})

    def test_ten_day_change_requires_eleven_observations_and_preserves_baseline(self):
        ten = make_latest(observation_sequence(10), {"status": "OK"}, date(2026, 9, 1))
        self.assertIsNone(ten["change_10d_pct"])
        self.assertEqual(ten["change_windows"]["10d"]["status"], "INSUFFICIENT_HISTORY")
        eleven = make_latest(observation_sequence(11), {"status": "OK"}, date(2026, 9, 1))
        self.assertEqual(eleven["change_windows"]["10d"]["baseline_date"], "2026-08-03")
        self.assertEqual(eleven["change_10d_oz"], -10.0)
        self.assertEqual(eleven["registered_change_10d_oz"], -10.0)
        self.assertEqual(eleven["eligible_change_10d_pct"], 0.0)
        self.assertIsNone(eleven["change_20d_pct"])

    def test_archived_cme_provenance_survives_csv_and_validation_export(self):
        with tempfile.TemporaryDirectory() as temp:
            folder = Path(temp)
            archive = {"method": "internet_archive_original_cme", "archive_url": "https://web.archive.org/web/test-only",
                       "archive_timestamp_utc": "20261007081907", "cdx_sha1_base32": "TEST_ONLY", "cdx_digest_verified": True}
            store_observation(folder, FIXTURE.read_bytes(), archive)
            publish(folder, {"status": "OK"}, date(2026, 10, 7))
            row = next(csv.DictReader((folder / "history.csv").read_text(encoding="utf-8").splitlines()))
            self.assertEqual(row["provenance_method"], "internet_archive_original_cme")
            self.assertEqual(row["archive_url"], archive["archive_url"])
            self.assertEqual(row["cdx_digest_verified"], "True")
            verified = json.loads((folder / "validation.json").read_text())["verified"][0]
            self.assertEqual(verified["archive_url"], archive["archive_url"])


class CollectorTests(unittest.TestCase):
    def test_403_stops_without_retry_or_cookie_workaround(self):
        opener = MagicMock()
        opener.open.side_effect = HTTPError("https://www.cmegroup.com", 403, "Forbidden", {}, None)
        with patch("comex_gold.collector.build_opener", return_value=opener):
            with self.assertRaises(ReportError):
                fetch_report(attempts=3)
        self.assertEqual(opener.open.call_count, 1)

    def test_transient_network_failure_has_bounded_retry(self):
        opener = MagicMock()
        opener.open.side_effect = URLError("timeout")
        with patch("comex_gold.collector.build_opener", return_value=opener), patch("comex_gold.collector.time.sleep"):
            with self.assertRaises(ReportError):
                fetch_report(attempts=2)
        self.assertEqual(opener.open.call_count, 2)

    def test_redirect_outside_cme_is_rejected(self):
        with self.assertRaises(ReportError):
            OfficialRedirects().redirect_request(None, None, 302, "", {}, "https://example.com/fake.xls")


if __name__ == "__main__":
    unittest.main()
