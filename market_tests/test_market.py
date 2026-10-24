import copy
import json
import tempfile
import unittest
from datetime import datetime, timedelta
from pathlib import Path
from unittest.mock import patch
from urllib.error import HTTPError

from market_reports import parsers
from market_reports.core import (ET,MYT,UTC,assess_date,commit_bundle,digest,due_reports,encoded,
    inventory_level,parse_time,rebuild_history,srf_level,verify_bundle,immutable)
from market_reports.sources import collect_one,download,registry
from market_reports.comex import health
from market_reports.report import daily,weekly,latest
from market_reports.render import markdown,publish
from market_reports.__main__ import run,validate_archive

FIX=Path(__file__).parent/'fixtures'
NOW=datetime(2026,10,24,3,0,tzinfo=UTC)


def receipt(key,obs=None,details=None,status='OK'):
    obs=obs or []
    for o in obs:
        o.update(source=key,source_url='https://example.org/'+key,response_sha256='a'*64,fetched_at_utc=NOW.isoformat(),quality='OK')
    return dict(id=key,url='https://example.org/'+key,status=status,observations=obs,details=details or {},fetched_at_utc=NOW.isoformat(),response_sha256='a'*64)


def fake_sources(now):
    out=[]
    for s in registry(now):
        k=s['id'];obs=[];details={}
        fixture={'aaii':'aaii.html','srf':'srf.json','crypto':'crypto.json','vix':'vix.txt','vix3m':'vix3m.txt','ici':'ici.html','treasury':'auctions.json','bea':'bea.txt','fomc':'fed_calendar.txt','bls':'bls.txt','occ':'occ_rss.xml','clarity_bill':'govinfo_clarity_excerpt.xml','genius_bill':'govinfo_genius_excerpt.xml'}.get(k)
        if fixture:
            args={'metric':k} if k in ('vix','vix3m') else {'identity':s['bill_identity']} if s['parser']=='bill' else {}
            obs,details=getattr(parsers,'parse_'+s['parser'])((FIX/fixture).read_bytes(),now,**args)
        out.append(receipt(k,obs,details))
    return out


def fake_comex(now):
    return receipt('comex',status='MISSING')


