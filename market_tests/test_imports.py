"""Historical snapshots cannot silently become authoritative observations or executable markup."""
import json
import tempfile
import unittest
from pathlib import Path
from market_reports.imports import FIELDS, import_csv, load_imports, parse_csv, publish_imports
from market_reports.render import page

SAMPLE = ','.join(FIELDS) + '\n0,2026-10-12,1.3,,15.21,69,15.067141026\n1,2026-10-13,1.3,,15.27,57,15.050647563\n'


class HistoricalImportTests(unittest.TestCase):
    def test_missing_remains_null_and_units_and_snapshot_meaning_are_preserved(self):
        with tempfile.TemporaryDirectory() as tmp:
            bundle = import_csv(SAMPLE, tmp, 'old.csv')
            self.assertIsNone(bundle['rows'][0]['values']['cnn_fg'])
            self.assertEqual(bundle['rows'][0]['values']['comex_registered'], '15.067141026')
            self.assertIn('not_individual_observation', bundle['date_semantics'])
            self.assertEqual(bundle['verification_status'], 'LEGACY_NOT_REVERIFIED')

    def test_reimport_with_normalized_line_endings_is_idempotent(self):
        with tempfile.TemporaryDirectory() as tmp:
            one = import_csv(SAMPLE, tmp, 'old.csv')
            path = Path(tmp) / 'imports' / (one['import_id'] + '.json')
            before = path.read_bytes()
            self.assertEqual(import_csv('\ufeff' + SAMPLE.replace('\n', '\r\n'), tmp, 'old.csv'), one)
            self.assertEqual(path.read_bytes(), before)
            self.assertEqual(len(load_imports(tmp)), 1)

    def test_unsupported_columns_are_rejected_instead_of_publishing_other_private_data(self):
        with self.assertRaises(ValueError):
            parse_csv(SAMPLE.replace('index,', 'account,index,', 1))

    def test_duplicate_dates_are_rejected_instead_of_double_counting(self):
        with self.assertRaises(ValueError):
            parse_csv(SAMPLE.replace('2026-10-13', '2026-10-12'))

    def test_formula_markup_nonfinite_and_out_of_range_cells_are_rejected(self):
        for cell in ['=1+1', '<script>alert(1)</script>', 'NaN', 'Infinity', '-1']:
            with self.subTest(cell=cell), self.assertRaises(ValueError):
                parse_csv(SAMPLE.replace('15.21', cell))
        with self.assertRaises(ValueError):
            parse_csv(SAMPLE.replace(',69,', ',101,'))
        with self.assertRaises(ValueError):
            parse_csv(SAMPLE.replace('0,2026-', '=1+1,2026-', 1))

    def test_corrupted_derived_rows_cannot_be_published_with_valid_source_hash(self):
        with tempfile.TemporaryDirectory() as tmp:
            bundle = import_csv(SAMPLE, tmp, 'old.csv')
            path = Path(tmp) / 'imports' / (bundle['import_id'] + '.json')
            bundle['rows'][0]['values']['vix'] = '99'
            path.write_text(json.dumps(bundle))
            with self.assertRaises(ValueError):
                publish_imports(tmp, Path(tmp) / 'site', page)

    def test_conflicting_source_label_preserves_existing_immutable_import(self):
        with tempfile.TemporaryDirectory() as tmp:
            import_csv(SAMPLE, tmp, 'old.csv')
            with self.assertRaises(ValueError):
                import_csv(SAMPLE, tmp, 'changed.csv')

    def test_publication_preserves_authoritative_history_and_gold_and_escapes_labels(self):
        with tempfile.TemporaryDirectory() as tmp:
            data = Path(tmp) / 'data'; data.mkdir()
            history = data / 'history.csv'; history.write_text('official history sentinel')
            target = Path(tmp) / 'site'; target.mkdir()
            gold = target / 'latest.json'; gold.write_text('Gold sentinel')
            bundle = import_csv(SAMPLE, data, '<script>.csv')
            links = publish_imports(data, target, page)
            folder = target / 'imports' / bundle['import_id']
            rendered = (folder / 'index.html').read_text()
            self.assertIn('&lt;script&gt;.csv', rendered)
            self.assertNotIn('<script>.csv', rendered)
            self.assertIn('缺失', rendered)
            self.assertIn('M oz', rendered)
            self.assertIn('#snapshot-2026-10-12', links)
            self.assertEqual((folder / 'data.csv').read_text(), SAMPLE)
            self.assertEqual(history.read_text(), 'official history sentinel')
            self.assertEqual(gold.read_text(), 'Gold sentinel')
            self.assertEqual(json.loads((target / 'imports/index.json').read_text())['imports'][0]['row_count'], 2)

    def test_empty_or_bad_date_export_is_rejected(self):
        for content in [','.join(FIELDS) + '\n', SAMPLE.replace('2026-10-12', '2026-02-30')]:
            with self.assertRaises(ValueError):
                parse_csv(content)
