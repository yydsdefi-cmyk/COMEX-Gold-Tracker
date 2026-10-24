"""Independent arithmetic failures and bounded Pages without deleting source history."""
import contextlib
import copy
import hashlib
import io
import json
import tempfile
import unittest
from datetime import datetime
from pathlib import Path
from market_reports.audit import audit_payload
from market_reports.core import UTC
from market_reports.trends import weekly_changes
from market_reports.__main__ import run,validate_archive
from market_reports.render import publish
from market_reports.sources import registry
from .test_market import receipt
from .test_calendar_trends import point,capture,NOW


class IndependentAuditTests(unittest.TestCase):
    def sample(self):
        c=capture([point('sp500',100,'2026-10-16'),point('sp500',110,'2026-10-23'),
                   point('us10y',4,'2026-10-16'),point('us10y',4.1,'2026-10-23'),
                   point('vix',20,'2026-10-16'),point('vix3m',25,'2026-10-16'),
                   point('vix',30,'2026-10-23'),point('vix3m',20,'2026-10-23')])
        p={'kind':'weekly','intended_local_date':'2026-10-24','capture_id':'a'*64,
           'analysis':{'weekly_comparisons':weekly_changes(c,[])}}
        return p,[c]

    def test_calculable_only_pass_does_not_claim_missing_indicators_pass(self):
        p,c=self.sample();r=audit_payload(p,c)
        self.assertEqual(r['status'],'PASS_CALCULABLE_ONLY');self.assertEqual(r['verified'],5)
        self.assertEqual(r['not_calculable'],11);self.assertEqual(r['failed'],0)

    def test_wrong_numeric_result_fails_independent_decimal_audit(self):
        p,c=self.sample();p['analysis']['weekly_comparisons'][0]['change']=99
        r=audit_payload(p,c);self.assertEqual(r['status'],'FAIL');self.assertEqual(r['failed'],1)

    def test_fabricated_provenance_cannot_pass_with_correct_numeric_result(self):
        p,c=self.sample();p['analysis']['weekly_comparisons'][0]['baseline']['response_sha256']='b'*64
        r=audit_payload(p,c);self.assertEqual(r['status'],'FAIL')
        self.assertIn('archived source',r['checks'][0]['error'])

    def test_mismatched_ratio_input_dates_rejected_independently(self):
        p,c=self.sample();r=next(x for x in p['analysis']['weekly_comparisons'] if x['metric']=='vix_ratio')
        r['end']['inputs'][0]['observation_date']='2026-10-22'
        self.assertEqual(audit_payload(p,c)['status'],'FAIL')

    def test_no_structured_or_calculable_data_returns_blocked(self):
        self.assertEqual(audit_payload({},[])['status'],'BLOCKED')
        p={'intended_local_date':'2026-10-24','capture_id':'x','analysis':{'weekly_comparisons':weekly_changes(capture([]),[])}}
        r=audit_payload(p,[]);self.assertEqual(r['status'],'BLOCKED');self.assertEqual(r['verified'],0)

    def test_display_scale_and_units_are_independently_checked(self):
        for field,value in [('scale',2),('unit','USD')]:
            p,c=self.sample();p['analysis']['weekly_comparisons'][0][field]=value
            self.assertEqual(audit_payload(p,c)['status'],'FAIL')

    def test_week_fragment_cannot_be_relabelled_as_complete_week(self):
        c=capture([point('sp500',100,'2026-10-21'),point('sp500',110,'2026-10-23')])
        p={'intended_local_date':'2026-10-24','capture_id':'x','analysis':{'weekly_comparisons':weekly_changes(c,[])}}
        p['analysis']['weekly_comparisons'][0]['status']='OK'
        r=audit_payload(p,[c]);self.assertEqual(r['status'],'FAIL')


class PagesRetentionTests(unittest.TestCase):
    def generate(self,data,at,kinds):
        def empty(now):
            return [dict(receipt(s['id'],status='MISSING'),fetched_at_utc=now.isoformat()) for s in registry(now)]
        with contextlib.redirect_stdout(io.StringIO()):
            run(kinds,data,at,empty,lambda now:dict(receipt('comex',status='MISSING'),fetched_at_utc=now.isoformat()))

    def test_publication_prunes_only_old_rendered_pages_preserving_all_source_bytes(self):
        with tempfile.TemporaryDirectory() as t:
            data=Path(t)/'data';site=Path(t)/'site';site.mkdir();(site/'latest.json').write_text('Gold sentinel')
            self.generate(data,datetime(2026,1,1,3,tzinfo=UTC),['daily'])
            publish(data,site);old_page=site/'market/archive/daily/2026-01-01/index.html';self.assertTrue(old_page.exists())
            self.generate(data,NOW,['daily','weekly'])
            authority={p:hashlib.sha256(p.read_bytes()).hexdigest() for p in data.rglob('*') if p.is_file()}
            publish(data,site);self.assertFalse(old_page.exists())
            index=(site/'market/index.html').read_text();self.assertIn('2026-01-01',index);self.assertIn('/blob/main/market_data/reports/daily/2026-01-01/',index)
            self.assertEqual((site/'latest.json').read_text(),'Gold sentinel')
            for p,h in authority.items():self.assertEqual(hashlib.sha256(p.read_bytes()).hexdigest(),h)
            validate_archive(data)

    def test_latest_weekly_kept_even_when_older_than_retention_window(self):
        with tempfile.TemporaryDirectory() as t:
            data=Path(t)/'data';site=Path(t)/'site'
            self.generate(data,datetime(2026,1,1,3,tzinfo=UTC),['weekly'])
            self.generate(data,NOW,['daily']);publish(data,site)
            self.assertIn('2026-01-01',(site/'market/weekly.html').read_text())
            self.assertTrue((site/'market/archive/weekly/2026-01-01/index.html').exists())
            self.assertIn('data-kind="weekly"',(site/'market/index.html').read_text())