class CollectionTests(unittest.TestCase):
    def test_aaii_values_and_week_not_web_modified(self):
        obs,d=parsers.parse_aaii((FIX/'aaii.html').read_bytes(),NOW)
        o=[x for x in obs if x['metric']=='aaii_spread' and x['observation_date']=='2026-10-21'][0]
        self.assertAlmostEqual(o['value'],-8.9)
        self.assertIsNone(o['publication_date'])
        self.assertGreaterEqual(len(obs),8)

    def test_aaii_invalid_composition_rejected(self):
        b=(FIX/'aaii.html').read_bytes().replace(b'36.9%',b'96.9%')
        with self.assertRaises(ValueError):parsers.parse_aaii(b,NOW)

    def test_crypto_calendar_seven_day_not_seventh_row(self):
        obs,_=parsers.parse_crypto((FIX/'crypto.json').read_bytes(),NOW)
        bydate={o['observation_date']:o for o in obs}
        self.assertEqual(bydate['2026-10-24']['value'],51)
        self.assertEqual(bydate['2026-10-17']['value'],55)

    def test_srf_all_sessions_exercises_excluded_and_sum(self):
        obs,d=parsers.parse_srf((FIX/'srf.json').read_bytes(),NOW)
        week=[o for o in obs if '2026-10-19'<=o['observation_date']<='2026-10-23']
        self.assertEqual(sum(o['value'] for o in week),12e6)
        self.assertEqual(len(d['excluded_exercises']),1)
        self.assertEqual(d['excluded_exercises'][0]['amount'],67e6)
        self.assertTrue(all(o['complete'] for o in week))

    def test_srf_duplicate_and_component_mismatch_rejected(self):
        js=json.loads((FIX/'srf.json').read_text());rows=js['repo']['operations']
        rows.append(copy.deepcopy(rows[0]))
        with self.assertRaises(ValueError):parsers.parse_srf(encoded(js),NOW)
        rows.pop();rows[0]['totalAmtAccepted']=1
        with self.assertRaises(ValueError):parsers.parse_srf(encoded(js),NOW)

    def test_srf_single_session_provisional(self):
        js=json.loads((FIX/'srf.json').read_text());js['repo']['operations']=js['repo']['operations'][:1]
        obs,_=parsers.parse_srf(encoded(js),NOW)
        self.assertFalse(obs[0]['complete'])

    def test_ici_unit_and_asset_delta(self):
        obs,d=parsers.parse_ici((FIX/'ici.html').read_bytes(),NOW)
        self.assertEqual(obs[0]['value'],7944.57e9)
        self.assertEqual(obs[1]['value'],21.49e9)
        self.assertIsNone(d['net_flow_usd'])
        with self.assertRaises(ValueError):parsers.parse_ici((FIX/'ici.html').read_bytes().replace(b'7,944.57',b'9,944.57'),NOW)

    def test_cboe_latest_close(self):
        obs,_=parsers.parse_cboe((FIX/'vix.txt').read_bytes(),NOW)
        self.assertEqual(obs[-1]['observation_date'],'2026-10-23')
        self.assertAlmostEqual(obs[-1]['value'],19.45)

    def test_treasury_coupon_amount_and_clock(self):
        obs,d=parsers.parse_auctions((FIX/'auctions.json').read_bytes(),NOW)
        rows=[a for a in d['auctions'] if '2026-10-24'<=a['date']<='2026-10-31' and a['type']!='Bill']
        self.assertEqual(sum(a['offering_usd'] for a in rows),213e9)
        self.assertEqual(sum(a['offering_usd'] for a in rows if a['type']!='FRN'),183e9)
        self.assertEqual(sum(a['offering_usd'] for a in rows if a['type']=='FRN'),30e9)
        self.assertTrue(all(a['close_myt'] for a in d['auctions']))
        self.assertTrue(all(a['tail_bp'] is None for a in rows))

    def test_provenance_and_partial_api_failure(self):
        spec=registry(NOW)[0]
        def ok(url):return (FIX/'aaii.html').read_bytes(),{'response_sha256':'b'*64,'fetched_at_utc':NOW.isoformat()}
        result=collect_one(spec,NOW,ok)
        self.assertEqual(result['status'],'OK')
        self.assertTrue(all(o['source_url']==spec['url'] and o['response_sha256']=='b'*64 for o in result['observations']))
        def fail(url):raise TimeoutError('test timeout')
        bad=collect_one(spec,NOW,fail)
        self.assertEqual(bad['status'],'MISSING');self.assertEqual(bad['observations'],[])

    def test_btc_daily_date_uses_provider_utc_not_us_equity_timezone(self):
        js={'chart':{'error':None,'result':[{'meta':{'exchangeTimezoneName':'UTC','currency':'USD'},'timestamp':[1792800000],
             'indicators':{'quote':[{'close':[60000]}]}}]}}
        obs,_=parsers.parse_yahoo(encoded(js),NOW,'btc')
        self.assertEqual(obs[0]['observation_date'],'2026-10-24')
        self.assertEqual(obs[0]['observation_timezone'],'UTC')

    def test_cnn_provider_epoch_is_not_invented_publication(self):
        data={'fear_and_greed':{'score':42,'rating':'fear','timestamp':1792713600000}}
        obs,_=parsers.parse_cnn(encoded(data),NOW)
        self.assertEqual(obs[0]['observation_date'],'2026-10-23')
        self.assertIsNone(obs[0]['publication_date'])
        self.assertEqual(obs[0]['provider_updated_at'],'2026-10-23T00:00:00+00:00')

    def test_no_retry_access_denial(self):
        calls=[]
        def deny(req,timeout):
            calls.append(1);raise HTTPError(req.full_url,418,'denied',{},None)
        with self.assertRaises(HTTPError):download('https://example.org',opener=deny)
        self.assertEqual(len(calls),1)

    def test_timeout_retry_bounded(self):
        calls=[]
        def timeout(req,timeout):calls.append(1);raise TimeoutError('test')
        with patch('market_reports.sources.time.sleep'):
            with self.assertRaises(TimeoutError):download('https://example.org',attempts=2,opener=timeout)
        self.assertEqual(len(calls),2)


