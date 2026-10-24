"""Adversarial archive linkage and independent report-period boundary checks."""
import contextlib
import copy
import io
import json
import shutil
import subprocess
import tempfile
import unittest
from datetime import datetime
from pathlib import Path

from market_reports.__main__ import run,validate_archive
from market_reports.core import UTC,encoded,digest,commit_bundle,due_reports
from market_reports.render import publish
from market_reports.schedule import expected_period,period_state,CLOCK_JS
from .test_market import NOW,fake_sources,fake_comex


class ArchiveLinkageTests(unittest.TestCase):
    def setUp(self):
        self.temp=tempfile.TemporaryDirectory();self.addCleanup(self.temp.cleanup)
        self.data=Path(self.temp.name)/'data'
        with contextlib.redirect_stdout(io.StringIO()):run(['daily','weekly'],self.data,NOW,fake_sources,fake_comex)
        self.pointer=self.data/'reports/daily/2026-10-24/latest.json'

    def payload(self):
        p=json.loads(self.pointer.read_text())
        return json.loads((self.pointer.parent/p['revision']/'report.json').read_text())

    def revision(self,payload,quality=None):
        commit_bundle(self.pointer.parent,{'report.md':'content','report.json':encoded(payload),
            'quality.json':encoded(payload['quality'] if quality is None else quality)})

    def test_csv_tampering_detected_without_mutating_archive(self):
        p=self.data/'history.csv';p.write_bytes(p.read_bytes().replace(b'51.0',b'99.0')+b'corrupt\n')
        before=p.read_bytes()
        with self.assertRaisesRegex(ValueError,'history CSV'):validate_archive(self.data)
        self.assertEqual(p.read_bytes(),before)

    def test_pointer_cannot_claim_different_capture_or_quality(self):
        original=json.loads(self.pointer.read_text())
        for key,value in [('capture_id','0'*64),('degraded',False),('generated_at_utc','2026-10-24T02:00:00+00:00')]:
            p={**original,key:value};self.pointer.write_bytes(encoded(p))
            with self.assertRaisesRegex(ValueError,'pointer/capture/quality'):validate_archive(self.data)
        self.pointer.write_bytes(encoded(original));validate_archive(self.data)

    def test_pointer_path_escape_rejected(self):
        p=json.loads(self.pointer.read_text());p['revision']='../../outside'
        self.pointer.write_bytes(encoded(p))
        with self.assertRaisesRegex(ValueError,'Invalid report pointer'):validate_archive(self.data)

    def test_renamed_content_addressed_revision_rejected(self):
        p=json.loads(self.pointer.read_text());(self.pointer.parent/p['revision']).rename(self.pointer.parent/('f'*20))
        with self.assertRaisesRegex(ValueError,'revision identity'):validate_archive(self.data)

    def test_embedded_capture_must_match_stored_capture(self):
        payload=self.payload();payload['capture']['observations'][0]['value']+=1
        self.revision(payload)
        with self.assertRaisesRegex(ValueError,'embedded capture/reference'):validate_archive(self.data)

    def test_report_cannot_reference_absent_capture(self):
        payload=self.payload();payload['capture_id']='0'*64;self.revision(payload)
        with self.assertRaisesRegex(ValueError,'embedded capture/reference'):validate_archive(self.data)

    def test_report_kind_and_period_bound_to_directory(self):
        payload=self.payload();payload['kind']='weekly';self.revision(payload)
        with self.assertRaisesRegex(ValueError,'directory/period'):validate_archive(self.data)

    def test_quality_file_and_receipts_cannot_diverge(self):
        payload=self.payload();quality=copy.deepcopy(payload['quality']);quality['missing_or_unverified']=[]
        self.revision(payload,quality)
        with self.assertRaisesRegex(ValueError,'quality/source'):validate_archive(self.data)

    def test_capture_cannot_omit_source_observations(self):
        payload=self.payload();capture=payload['capture'];capture['observations'].pop()
        raw=encoded(capture);(self.data/'captures'/(digest(raw)+'.json')).write_bytes(raw)
        with self.assertRaisesRegex(ValueError,'flattened observations'):validate_archive(self.data)

    def test_interrupted_csv_recovers_without_network_or_history_rewrite(self):
        authority={p:p.read_bytes() for p in self.data.rglob('*') if p.is_file() and p.name!='history.csv'}
        before=(self.data/'history.csv').read_bytes();(self.data/'history.csv').unlink()
        with self.assertRaisesRegex(ValueError,'history CSV'):validate_archive(self.data)
        def no_network(now):raise AssertionError('No network should run')
        late=datetime(2026,10,24,11,tzinfo=UTC)
        with contextlib.redirect_stdout(io.StringIO()) as log:
            self.assertIsNone(run(['due'],self.data,late,no_network,no_network))
        self.assertIn('Recovering derived history CSV',log.getvalue())
        self.assertEqual(before,(self.data/'history.csv').read_bytes())
        for p,b in authority.items():self.assertEqual(b,p.read_bytes())
        validate_archive(self.data)

    def test_bad_immutable_capture_blocks_derived_recovery(self):
        p=next((self.data/'captures').glob('*.json'));p.write_bytes(p.read_bytes()+b' ')
        (self.data/'history.csv').write_bytes(b'keep evidence')
        with self.assertRaisesRegex(ValueError,'Capture hash'):
            run(['due'],self.data,datetime(2026,10,24,11,tzinfo=UTC),fake_sources,fake_comex)
        self.assertEqual((self.data/'history.csv').read_bytes(),b'keep evidence')

    def test_latest_pages_have_individual_clocks_archives_are_labelled(self):
        site=Path(self.temp.name)/'site';publish(self.data,site)
        for kind in ['daily','weekly']:
            h=(site/'market'/(kind+'.html')).read_text()
            self.assertIn('data-kind="'+kind+'"',h)
            self.assertIn('MarketReportClock',h)
            archive=(site/'market/archive'/kind/'2026-10-24/index.html').read_text()
            self.assertIn('历史档案',archive);self.assertNotIn('MarketReportClock',archive)
        (self.data/'reports/weekly/2026-10-24/latest.json').unlink();publish(self.data,site)
        self.assertIn('data-report-date=""',(site/'market/index.html').read_text())


