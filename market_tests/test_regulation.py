"""Source-identity, legal-stage, pagination and backward-compatible archive checks."""
import copy
import json
import tempfile
import unittest
from datetime import datetime
from pathlib import Path
from unittest.mock import patch
from urllib.error import HTTPError
from market_reports import parsers
from market_reports.core import UTC,encoded,digest,rebuild_history
from market_reports.sources import collect_one,registry
from market_reports.regulation import collect_register,fr_page_url,status_from_title,timeline_day
from market_reports.report import timeline,regulatory_upcoming,weekly
from market_reports.__main__ import validate_archive
from .test_market import receipt

FIX=Path(__file__).parent/'fixtures'
NOW=datetime(2026,10,24,7,0,tzinfo=UTC)
IDENTITIES={'clarity':{'congress':'119','type':'HR','number':'3633'},'genius':{'congress':'119','type':'S','number':'1582'}}


def fr_document(number='2026-1',title='Stablecoin final rule',typ='Rule'):
    return {'document_number':number,'title':title,'type':typ,'publication_date':'2026-10-23',
            'html_url':'https://www.federalregister.gov/documents/2026/10/23/'+number+'/test','abstract':'Stablecoin issuance'}


def fr_downloader(second_error=None,duplicate=False,bad_detail=False):
    first=fr_document();second=fr_document('2026-2','Proposed stablecoin rule','Proposed Rule')
    def fetch(url):
        if '/documents.json?' in url:
            if 'page=2' in url:
                if second_error:raise second_error
                item=first if duplicate else second
            else:item=first
            obj={'count':2,'total_pages':2,'results':[item]}
        else:
            identity='2026-2' if '2026-2.json' in url else '2026-1'
            obj={'document_number':'wrong' if bad_detail else identity,'type':'Proposed Rule' if identity=='2026-2' else 'Rule',
                 'effective_on':None if identity=='2026-2' else '2027-01-18','comments_close_on':'2026-10-30' if identity=='2026-2' else None,
                 'pdf_url':'https://www.govinfo.gov/test.pdf'}
        b=encoded(obj);return b,{'response_sha256':digest(b),'fetched_at_utc':NOW.isoformat(),'http_status':200}
    return fetch


