import json
import os
import time
from concurrent.futures import ThreadPoolExecutor, as_completed
from datetime import datetime, timedelta
from urllib.error import HTTPError, URLError
from urllib.parse import urlencode, quote
from urllib.request import Request, urlopen
from . import parsers
from .core import UTC, stamp, digest, assess_date, observation, ET


def registry(now):
    def s(key,url,parser,age=4,kind='primary',note=''):
        return dict(id=key,url=url,parser=parser,max_age_days=age,kind=kind,note=note)
    src=[
      s('aaii','https://www.aaii.com/sentimentsurvey','aaii',10,note='Weekly. Full historical member dataset not required.'),
      s('cnn','https://production.dataviz.cnn.io/index/fearandgreed/graphdata','cnn',4,note='Official CNN origin; undocumented endpoint may refuse requests. No access-control bypass.'),
      s('vix','https://cdn.cboe.com/api/global/us_indices/daily_prices/VIX_History.csv','cboe',4),
      s('vix3m','https://cdn.cboe.com/api/global/us_indices/daily_prices/VIX3M_History.csv','cboe',4),
      s('crypto','https://api.alternative.me/fng/?limit=31&format=json','crypto',1),
      s('srf','https://markets.newyorkfed.org/api/rp/repo/all/results/lastTwoWeeks.json','srf',4),
      s('treasury','https://www.treasurydirect.gov/TA_WS/securities/announced?format=json&days=30','auctions',10,note='Official 30-day announcements endpoint; client filters auction dates. Unannounced future supply unknown; tail needs WI yield.'),
      s('ici','https://www.ici.org/research/stats/mmf','ici',10,note='USD billions table. Asset change is not net flow.'),
      s('bls','https://www.bls.gov/schedule/news_release/bls.ics','bls'),
      s('bea','https://www.bea.gov/news/schedule','bea'),
      s('fomc','https://www.federalreserve.gov/monetarypolicy/fomccalendars.htm','fomc'),
      s('sec','https://www.sec.gov/news/pressreleases.rss','rss'),
      s('cftc','https://www.cftc.gov/RSS/RSSGP/rssgp.xml','rss'),
      s('fed','https://www.federalreserve.gov/feeds/press_all.xml','rss'),
      s('congress','https://www.govinfo.gov/rss/bills.xml','rss',note='Official GPO bill publications, not comprehensive vote/amendment monitoring.'),
      s('whitehouse','https://www.whitehouse.gov/presidential-actions/feed/','rss'),
      s('treasury_news','https://home.treasury.gov/news/press-releases','treasury_news',note='Official press-release index; linked release pages are the primary references.'),
      s('federal_register','https://www.federalregister.gov/api/v1/documents.json?'+urlencode({'conditions[term]':'cryptocurrency OR stablecoin OR "digital asset" OR tokenization','conditions[publication_date][gte]':(now.date()-timedelta(days=7)).isoformat(),'per_page':'100','order':'newest'}),'federal_register',note='Rule/Proposed Rule/Notice types authoritative; effective_on may be absent.'),
    ]
    for key,symbol in [('sp500','^GSPC'),('nasdaq','^IXIC'),('us10y','^TNX'),('dxy','DX-Y.NYB'),('wti','CL=F'),('gold','GC=F'),('btc','BTC-USD')]:
        src.append(s(key,'https://query1.finance.yahoo.com/v8/finance/chart/'+quote(symbol,safe='')+'?range=1mo&interval=1d','yahoo',2 if key=='btc' else 4,'secondary',
                     'Free Yahoo chart; futures for WTI/gold. May be intraday/delayed, never assert official close.'))
    return src