class DateAndMathTests(unittest.TestCase):
    def test_timezone_and_dst(self):
        self.assertEqual(datetime(2026,10,28,14,tzinfo=ET).astimezone(MYT).hour,2)
        self.assertEqual(datetime(2026,11,4,14,tzinfo=ET).astimezone(MYT).hour,3)
        with self.assertRaises(ValueError):parse_time('2026-10-24T08:00:00')

    def test_missing_stale_future(self):
        self.assertEqual(assess_date('2026-10-01',NOW,4),'STALE')
        self.assertEqual(assess_date('2026-10-25',NOW,4),'FUTURE')
        self.assertEqual(assess_date('2026-10-23',NOW,4),'OK')

    def test_srf_boundaries(self):
        self.assertEqual([srf_level(v) for v in [0,9999999999,10e9,49999999999,50e9,100e9,100000000001]],['Normal','Normal','Stress','Stress','Red Alert','Red Alert','Severe'])
        with self.assertRaises(ValueError):srf_level(-1)

    def test_inventory_boundaries(self):
        self.assertEqual([inventory_level(v) for v in [None,-1,-1.0001,-3,-3.001,-5,-5.001]],['UNKNOWN','NORMAL','YELLOW','YELLOW','ORANGE','ORANGE','RED'])

    def test_comex_same_day_after05_not_generated_at(self):
        s={'available':True,'update_status':'UNCHANGED','freshness':'WITHIN_AGE_LIMIT','last_update':{'attempted_at_utc':'2026-10-23T23:59:59+00:00'}}
        runs=[{'status':'completed','conclusion':'success','event':'schedule','updated_at':'2026-10-24T00:00:13+00:00'}]
        self.assertEqual(health(s,NOW,runs),[])
        s['last_update']['attempted_at_utc']='2026-10-22T23:59:59+00:00'
        self.assertIn('NOT_TODAY_AFTER_05_MYT',health(s,NOW,runs))
        s['last_update']['attempted_at_utc']='2026-10-24T04:00:00+00:00'
        self.assertIn('FUTURE_OR_OVERDUE_ATTEMPT',health(s,NOW,runs))

    def test_comex_run_fail_and_snapshot_lag(self):
        s={'available':True,'update_status':'UNCHANGED','freshness':'WITHIN_AGE_LIMIT','last_update':{'attempted_at_utc':'2026-10-23T23:00:00+00:00'}}
        runs=[{'status':'completed','conclusion':'success','event':'schedule','updated_at':'2026-10-24T00:00:13+00:00'}]
        self.assertIn('SNAPSHOT_BEHIND_RUN',health(s,NOW,runs))
        runs[0]['conclusion']='failure'
        self.assertIn('LATEST_COLLECTION_FAILED_OR_CANCELLED',health(s,NOW,runs))

    def test_calendars(self):
        _,b=parsers.parse_bea((FIX/'bea.txt').read_bytes(),NOW)
        self.assertTrue(any(e['at_myt']=='2026-10-29T20:30:00+08:00' and 'GDP' in e['name'] for e in b['events']))
        _,f=parsers.parse_fomc((FIX/'fed_calendar.txt').read_bytes(),NOW)
        self.assertEqual(f['events'][0]['at_myt'],'2026-10-29T02:00:00+08:00')

    def test_schedule_due_and_no_early_execution(self):
        with tempfile.TemporaryDirectory() as t:
            self.assertEqual(due_reports(datetime(2026,10,24,0,0,tzinfo=UTC),t),['daily'])
            self.assertEqual(due_reports(datetime(2026,10,24,2,0,tzinfo=UTC),t),['daily','weekly'])
            self.assertEqual(due_reports(datetime(2026,10,23,23,59,tzinfo=UTC),t),[])


