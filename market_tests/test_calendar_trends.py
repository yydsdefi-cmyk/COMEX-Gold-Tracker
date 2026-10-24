"""Actual official calendar fixtures, SRF exclusions and independently specified unit checks."""
import copy
import json
import unittest
from datetime import datetime
from decimal import Decimal
from pathlib import Path

from market_reports import parsers
from market_reports.calendar import collect_calendar,parse_calendar,URL
from market_reports.core import UTC,encoded,digest,srf_level
from market_reports.report import daily,weekly,event_list,event_lines
from market_reports.sources import registry,collect_one
from market_reports.trends import weekly_changes,dated_series
from .test_market import receipt,fake_sources

FIX=Path(__file__).parent/'fixtures'
NOW=datetime(2026,10,24,7,tzinfo=UTC)


def calendar_downloader(fail_child=False,wrong_child=False):
    calls=[]
    def fetch(url):
        calls.append(url)
        child=url!=URL
        if child and fail_child:raise TimeoutError('isolated child failure')
        body=(FIX/('nyfed_calendar_nov.html' if child and not wrong_child else 'nyfed_calendar_oct.html')).read_bytes()
        return body,{'response_sha256':digest(body),'fetched_at_utc':NOW.isoformat(),'http_status':200}
    return fetch,calls


def point(metric,value,day,**more):
    source={'aaii_spread':'aaii','crypto_fg':'crypto','srf_usd':'srf','mmf_assets_usd':'ici','comex_registered_ratio':'comex'}.get(metric,metric)
    return {'metric':metric,'source':source,'value':value,'observation_date':day,'publication_date':None,
            'source_url':'https://example.org/'+source,'response_sha256':'a'*64,'quality':'OK',
            'fetched_at_utc':NOW.isoformat(),'complete':True,**more}


def capture(points,statuses=None,at=NOW):
    states={o['source']:'OK' for o in points};states.update(statuses or {})
    return {'generated_at_utc':at.isoformat(),'observations':points,
            'sources':[receipt(k,status=v) for k,v in states.items()]}


class SRFPrecisionTests(unittest.TestCase):
    def body(self):return json.loads((FIX/'srf.json').read_text())

    def test_sve_only_abbreviation_excluded(self):
        js=self.body();row=next(r for r in js['repo']['operations'] if r['note']);row['note']='SVE'
        obs,d=parsers.parse_srf(encoded(js),NOW)
        self.assertEqual(len(d['excluded_exercises']),1)
        self.assertEqual(sum(o['value'] for o in obs if '2026-10-19'<=o['observation_date']<='2026-10-23'),12e6)

    def test_latest_word_is_not_test_operation(self):
        js=self.body();row=next(r for r in js['repo']['operations'] if not r['note']);row['note']='latest operational update'
        obs,d=parsers.parse_srf(encoded(js),NOW)
        self.assertEqual(len(d['excluded_exercises']),1)
        self.assertEqual(len(obs),10)

    def test_aware_update_offset_preserved_and_not_first_publication(self):
        js=self.body();js['repo']['operations'][0]['lastUpdated']='2026-10-23T12:30:26Z'
        obs,_=parsers.parse_srf(encoded(js),NOW);o=next(x for x in obs if x['observation_date']=='2026-10-23')
        # The afternoon update is later; inspect the morning-only subset to isolate conversion.
        js['repo']['operations']=js['repo']['operations'][:1]
        only,_=parsers.parse_srf(encoded(js),NOW)
        self.assertEqual(only[0]['provider_updated_at'],'2026-10-23T12:30:26+00:00')
        self.assertIsNone(o['publication_date']);self.assertIsNone(only[0]['publication_date'])

    def test_two_same_sessions_not_full_day(self):
        js=self.body();rows=[r for r in js['repo']['operations'] if r['operationDate']=='2026-10-23']
        rows[1]['releaseTime']=rows[0]['releaseTime'];rows[1]['closeTime']=rows[0]['closeTime']
        js['repo']['operations']=rows
        obs,_=parsers.parse_srf(encoded(js),NOW);self.assertFalse(obs[0]['complete'])

    def test_unclassified_latest_method_is_provisional(self):
        js=self.body();other=copy.deepcopy(js['repo']['operations'][0]);other['operationId']='unclassified-test-id';other['operationMethod']='Changed Method'
        js['repo']['operations'].append(other);body=encoded(js)
        spec=next(s for s in registry(NOW) if s['id']=='srf')
        r=collect_one(spec,NOW,lambda url:(body,{'response_sha256':digest(body),'fetched_at_utc':NOW.isoformat()}))
        self.assertEqual(r['status'],'PROVISIONAL');self.assertEqual(len(r['details']['unclassified_operations']),1)

    def test_partial_usage_never_rendered_as_full_day_normal(self):
        o=point('srf_usd',1e6,'2026-10-23',complete=False,level='Normal',operation_count=1)
        r=receipt('srf',[o],status='PROVISIONAL');c={'generated_at_utc':NOW.isoformat(),'observations':[o],'sources':[r]}
        md=daily(c);self.assertNotIn('→ Normal',md);self.assertIn('全天等级待确认',md)
        self.assertIn('完整使用量/等级待确认',md)
        w=weekly(c,[]);self.assertNotIn('最大单日',w);self.assertIn('不把小额部分值标为全天Normal',w)

    def test_crypto_daily_stamp_not_invented_publication(self):
        obs,_=parsers.parse_crypto((FIX/'crypto.json').read_bytes(),NOW)
        self.assertTrue(all(o['publication_date'] is None and o.get('provider_timestamp') for o in obs))

    def test_future_operation_rejected(self):
        js=self.body();js['repo']['operations'][0]['operationDate']='2026-10-25'
        with self.assertRaises(ValueError):parsers.parse_srf(encoded(js),NOW)