class IndependentClockTests(unittest.TestCase):
    # Expected dates written from the MYT specification, not computed by the implementation.
    CASES=[
        ('daily','2026-10-24T00:00:00+00:00','2026-10-24','CURRENT'),
        ('daily','2026-10-24T23:59:59+00:00','2026-10-24','CURRENT'),
        ('daily','2026-10-25T00:00:00+00:00','2026-10-24','PENDING'),
        ('daily','2026-10-25T03:59:59+00:00','2026-10-24','PENDING'),
        ('daily','2026-10-25T04:00:00+00:00','2026-10-24','OVERDUE'),
        ('weekly','2026-10-31T01:59:59+00:00','2026-10-24','CURRENT'),
        ('weekly','2026-10-31T02:00:00+00:00','2026-10-24','PENDING'),
        ('weekly','2026-10-31T06:00:00+00:00','2026-10-24','OVERDUE'),
        ('weekly','2026-11-01T00:00:00+00:00','2026-10-31','CURRENT'),
        ('daily','2026-11-01T00:00:00+00:00','2026-11-01','CURRENT'),
        ('daily','2026-10-25T04:00:00+00:00','2026-10-26','EARLY'),
    ]

    def test_myt_daily_weekly_boundaries_and_recovery_window(self):
        for kind,at,day,want in self.CASES:
            with self.subTest(kind=kind,at=at):
                now=datetime.fromisoformat(at)
                self.assertEqual(period_state(kind,day,None,now),want)
        self.assertEqual(expected_period('weekly',datetime.fromisoformat('2026-10-31T01:59:59+00:00')).date().isoformat(),'2026-10-24')
        self.assertEqual(expected_period('weekly',datetime.fromisoformat('2026-10-31T02:00:00+00:00')).date().isoformat(),'2026-10-31')

    def test_one_report_refresh_does_not_mask_other_missing_period(self):
        now=datetime(2026,10,31,6,tzinfo=UTC)
        self.assertEqual(period_state('daily','2026-10-31',None,now),'CURRENT')
        self.assertEqual(period_state('weekly','2026-10-24',None,now),'OVERDUE')
        now=datetime(2026,10,25,4,tzinfo=UTC)
        self.assertEqual(period_state('weekly','2026-10-24',None,now),'CURRENT')
        self.assertEqual(period_state('daily','2026-10-24',None,now),'OVERDUE')

    def test_future_device_clock_warning_and_missing_report(self):
        now=datetime(2026,10,25,4,tzinfo=UTC)
        self.assertEqual(period_state('daily','2026-10-25','2026-10-25T04:06:00+00:00',now),'CLOCK')
        self.assertEqual(period_state('daily','',None,now),'OVERDUE')
        with self.assertRaises(ValueError):expected_period('monthly',now)

    def test_early_manual_preview_does_not_satisfy_daily_or_weekly_schedule(self):
        from .test_market import receipt
        for at,want in [('2026-10-23T23:30:00+00:00',['daily','weekly']),('2026-10-24T01:59:00+00:00',['weekly'])]:
            with tempfile.TemporaryDirectory() as t,contextlib.redirect_stdout(io.StringIO()):
                run(['daily','weekly'],t,datetime.fromisoformat(at),fake_sources,lambda now:receipt('comex'))
                self.assertEqual(due_reports(datetime(2026,10,24,2,tzinfo=UTC),t),want)

    def test_same_date_preview_requires_generation_at_or_after_target(self):
        for kind,day,generated,at in [
            ('daily','2026-10-25','2026-10-24T23:30:00+00:00','2026-10-25T00:00:00+00:00'),
            ('weekly','2026-10-31','2026-10-31T01:59:00+00:00','2026-10-31T02:00:00+00:00')]:
            self.assertEqual(period_state(kind,day,generated,datetime.fromisoformat(at)),'PENDING')
            self.assertEqual(period_state(kind,day,at,datetime.fromisoformat(at)),'CURRENT')

    @unittest.skipUnless(shutil.which('node'),'Node unavailable: browser equivalent not executed locally')
    def test_actual_javascript_against_independent_cases(self):
        cases=[{'kind':k,'now':int(datetime.fromisoformat(t).timestamp()*1000),'day':d,'want':w} for k,t,d,w in self.CASES]
        script="global.window={};global.document={querySelectorAll:()=>[]};global.setInterval=()=>{};"+CLOCK_JS
        script+='\nconst cases='+json.dumps(cases)+';for(const c of cases){const r=window.MarketReportClock.assess(c.kind,c.day,null,c.now);if(r.state!==c.want)throw Error(JSON.stringify({c,r}));}console.log(cases.length);'
        script+="if(window.MarketReportClock.assess('daily','2026-10-25','2026-10-24T23:30:00Z',Date.parse('2026-10-25T00:00:00Z')).state!=='PENDING')throw Error('Early manual preview accepted');"
        result=subprocess.run(['node','-e',script],check=True,capture_output=True,text=True)
        self.assertEqual(int(result.stdout.strip()),len(cases))