class IntegrityAndEndToEndTests(unittest.TestCase):
    def test_bundle_idempotent_and_tamper_rejection(self):
        with tempfile.TemporaryDirectory() as t:
            files={'report.md':'test','report.json':'{}','quality.json':'{}'}
            rev=commit_bundle(t,files)
            self.assertEqual(rev,commit_bundle(t,files))
            Path(t,rev,'report.md').write_text('tampered')
            with self.assertRaises(ValueError):verify_bundle(Path(t,rev))
            with self.assertRaises(ValueError):commit_bundle(t,files)

    def test_interrupted_bundle_recovery(self):
        with tempfile.TemporaryDirectory() as t:
            files={'report.md':'test','report.json':'{}','quality.json':'{}'}
            hashes={k:digest(v.encode()) for k,v in files.items()};rev=digest(encoded(hashes))[:20]
            immutable(Path(t,rev,'report.md'),b'test')
            self.assertFalse(Path(t,rev,'MANIFEST.json').exists())
            self.assertEqual(commit_bundle(t,files),rev)
            verify_bundle(Path(t,rev))

    def test_full_pipeline_partial_failure_archive_and_render(self):
        with tempfile.TemporaryDirectory() as t:
            d=Path(t,'data');site=Path(t,'site')
            q=run(['daily','weekly'],d,NOW,fake_sources,fake_comex)
            self.assertEqual(q['acceptance'],'DEGRADED')
            first=(d/'history.csv').read_bytes()
            run(['daily','weekly'],d,NOW,fake_sources,fake_comex)
            self.assertEqual(first,(d/'history.csv').read_bytes())
            self.assertEqual(len(list((d/'captures').glob('*.json'))),1)
            self.assertEqual(publish(d,site),2)
            html=(site/'market/daily.html').read_text()
            self.assertIn('width=device-width',html)
            self.assertIn('本次COMEX未核验',html)
            self.assertIn('Timeline',(site/'market/weekly.html').read_text())
            validate_archive(d)
            capture=next((d/'captures').glob('*.json'));capture.write_text(capture.read_text()+' ')
            with self.assertRaises(ValueError):validate_archive(d)

    def test_healthy_due_rerun_does_not_collect(self):
        with tempfile.TemporaryDirectory() as t:
            run(['daily','weekly'],t,NOW,fake_sources,fake_comex)
            for p in Path(t,'reports').glob('*/*/latest.json'):
                x=json.loads(p.read_text());x['degraded']=False;p.write_bytes(encoded(x))
            self.assertEqual(due_reports(NOW,t),[])
            with patch('market_reports.__main__.collect') as c:
                self.assertIsNone(run(['due'],t,NOW,fake_sources,fake_comex));c.assert_not_called()

    def test_gfm_tables_have_contiguous_rows(self):
        c={'generated_at_utc':NOW.isoformat(),'sources':[fake_comex(NOW)],'observations':[]}
        md=weekly(c,[])
        self.assertNotIn('\n\n|---',md)
        self.assertIn('|资产|直接/间接影响|\n|---|---|',md)

    def test_html_escaping(self):
        h=markdown('<script>alert(1)</script> [bad](javascript:alert) **test**')
        self.assertNotIn('<script>',h);self.assertNotIn('href="javascript:',h);self.assertIn('<strong>test</strong>',h)

    def test_weekly_legal_status_not_auto_effective(self):
        obs,details=parsers.parse_federal_register((FIX/'fr.json').read_bytes(),NOW)
        self.assertEqual(details['items'][0]['legal_status'],'Rule')
        self.assertIsNone(details['items'][0]['effective_date'])
        c={'generated_at_utc':NOW.isoformat(),'sources':[receipt('federal_register',details=details)],'observations':[]}
        md=weekly(c,[])
        self.assertIn('生效 待核验',md);self.assertNotIn('已经生效',md)

    def test_workflow_permissions_and_no_untrusted_execution(self):
        w=(Path(__file__).parents[1]/'.github/workflows/market-reports.yml').read_text()
        self.assertIn('permissions:\n  contents: read',w)
        self.assertNotIn('pull_request_target',w);self.assertNotIn('write-all',w)
        self.assertIn('cancel-in-progress: false',w)
        self.assertIn('workflow_dispatch:',w)
        for line in w.splitlines():
            if 'uses: actions/' in line:
                ref=line.split('@')[1].split()[0];self.assertEqual(len(ref),40)