class PublicCalendarTests(unittest.TestCase):
    def test_actual_october_calendar_eci_and_empty_holiday_cells(self):
        d=parse_calendar((FIX/'nyfed_calendar_oct.html').read_bytes())
        e=next(e for e in d['events'] if e['event_id']=='eci')
        self.assertEqual(e['at_myt'],'2026-10-30T20:30:00+08:00')
        self.assertEqual(e['release_url'],'https://www.bls.gov/news.release/eci.toc.htm')
        self.assertEqual(d['through'],'2026-10-31');self.assertIsNone(e['publication_date'])

    def test_actual_november_calendar_converts_after_dst(self):
        d=parse_calendar((FIX/'nyfed_calendar_nov.html').read_bytes())
        e=next(e for e in d['events'] if e['event_id']=='jobs')
        self.assertEqual(e['at_myt'],'2026-11-06T21:30:00+08:00')

    def test_next_month_fetched_only_when_required(self):
        get,calls=calendar_downloader();r=collect_calendar(NOW,get)
        self.assertEqual(r['status'],'OK');self.assertEqual(calls,[URL])
        get,calls=calendar_downloader();r=collect_calendar(datetime(2026,10,25,2,tzinfo=UTC),get)
        self.assertEqual(r['status'],'OK');self.assertEqual(len(calls),2)
        self.assertEqual(r['details']['calendar_covers_through'],'2026-11-30')

    def test_child_failure_retains_verified_parent_events(self):
        get,calls=calendar_downloader(fail_child=True);r=collect_calendar(datetime(2026,10,25,2,tzinfo=UTC),get)
        self.assertEqual(r['status'],'PARTIAL');self.assertEqual(len(calls),2)
        self.assertTrue(any(e['event_id']=='eci' for e in r['details']['events']))
        self.assertTrue(all(e['source_response_sha256'] for e in r['details']['events']))

    def test_wrong_child_month_not_claimed_as_coverage(self):
        get,_=calendar_downloader(wrong_child=True);r=collect_calendar(datetime(2026,10,25,2,tzinfo=UTC),get)
        self.assertEqual(r['status'],'PARTIAL');self.assertEqual(len(r['details']['pages']),1)

    def test_stale_calendar_cannot_be_green(self):
        get,_=calendar_downloader();r=collect_calendar(datetime(2026,12,1,tzinfo=UTC),get)
        self.assertEqual(r['status'],'INCOMPLETE')

    def test_html_error_missing_timezone_and_missing_weekday_rejected(self):
        body=(FIX/'nyfed_calendar_oct.html').read_bytes()
        for invalid in [b'<html>Access denied</html>',body.replace(b'all Eastern Time',b'Local Time'),body.replace(b'<div>30',b'<div>31')]:
            with self.assertRaises(ValueError):parse_calendar(invalid)

    def test_untrusted_next_month_link_rejected(self):
        body=(FIX/'nyfed_calendar_oct.html').read_bytes().replace(b'/research/calendars/i-nov26.html',b'https://example.org/calendar')
        with self.assertRaises(ValueError):parse_calendar(body)

    def test_primary_calendar_and_nyfed_corroboration_not_duplicate_events(self):
        receipts=fake_sources(NOW);c={'generated_at_utc':NOW.isoformat(),'observations':[],'sources':receipts}
        e=event_list(c,True);self.assertEqual(len(e),4)
        gdp=next(x for x in e if x['event_id']=='gdp');self.assertEqual(len(gdp['evidence']),2)
        self.assertEqual(gdp['source'],'BEA');self.assertEqual(sum(x['event_id']=='eci' for x in e),1)

    def test_conflicting_calendar_times_remain_flagged(self):
        e={'name':'Consumer Price Index','at_myt':'2026-10-24T20:30:00+08:00','source':'BLS','tier1':True}
        alternate={**e,'at_myt':'2026-10-24T21:30:00+08:00','source':'NYFed calendar'}
        c={'generated_at_utc':NOW.isoformat(),'observations':[],'sources':[receipt('bls',details={'events':[e]}),receipt('nyfed_calendar',details={'events':[alternate]})]}
        rows=event_list(c);self.assertEqual(len(rows),2);self.assertTrue(all(x['time_conflict'] for x in rows))
        self.assertIn('来源时刻冲突',''.join(event_lines(c)))