class OfficialRegulationTests(unittest.TestCase):
    def test_actual_occ_announcement_is_not_effective_rule(self):
        _,d=parsers.parse_rss((FIX/'occ_rss.xml').read_bytes(),NOW)
        item=next(i for i in d['items'] if 'GENIUS' in i['title'])
        self.assertEqual(item['legal_status'],'FinalRuleAnnouncement')
        self.assertIsNone(item['effective_date'])
        self.assertEqual(timeline_day(item),'2026-10-21')
        self.assertEqual(item['topics'],['稳定币'])

    def test_staff_statement_never_promoted_to_rule(self):
        self.assertEqual(status_from_title('Staff Statement on Proposed Rules'),'GuidanceOrSpeech')
        self.assertEqual(status_from_title('Agency Proposes Stablecoin Regulation'),'ProposalAnnouncement')
        self.assertEqual(status_from_title('Agency Finalizes Stablecoin Rule'),'FinalRuleAnnouncement')
        self.assertEqual(status_from_title('Agency Publishes Examination Priorities'),'SupervisoryPriorities')
        self.assertEqual(status_from_title('Agency Approves Bank Application'),'UNRESOLVED')

    def test_actual_genius_public_law_and_no_recent_action(self):
        _,d=parsers.parse_bill((FIX/'govinfo_genius_excerpt.xml').read_bytes(),NOW,IDENTITIES['genius'])
        self.assertEqual(d['enactment_record'],'ENACTED')
        self.assertEqual(d['laws'],[{'type':'Public Law','number':'119-27'}])
        self.assertEqual(d['latest_action']['date'],'2025-07-18')
        self.assertEqual(d['actions_in_window'],0)
        self.assertEqual(d['items'],[])

    def test_actual_clarity_cloture_is_not_enactment(self):
        _,d=parsers.parse_bill((FIX/'govinfo_clarity_excerpt.xml').read_bytes(),NOW,IDENTITIES['clarity'])
        self.assertEqual(d['enactment_record'],'NO_ENACTMENT_RECORD')
        self.assertIn('cloture',d['latest_action']['text'])
        self.assertEqual(d['actions_in_window'],0)

    def test_wrong_bill_and_future_action_rejected(self):
        body=(FIX/'govinfo_clarity_excerpt.xml').read_bytes()
        with self.assertRaises(ValueError):parsers.parse_bill(body,NOW,IDENTITIES['genius'])
        with self.assertRaises(ValueError):parsers.parse_bill(body.replace(b'2026-09-15',b'2026-12-15'),NOW,IDENTITIES['clarity'])

    def test_congress_event_date_not_invented_publication(self):
        item={'title':'CLARITY Act passed House','url':'https://www.govinfo.gov/test.xml','publication_date':None,
              'event_date':'2026-10-22','legal_status':'CongressAction','effective_date':None}
        capture={'generated_at_utc':NOW.isoformat(),'observations':[],'sources':[receipt('clarity_bill',details={'items':[item]})]}
        rows=timeline(capture)
        self.assertEqual(rows[0]['timeline_date'],'2026-10-22')
        self.assertIsNone(rows[0]['publication_date'])
        self.assertIn('正式国会行动记录（不等于已成法）',weekly(capture,[]))

    def test_us_timestamp_day_and_exclusive_week_end(self):
        self.assertEqual(timeline_day({'publication_date':'2026-10-24T01:00:00+00:00'}),'2026-10-23')
        self.assertEqual(timeline_day({'publication_date':'2026-10-24'}),'2026-10-24')
        i={'title':'Stablecoin rule','publication_date':'2026-10-24','url':'https://www.federalregister.gov/test','legal_status':'Rule','effective_date':None}
        c={'generated_at_utc':NOW.isoformat(),'sources':[receipt('federal_register',details={'items':[i]})],'observations':[]}
        self.assertEqual(timeline(c),[])

    def test_register_full_window_pagination_and_types(self):
        r=collect_register(NOW,fr_downloader())
        self.assertEqual(r['status'],'OK')
        self.assertEqual(r['details']['scanned_documents'],2)
        self.assertEqual([i['legal_status'] for i in r['details']['items']],['Rule','Proposed Rule'])
        self.assertEqual(r['details']['items'][0]['effective_date'],'2027-01-18')
        self.assertNotIn('term',fr_page_url(NOW,1))
        self.assertIn('2026-10-17',fr_page_url(NOW,1));self.assertIn('2026-10-23',fr_page_url(NOW,1))

    def test_generic_crypto_rule_is_not_direct_bitcoin_or_ether_obligation(self):
        from market_reports.regulation import asset_relevance
        items=[{'title':'OCC Final Rule for Stablecoin Issuers under GENIUS Act'}]
        self.assertIn('间接影响可能',asset_relevance(items,'BTC'))
        self.assertIn('间接影响可能',asset_relevance(items,'ETH'))
        self.assertIn('直接相关主题',asset_relevance(items,'Stablecoin'))
        self.assertIn('未确认',asset_relevance(items,'Tokenized Securities'))
        self.assertIn('未确认',asset_relevance([{'title':'Tokenized Deposits'},{'title':'Securities Custody'}],'Tokenized Securities'))

    def test_plain_language_clarity_is_not_a_crypto_signal(self):
        from market_reports.regulation import KEY
        self.assertFalse(KEY.search('Information collection improves clarity of paperwork requirements'))
        self.assertTrue(KEY.search('Digital Asset Market Clarity Act'))
        self.assertFalse(KEY.search('whether this improves regulatory clarity'))
        xml=b'<rss><channel><item><title>Agency Budget Review</title><description>whether this improves clarity</description><link>https://www.sec.gov/test</link><pubDate>21 Oct 2026 07:00:00 -0400</pubDate></item></channel></rss>'
        _,d=parsers.parse_rss(xml,NOW)
        self.assertFalse(d['items'][0]['topic_signal'])

    def test_register_partial_page_failure_keeps_verified_facts(self):
        r=collect_register(NOW,fr_downloader(second_error=TimeoutError('test')))
        self.assertEqual(r['status'],'PARTIAL')
        self.assertEqual(len(r['details']['items']),1)
        self.assertFalse(r['details']['coverage_complete'])
        self.assertEqual(r['details']['items'][0]['legal_status'],'Rule')

    def test_register_duplicate_page_rejected(self):
        r=collect_register(NOW,fr_downloader(duplicate=True))
        self.assertEqual(r['status'],'PARTIAL')
        self.assertTrue(any('Duplicate' in x for x in r['details']['coverage_issues']))

    def test_register_detail_mismatch_does_not_invent_effective_date(self):
        r=collect_register(NOW,fr_downloader(bad_detail=True))
        self.assertTrue(all(i['effective_date'] is None and 'detail_error' in i for i in r['details']['items']))

    def test_only_structured_future_deadlines_rendered(self):
        r=collect_register(NOW,fr_downloader())
        c={'generated_at_utc':NOW.isoformat(),'sources':[r],'observations':[]}
        rows=regulatory_upcoming(c)
        self.assertEqual(len(rows),1);self.assertIn('2026-10-30',rows[0]);self.assertIn('意见截止日',rows[0])
        self.assertNotIn('2027-01-18',' '.join(rows))