def download(url, timeout=20, attempts=2, opener=urlopen):
    for attempt in range(attempts):
        try:
            req=Request(url,headers={'User-Agent':'MarketReports/1.0 (+https://github.com/yydsdefi-cmyk/COMEX-Gold-Tracker)','Accept':'application/json,text/csv,text/html,application/xml;q=0.9,*/*;q=0.8'})
            if url.startswith('https://api.github.com/') and os.environ.get('GITHUB_TOKEN'):
                req.add_header('Authorization', 'Bearer '+os.environ['GITHUB_TOKEN'])
            with opener(req,timeout=timeout) as r:
                body=r.read(6*1024*1024+1)
                if len(body)>6*1024*1024:
                    raise ValueError('Response over size limit')
                return body, {'http_status':r.status,'response_sha256':digest(body),'response_bytes':len(body),
                              'http_last_modified':r.headers.get('Last-Modified'),'http_date':r.headers.get('Date'),
                              'fetched_at_utc':stamp(datetime.now(UTC)),'final_url':r.url,'attempts':attempt+1}
        except HTTPError as e:
            if e.code not in (429,500,502,503,504) or attempt+1 == attempts:
                raise
        except (URLError,TimeoutError,OSError):
            if attempt+1 == attempts:
                raise
        time.sleep(min(2**attempt,4))
    raise RuntimeError('Download exhausted')


def collect_one(spec, now, downloader=download):
    receipt = {**spec,'fetched_at_utc':stamp(now),'status':'MISSING','observations':[],'details':{}}
    try:
        body,meta=downloader(spec['url'])
        receipt.update(meta)
        fn=getattr(parsers,'parse_'+spec['parser'])
        args={'metric':spec['id']} if spec['parser'] in ('cboe','yahoo') else {}
        obs,details=fn(body,now,**args)
        if spec['id']=='federal_register':
            for item in details.get('items',[])[:20]:
                detail_url='https://www.federalregister.gov/api/v1/documents/'+item['document_number']+'.json'
                try:
                    detail_body,detail_meta=downloader(detail_url)
                    document=json.loads(detail_body)
                    if document['document_number']!=item['document_number'] or document['type']!=item['legal_status']:
                        raise ValueError('Federal Register detail/search mismatch')
                    item.update(effective_date=document.get('effective_on'),comments_close_on=document.get('comments_close_on'),
                                official_pdf=document.get('pdf_url'),action=document.get('action'),
                                detail_response_sha256=detail_meta['response_sha256'],detail_fetched_at_utc=detail_meta['fetched_at_utc'])
                except Exception as exc:
                    item['detail_error']=type(exc).__name__+': '+str(exc)[:200]
        for o in obs:
            o.update(source=spec['id'],source_url=spec['url'],response_sha256=meta['response_sha256'],fetched_at_utc=meta['fetched_at_utc'])
            o['quality']='SCHEDULED' if o.get('scheduled') else assess_date(o['observation_date'],now,spec['max_age_days'])
            if o['quality']=='FUTURE':
                raise ValueError('Future observed value')
        receipt.update(observations=obs,details=details,status='OK')
        if obs:
            latest=max(o['observation_date'] for o in obs if not o.get('scheduled')) if any(not o.get('scheduled') for o in obs) else None
            if latest and assess_date(latest,now,spec['max_age_days'])!='OK':
                receipt['status']='STALE'
        if spec['id']=='srf' and obs and not max(obs,key=lambda o:o['observation_date'])['complete']:
            receipt['status']='PROVISIONAL'
        if spec['id']=='federal_register' and not details['coverage_complete']:
            receipt['status']='INCOMPLETE'
    except Exception as e:
        receipt.update(status='MISSING',error=type(e).__name__+': '+str(e)[:350],observations=[],details={})
    return receipt


def collect(now, downloader=download):
    receipts=[]
    with ThreadPoolExecutor(max_workers=4) as pool:
        jobs=[pool.submit(collect_one,s,now,downloader) for s in registry(now)]
        for f in as_completed(jobs):
            r=f.result()
            print(json.dumps({'source':r['id'],'status':r['status'],'error':r.get('error')},ensure_ascii=False),flush=True)
            receipts.append(r)
    return sorted(receipts,key=lambda x:x['id'])