class TrendMathTests(unittest.TestCase):
    def row(self,c,metric,prior=None):return next(x for x in weekly_changes(c,prior or []) if x['metric']==metric)

    def test_independent_price_yield_spread_and_dollar_units(self):
        values=[('sp500',100,110,Decimal('10'),'%',1),('us10y',4,4.1,Decimal('10'),'bp',1),
                ('aaii_spread',-3,-8,Decimal('-5'),'pp',1),('srf_usd',5e9,12e9,Decimal('7'),'B USD',1e9),
                ('mmf_assets_usd',7000e9,7900e9,Decimal('900'),'B USD',1e9),
                ('comex_registered_ratio',64,63,Decimal('-1'),'pp',1)]
        for metric,a,b,want,unit,scale in values:
            with self.subTest(metric=metric):
                c=capture([point(metric,a,'2026-10-16'),point(metric,b,'2026-10-23')]);r=self.row(c,metric)
                self.assertAlmostEqual(r['change'],float(want));self.assertEqual(r['change_unit'],unit);self.assertEqual(r['scale'],scale)

    def test_ratio_common_dates_and_regime_change_with_inputs(self):
        c=capture([point('vix',20,'2026-10-16'),point('vix3m',25,'2026-10-16'),
                   point('vix',30,'2026-10-23'),point('vix3m',20,'2026-10-23')])
        r=self.row(c,'vix_ratio');self.assertEqual(r['baseline']['value'],.8);self.assertEqual(r['end']['value'],1.5)
        self.assertAlmostEqual(r['change'],.7);self.assertEqual(r['regime_start'],'Contango');self.assertEqual(r['regime_end'],'Backwardation')
        self.assertEqual(len(r['regime_changes']),1)
        self.assertEqual([x['observation_date'] for x in r['end']['inputs']],['2026-10-23','2026-10-23'])
        self.assertTrue(all(x['source_url'] and x['response_sha256'] for x in r['end']['inputs']))

    def test_mismatched_vix_dates_never_make_week_baseline(self):
        c=capture([point('vix',20,'2026-10-16'),point('vix3m',25,'2026-10-15'),
                   point('vix',30,'2026-10-23'),point('vix3m',20,'2026-10-23')])
        r=self.row(c,'vix_ratio');self.assertEqual(r['status'],'INSUFFICIENT');self.assertIsNone(r['change'])
        self.assertIn('比较基准不足',weekly(c,[]))

    def test_week_fragment_marked_partial_not_whole_week(self):
        c=capture([point('sp500',100,'2026-10-21'),point('sp500',110,'2026-10-23')])
        self.assertEqual(self.row(c,'sp500')['status'],'PARTIAL_WEEK')
        self.assertIn('仅有周内片段',weekly(c,[]))

    def test_historical_points_keep_stale_label_but_are_usable_as_history(self):
        c=capture([point('sp500',100,'2026-10-16',quality='STALE'),point('sp500',110,'2026-10-23')])
        r=self.row(c,'sp500');self.assertEqual(r['status'],'OK');self.assertEqual(r['baseline']['quality'],'STALE')

    def test_missing_current_source_marks_archived_end_not_current_observation(self):
        old=capture([point('vix',20,'2026-10-16'),point('vix',22,'2026-10-23')],at=datetime(2026,10,24,3,tzinfo=UTC))
        c=capture([],{'vix':'MISSING'});r=self.row(c,'vix',[old])
        self.assertEqual(r['source_status_current'],'MISSING');self.assertEqual(r['end']['observation_date'],'2026-10-23')
        self.assertIn('末点可能来自历史档案',weekly(c,[old]))

    def test_newest_capture_revision_wins_without_mutating_sources(self):
        old=capture([point('sp500',100,'2026-10-16'),point('sp500',105,'2026-10-23')],at=datetime(2026,10,24,3,tzinfo=UTC))
        c=capture([point('sp500',110,'2026-10-23')]);before=copy.deepcopy([old,c]);r=self.row(c,'sp500',[old])
        self.assertAlmostEqual(r['change'],10);self.assertEqual([old,c],before)

    def test_zero_price_baseline_not_fabricated_percent_return(self):
        c=capture([point('sp500',0,'2026-10-16'),point('sp500',10,'2026-10-23')])
        r=self.row(c,'sp500');self.assertEqual(r['status'],'ZERO_BASELINE');self.assertIsNone(r['change'])

    def test_partial_srf_excluded_from_full_day_comparisons(self):
        c=capture([point('srf_usd',5e9,'2026-10-16'),point('srf_usd',1e6,'2026-10-23',complete=False)])
        r=self.row(c,'srf_usd');self.assertIsNone(r['change'])

    def test_no_future_or_unverified_points_in_trend(self):
        c=capture([point('sp500',100,'2026-10-16'),point('sp500',110,'2026-10-23',quality='UNVERIFIED'),point('sp500',999,'2026-10-25')])
        self.assertIsNone(self.row(c,'sp500')['change'])


class ProviderShapeTests(unittest.TestCase):
    def test_duplicate_daily_index_date_is_missing_not_silent_overwrite(self):
        b=(FIX/'vix.txt').read_bytes();body=b+b.splitlines()[-1]+b'\n'
        spec=next(s for s in registry(NOW) if s['id']=='vix')
        r=collect_one(spec,NOW,lambda url:(body,{'response_sha256':digest(body),'fetched_at_utc':NOW.isoformat()}))
        self.assertEqual(r['status'],'MISSING');self.assertIn('Duplicate indicator',r['error'])

    def test_yahoo_timestamp_and_close_arrays_must_match(self):
        js={'chart':{'error':None,'result':[{'meta':{'exchangeTimezoneName':'UTC'},'timestamp':[1,2],'indicators':{'quote':[{'close':[100]}]}}]}}
        with self.assertRaisesRegex(ValueError,'length mismatch'):parsers.parse_yahoo(encoded(js),NOW)