class AvailabilityAndHistoryTests(unittest.TestCase):
    def test_access_denial_does_not_retry_alternate_ici_route(self):
        calls=[]
        spec=next(s for s in registry(NOW) if s['id']=='ici')
        def fetch(url):calls.append(url);raise HTTPError(url,403,'denied',{},None)
        result=collect_one(spec,NOW,fetch)
        self.assertEqual(result['status'],'MISSING');self.assertEqual(calls,[spec['url']])

    def test_ici_workbook_units_components_and_13_week_asset_trend(self):
        obs,d=parsers.parse_ici_workbook((FIX/'ici_public_workbook.xls').read_bytes(),NOW)
        latest=max((o for o in obs if o['metric']=='mmf_assets_usd'),key=lambda o:o['observation_date'])
        delta=max((o for o in obs if o['metric']=='mmf_weekly_asset_change_usd'),key=lambda o:o['observation_date'])
        self.assertEqual(latest['value'],7944573e6)
        self.assertEqual(delta['value'],21489e6)
        self.assertEqual(d['verified_weeks'],20)
        self.assertEqual(d['asset_trend_13w']['asset_change_usd'],83827e6)
        self.assertIsNone(d['asset_trend_13w']['net_flow_usd'])
        self.assertIsNone(latest['publication_date'])

    def test_calendar_html_denial_cannot_pass_as_empty_calendar(self):
        with self.assertRaises(ValueError):parsers.parse_bls(b'<html><h1>Access Denied</h1></html>',NOW)

    def test_legacy_captures_remain_valid_without_rewriting(self):
        root=Path(__file__).parents[1]
        old=next(p for p in (root/'market_data/captures').glob('*.json') if json.loads(p.read_text())['schema_version']==1)
        original=old.read_bytes()
        with tempfile.TemporaryDirectory() as t:
            p=Path(t,'captures',old.name);p.parent.mkdir();p.write_bytes(original)
            rebuild_history(t)
            self.assertEqual(validate_archive(t),1)
            self.assertEqual(p.read_bytes(),original)


class IncidentTests(unittest.TestCase):
    def test_no_human_issue_is_edited_and_bot_incident_deduplicates(self):
        from market_reports.alerts import reconcile,TITLE,MARKER
        calls=[]
        human={'number':1,'title':TITLE,'body':MARKER,'user':{'login':'human'}}
        bot={'number':2,'title':TITLE,'body':MARKER,'user':{'login':'github-actions[bot]'}}
        def api(path,method='GET',payload=None):
            calls.append((path,method,payload));return [human,bot] if method=='GET' else {}
        self.assertEqual(reconcile(api,['actual test failure'],'https://github.com/owner/repo/actions/runs/1'),'UPDATED')
        self.assertEqual(calls[-1][0],'/issues/2');self.assertEqual(calls[-1][1],'PATCH')

    def test_first_real_failure_payload_opens_one_marked_issue(self):
        from market_reports.alerts import reconcile,TITLE,MARKER
        calls=[]
        def api(path,method='GET',payload=None):
            calls.append((path,method,payload));return [] if method=='GET' else {'number':1}
        self.assertEqual(reconcile(api,['critical comex missing'],'https://github.com/owner/repo/actions/runs/3'),'OPENED')
        self.assertEqual(calls[-1][0:2],('/issues','POST'))
        self.assertEqual(calls[-1][2]['title'],TITLE)
        self.assertIn(MARKER,calls[-1][2]['body'])
        self.assertNotIn('assignees',calls[-1][2])

    def test_incident_recovery_closes_only_marked_bot_issue(self):
        from market_reports.alerts import reconcile,TITLE,MARKER
        calls=[]
        def api(path,method='GET',payload=None):
            calls.append((path,method,payload));return [{'number':5,'title':TITLE,'body':MARKER,'user':{'login':'github-actions[bot]'}}] if method=='GET' else {}
        self.assertEqual(reconcile(api,[],'https://github.com/owner/repo/actions/runs/2'),'RESOLVED')
        self.assertEqual(calls[-1],('/issues/5','PATCH',{'state':'closed','state_reason':'completed'}))

    def test_healthy_report_does_not_create_notification(self):
        from market_reports.alerts import reconcile
        calls=[]
        def api(path,method='GET',payload=None):calls.append(method);return []
        self.assertEqual(reconcile(api,[],'https://github.com/owner/repo/actions/runs/2'),'HEALTHY_NO_INCIDENT')
        self.assertEqual(calls,['GET'])

    def test_missing_expected_weekly_and_failed_run_are_detected(self):
        from market_reports.alerts import problems
        with tempfile.TemporaryDirectory() as t:
            p=problems(t,NOW,'failure')
            self.assertTrue(any('weekly report missing' in x for x in p))
            self.assertTrue(any('daily report missing' in x for x in p))
            self.assertIn('Report workflow result: failure',p)
