"""Strict, fixture-tested adapters. Missing dates/units fail closed."""
import csv
import io
import json
import re
import xml.etree.ElementTree as XML
from datetime import datetime, timedelta
from email.utils import parsedate_to_datetime
from html import unescape
from zoneinfo import ZoneInfo
from .core import ET, MYT, UTC, number, observation, srf_level


def text(html):
    return re.sub(r'\s+', ' ', unescape(re.sub('<[^>]+>', ' ', html))).strip()


def parse_aaii(body, now):
    s = body.decode('utf-8-sig')
    ending = re.search(r'Week ending\s+([A-Z][a-z]+ \d{1,2}, \d{4})', s, re.I)
    if not ending:
        raise ValueError('AAII week ending missing')
    day = datetime.strptime(ending[1], '%B %d, %Y').date().isoformat()
    vals = {}
    for name, css in [('bull','bull'),('neutral','neut'),('bear','bear')]:
        m = re.search(r'ssv2-snum\s+' + css + r'[^>]*>\s*([\d.]+)%', s)
        if not m and name == 'neutral':
            m = re.search(r'ssv2-snum\s+neutral[^>]*>\s*([\d.]+)%', s)
        if not m:
            raise ValueError('AAII ' + name + ' missing')
        vals[name] = number(m[1])
    if abs(sum(vals.values()) - 100) > .3 or any(not 0 <= v <= 100 for v in vals.values()):
        raise ValueError('AAII composition invalid')
    # dateModified is NOT the survey publication date.
    obs = [observation('aaii_'+k,v,day,'percent') for k,v in vals.items()]
    obs.append(observation('aaii_spread', vals['bull']-vals['bear'],day,'percentage_points'))
    for hday,bull,neutral,bear in re.findall(r'<div class="date">(\d{1,2}/\d{1,2}/\d{4})</div>.*?class="bar bullish"[^>]*>([\d.]+)%.*?class="bar neutral"[^>]*>([\d.]+)%.*?class="bar bearish"[^>]*>([\d.]+)%',s,re.S):
        hd=datetime.strptime(hday,'%m/%d/%Y').date().isoformat()
        if hd==day:continue
        v=[number(x) for x in (bull,neutral,bear)]
        if abs(sum(v)-100)>.3 or any(not 0<=x<=100 for x in v):raise ValueError('Historical AAII composition invalid')
        obs += [observation('aaii_'+k,x,hd,'percent') for k,x in zip(['bull','neutral','bear'],v)]
        obs.append(observation('aaii_spread',v[0]-v[2],hd,'percentage_points'))
    return obs, {'week_ending':day,'publication_note':'发布日期未提供；不以网页dateModified代替'}


def parse_cboe(body, now, metric='vix'):
    rows = list(csv.DictReader(io.StringIO(body.decode('utf-8-sig'))))
    out = []
    for r in rows[-90:]:
        date = datetime.strptime(r['DATE'].strip(), '%m/%d/%Y').date().isoformat()
        v=number(r['CLOSE'])
        if v<=0:raise ValueError('Non-positive Cboe volatility index')
        out.append(observation(metric,v,date,'index'))
    if not out:
        raise ValueError('Empty Cboe CSV')
    return out, {'publication_note':'官方日收盘序列未提供逐行发布时间'}


def parse_crypto(body, now):
    js = json.loads(body)
    if js.get('metadata',{}).get('error'):
        raise ValueError('Alternative.me error')
    obs = []
    for row in js['data']:
        d = datetime.fromtimestamp(int(row['timestamp']), UTC)
        value = number(row['value'])
        if not 0 <= value <= 100:
            raise ValueError('F&G outside [0,100]')
        obs.append(observation('crypto_fg',value,d.date().isoformat(),'index',
                               provider_timestamp=d.isoformat(),classification=row['value_classification']))
    if not obs:
        raise ValueError('Empty Alternative.me response')
    return obs, {'date_basis':'provider daily timestamp UTC; not inferred MYT date',
                 'publication_note':'Daily provider timestamp retained separately; independent publication time not supplied'}


def parse_cnn(body, now):
    js = json.loads(body)['fear_and_greed']
    value = number(js['score'])
    if not 0 <= value <= 100:
        raise ValueError('CNN score outside range')
    raw_stamp=js['timestamp']
    d = datetime.fromtimestamp(raw_stamp/(1000 if raw_stamp>1e11 else 1),UTC) if isinstance(raw_stamp,(float,int)) else datetime.fromisoformat(raw_stamp.replace('Z','+00:00'))
    if d.tzinfo is None:
        raise ValueError('CNN timestamp lacks zone')
    return [observation('cnn_fg',value,d.date().isoformat(),'index',None,provider_updated_at=d.isoformat(),classification=js['rating'])], {'publication_note':'provider timestamp retained as update time; publication time not separately provided'}


def parse_srf(body, now):
    rows = json.loads(body)['repo']['operations']
    accepted, excluded, unknown, seen = {}, [], [], set()
    for r in rows:
        uid = r['operationId']
        if uid in seen:
            raise ValueError('Duplicate NYFed operation: '+uid)
        seen.add(uid)
        note = text(r.get('note',''))
        if re.search(r'\bsmall[-\s]+value\b|\bSVE\b|\btest(?:ing)?\b|\bexercise(?:s)?\b',note,re.I):
            excluded.append({'id':uid,'date':r['operationDate'],'amount':r.get('totalAmtAccepted'),'reason':note})
            continue
        if r.get('auctionStatus') != 'Results':
            continue
        if r.get('operationType') != 'Repo' or r.get('term') != 'Overnight' or r.get('operationMethod') != 'Full Allotment':
            unknown.append({'id':uid,'date':r['operationDate'],'type':r.get('operationType'),
                            'term':r.get('term'),'method':r.get('operationMethod'),'amount':r.get('totalAmtAccepted')})
            continue
        day = r['operationDate']
        if datetime.strptime(day,'%Y-%m-%d').date()>now.astimezone(ET).date():
            raise ValueError('Future NYFed operation date')
        amt = number(r['totalAmtAccepted'])
        if amt < 0 or abs(amt-sum(number(d['amtAccepted']) for d in r['details'])) > .01:
            raise ValueError('NYFed totals mismatch')
        updated=datetime.fromisoformat(r['lastUpdated'].replace('Z','+00:00'))
        if updated.tzinfo is None:updated=updated.replace(tzinfo=ET)
        if updated>now+timedelta(minutes=5):raise ValueError('Future NYFed update')
        stamp=updated.astimezone(UTC).isoformat()
        entry = accepted.setdefault(day, {'usd':0,'operations':[],'published':stamp})
        entry['usd'] += amt
        entry['published'] = max(stamp,entry['published'])
        entry['operations'].append({'id':uid,'usd':amt,'releaseTime':r['releaseTime'],'closeTime':r['closeTime']})
    if not accepted:
        raise ValueError('No regular overnight SRF operations')
    expected={('08:15','08:30'),('13:30','13:45')}
    obs=[]
    for d,r in sorted(accepted.items()):
        slots={(o['releaseTime'],o['closeTime']) for o in r['operations']}
        complete=len(r['operations'])==2 and slots==expected and not any(x['date']==d for x in unknown)
        obs.append(observation('srf_usd',r['usd'],d,'USD',provider_updated_at=r['published'],
            level=srf_level(r['usd']),operation_count=len(r['operations']),complete=complete))
    return obs, {'days':accepted,'excluded_exercises':excluded,'unclassified_operations':unknown,
                 'completion_rule':'exactly one 08:15-08:30 and one 13:30-13:45 ET regular operation; no unclassified same-day rows; schedule changes require review',
                 'publication_note':'lastUpdated is a revision timestamp; independent first publication time not supplied',
                 'schedule_reference':'https://www.newyorkfed.org/markets/opolicy/operating_policy_251210'}


def parse_auctions(body, now):
    rows = json.loads(body)
    if not isinstance(rows,list):
        raise ValueError('Treasury response not a list')
    out,obs,seen = [],[],set()
    for r in rows:
        rawday = r.get('auctionDate') or r.get('competitiveAuctionCloseDate')
        if not rawday:
            continue
        day = rawday[:10]
        if not now.date()-timedelta(days=10) <= datetime.fromisoformat(day).date() <= now.date()+timedelta(days=8):
            continue
        uid = (r.get('cusip'),day)
        if uid in seen:
            raise ValueError('Duplicate Treasury auction')
        seen.add(uid)
        amount = number(r['offeringAmount']) if r.get('offeringAmount') else None
        kind = r.get('securityType') or r.get('type')
        if r.get('floatingRate')=='Yes':kind='FRN'
        elif r.get('inflationProtected')=='Yes':kind='TIPS'
        if kind not in ('Bill','Note','Bond','TIPS','FRN'):
            raise ValueError('Unrecognized Treasury type')
        closing = r.get('competitiveClosingTime') or r.get('competitiveAuctionCloseTime')
        close_myt = None
        if closing:
            try:
                clock=datetime.strptime(closing,'%I:%M %p').time() if 'M' in closing.upper() else datetime.fromisoformat(day+'T'+closing).time()
                dt = datetime.combine(datetime.fromisoformat(day).date(),clock,tzinfo=ET)
                close_myt = dt.astimezone(MYT).isoformat()
            except ValueError:
                pass
        item = {'date':day,'type':kind,'term':r.get('securityTerm'), 'cusip':r.get('cusip'),
                'offering_usd':amount,'announcement_date':r.get('announcementDate','')[:10] or None,
                'updated':r.get('updatedTimestamp'),'close_myt':close_myt,
                'bid_to_cover':number(r['bidToCoverRatio']) if r.get('bidToCoverRatio') else None,
                'high_yield':number(r['highYield']) if r.get('highYield') else None,
                'tail_bp':None,'tail_note':'缺少可复核的拍卖前when-issued收益率，不计算tail/stop-through'}
        if item['announcement_date'] and item['announcement_date'] > now.astimezone(ET).date().isoformat():
            continue
        out.append(item)
        if amount is not None:
            obs.append(observation('treasury_offering_'+str(r.get('cusip')),amount,day,'USD',item['announcement_date'],scheduled=True))
    return obs, {'auctions':sorted(out,key=lambda x:(x['date'],x['term'] or '')),
                 'coverage':'only announced offerings; unpublished future amounts unknown; includes TIPS/FRN in coupon bucket'}


def parse_ici(body, now):
    s = body.decode('utf-8-sig')
    # Scope to the article, excluding navigation dates and unrelated news.
    start = s.find('—Total money market fund assets')
    if start < 0:
        start = s.find('Total money market fund assets')
    if start < 0:
        raise ValueError('ICI article missing')
    fragment = s[max(0,start-400):]
    dates = re.findall(r'<strong>\s*(\d{1,2}/\d{1,2}/\d{4})\s*</strong>', fragment)
    if not dates:
        raise ValueError('ICI table date missing')
    day = datetime.strptime(dates[0],'%m/%d/%Y').date().isoformat()
    total = re.search(r'<tr>\s*<td>\s*<span>\s*<strong>Total.*?</tr>',fragment,re.S)
    if not total:
        raise ValueError('ICI Total row missing')
    cells = [text(c) for c in re.findall(r'<td[^>]*>(.*?)</td>',total[0],re.S)]
    vals = [number(x) for x in cells[1:]]
    if len(vals) < 3 or abs(vals[0]-vals[1]-vals[2]) > .03:
        raise ValueError('ICI table arithmetic mismatch')
    # Table units must be explicitly stated, never infer billions from magnitude.
    if not re.search(r'billions|billions of dollars',text(s[max(0,start-500):start+10000]),re.I):
        raise ValueError('ICI billions unit missing')
    p = re.search(r'article-subheading.*?<time datetime="([^"]+)"', s,re.S)
    pub = p[1] if p else None
    return [observation('mmf_assets_usd',vals[0]*1e9,day,'USD',pub),
            observation('mmf_weekly_asset_change_usd',vals[2]*1e9,day,'USD',pub)], {
                'net_flow_usd':None,'note':'周资产变化不等于精确净流量；高资产不是必然回流股市的资金',
                'three_month_trend':'积累连续已核验周度资料后计算，当前不足'}


def parse_yahoo(body, now, metric='sp500'):
    js = json.loads(body)['chart']
    if js.get('error'):
        raise ValueError('Yahoo chart error')
    js = js['result'][0]
    closes = js['indicators']['quote'][0]['close']
    if len(js.get('timestamp',[]))!=len(closes):raise ValueError('Yahoo timestamp/close length mismatch')
    quote_zone=ZoneInfo(js['meta']['exchangeTimezoneName'])
    obs = []
    for t,v in zip(js.get('timestamp',[]),closes):
        if v is None:
            continue
        dt = datetime.fromtimestamp(t,UTC)
        obs.append(observation(metric,v,dt.astimezone(quote_zone).date().isoformat(),
                               'percent_yield' if metric=='us10y' else js['meta'].get('currency','USD'),
                               None,quote_timestamp=dt.isoformat(),basis='Yahoo daily bars in provider exchangeTimezoneName; latest bar may be intraday',observation_timezone=str(quote_zone)))
    if not obs:
        raise ValueError('Yahoo has no prices')
    return obs, {'secondary_source':True,'not_guaranteed_official_close':True}


def parse_rss(body, now):
    root = XML.fromstring(body)
    from .regulation import KEY
    items = []
    for e in root.findall('.//item'):
        title = text(e.findtext('title') or '')
        link = e.findtext('link') or ''
        dt = e.findtext('pubDate') or e.findtext('{http://purl.org/dc/elements/1.1/}date')
        if not title or not link.startswith('https://') or not dt:
            continue
        try:
            pub = parsedate_to_datetime(dt)
        except (ValueError,TypeError):
            pub = datetime.fromisoformat(dt.replace('Z','+00:00'))
        if pub.tzinfo is None:
            raise ValueError('RSS publication time lacks zone')
        if now-timedelta(days=8) <= pub <= now:
            items.append({'title':title,'url':link,'publication_date':pub.isoformat(),
                          'event_date':None,'legal_status':'UNRESOLVED','effective_date':None,
                          'topic_signal':bool(KEY.search(title+' '+text(e.findtext('description') or ''))),
                          'summary':text(e.findtext('description') or '')[:1200],
                          'review_candidate':bool(re.search(r'examination priorities',title,re.I)),
                          'note':'官方公告；标题或RSS摘要主题筛选不等于法律效力核验'})
    from .regulation import status_from_title,topics
    for item in items:
        item['legal_status']=status_from_title(item['title'])
        item['topics']=topics(item['title']+' '+item.get('summary',''))
        item['verified_scope']='official feed title/summary; linked legal body not examined'
    return [], {'items':items,'coverage':'feed window only; no items does not establish no developments'}


def parse_federal_register(body, now):
    js=json.loads(body)
    items=[]
    for r in js['results']:
        day=r['publication_date']
        if not now.date()-timedelta(days=7) <= datetime.fromisoformat(day).date() <= now.date():
            continue
        items.append({'title':r['title'],'url':r['html_url'],'publication_date':day,
                      'event_date':None,'legal_status':r['type'],'effective_date':r.get('effective_on'),
                      'document_number':r['document_number'], 'note':'Federal Register文种；Rule不自动等于已生效'})
    return [], {'items':items,'count':js['count'],'total_pages':js.get('total_pages'),
                'coverage_complete':js.get('total_pages',1)<=1}


def parse_bls(body, now):
    s=body.decode('utf-8-sig').replace('\r\n ', '').replace('\n ', '')
    if 'BEGIN:VCALENDAR' not in s or 'END:VCALENDAR' not in s or 'BEGIN:VEVENT' not in s:
        raise ValueError('BLS response is not a populated iCalendar')
    items=[];all_dates=[]
    for chunk in s.split('BEGIN:VEVENT')[1:]:
        m=re.search(r'DTSTART(?:;TZID=([^:\r\n]+))?:(\d{8}T\d{6}Z?)',chunk)
        title=re.search(r'SUMMARY:(.+)',chunk)
        if not m or not title:
            continue
        raw=m[2]
        if not raw.endswith('Z') and m[1] not in ('US-Eastern','America/New_York'):
            raise ValueError('BLS timezone unrecognized')
        dt=datetime.strptime(raw.rstrip('Z'),'%Y%m%dT%H%M%S')
        dt=dt.replace(tzinfo=UTC if raw.endswith('Z') else ET)
        all_dates.append(dt.astimezone(MYT).date().isoformat())
        if now-timedelta(days=7)<=dt<=now+timedelta(days=8):
            items.append({'name':title[1].strip(),'at_myt':dt.astimezone(MYT).isoformat(),'source':'BLS',
                          'tier1':bool(re.search('Consumer Price|Producer Price|Employment Situation|Employment Cost',title[1],re.I))})
    if not all_dates:raise ValueError('BLS calendar has no dated events')
    return [], {'events':items,'calendar_covers_through':max(all_dates),'coverage':'BLS only; FOMC and BEA processed separately'}


def parse_bea(body, now):
    s=body.decode('utf-8-sig')
    events=[]
    # Separate year tables prevent silently assigning next year's releases to this year.
    for table in re.findall(r'<table\b.*?</table>',s,re.S):
        year=re.search(r'Year (\d{4})',table)
        if not year:
            continue
        for row in re.findall(r'<tr\b.*?</tr>',table,re.S):
            day=re.search(r'class="release-date">([^<]+)',row)
            clock=re.search(r'class="text-muted">([^<]+)',row)
            title=re.search(r'<td[^>]*class="release-title[^>]*>(.*?)</td>',row,re.S)
            if not all([day,clock,title]):
                continue
            dt=datetime.strptime(day[1]+' '+year[1]+' '+clock[1],'%B %d %Y %I:%M %p').replace(tzinfo=ET)
            name=text(title[1])
            if now-timedelta(days=7)<=dt<=now+timedelta(days=8):
                events.append({'name':name,'at_myt':dt.astimezone(MYT).isoformat(),'source':'BEA',
                               'tier1':bool(re.search('GDP|Gross Domestic|Personal Income',name,re.I))})
    if not re.search(r'Year \d{4}',s):
        raise ValueError('BEA schedule structure changed')
    return [], {'events':events}


def parse_fomc(body, now):
    s=body.decode('utf-8-sig')
    sections=re.split(r'(\d{4}) FOMC Meetings',s)
    if len(sections)<3:
        raise ValueError('FOMC year sections missing')
    events=[]
    for idx in range(1,len(sections),2):
        year=sections[idx]
        if idx+1 >= len(sections):
            continue
        for chunk in sections[idx+1].split('class="row fomc-meeting')[1:]:
            month=re.search(r'fomc-meeting__month[^>]*>\s*<strong>([^<]+)',chunk)
            days=re.search(r'fomc-meeting__date[^>]*>([^<]+)',chunk)
            if not month or not days or '/' in month[1]:
                continue
            nums=re.findall(r'\d+',days[1])
            if not nums:
                continue
            dt=datetime.strptime(month[1].strip()+' '+nums[-1]+' '+year,'%B %d %Y').replace(hour=14,tzinfo=ET)
            if now-timedelta(days=7)<=dt<=now+timedelta(days=8):
                events.append({'name':'FOMC 利率决定（14:00 ET标准发布时间；临时变更须核验）',
                               'at_myt':dt.astimezone(MYT).isoformat(),'source':'Fed calendar','tier1':True,
                               'time_basis':'meeting end date verified; 14:00 ET standing convention, not date-specific announcement'})
    return [], {'events':events}


def parse_treasury_news(body, now):
    s=body.decode('utf-8-sig')
    items=[]
    # Treasury's public index currently permits unquoted HTML attributes.
    rows=re.findall(r'<time\b[^>]*datetime=["\']?([^\s>"\']+)[^>]*>.*?</time>(.*?)(?=<time\b|$)',s,re.S)
    for raw,chunk in rows:
        pub=datetime.fromisoformat(raw.replace('Z','+00:00'))
        if pub.tzinfo is None:raise ValueError('Treasury date has no zone')
        if not now-timedelta(days=8)<=pub<=now:continue
        link=re.search(r'<a\b[^>]*href=["\']?(/news/press-releases/[a-z]+\d+/?)["\']?[^>]*>(.*?)</a>',chunk,re.S)
        if link:
            items.append({'title':text(link[2]),'url':'https://home.treasury.gov'+link[1],
                          'publication_date':pub.isoforma…2216 tokens truncated…   for n in range(100):
              runs=api('/actions/workflows/market-reports.yml/runs?event=workflow_dispatch&per_page=5')['workflow_runs']
              candidates=[r for r in runs if datetime.fromisoformat(r['created_at'].replace('Z','+00:00'))>=started-timedelta(seconds=2)]
              if candidates:
                  selected=candidates[0]
                  print('Manual dispatch run',selected['id'],selected['status'],selected.get('conclusion'),flush=True)
                  if selected['status']=='completed':break
              time.sleep(5)
          assert selected and selected['status']=='completed', 'Manual dispatch did not complete in time'
          evidence={'dispatch_http':204,'report_input':'both','run_id':selected['id'],'run_url':selected['html_url'],'event':selected['event'],'conclusion':selected['conclusion'],'verified_at_utc':datetime.now(timezone.utc).isoformat()}
          open('evidence/manual-dispatch.json','w').write(json.dumps(evidence,indent=2))
          assert selected['conclusion']=='success',evidence
          PY
      - name: Read persisted archive and independently audit real weekly calculations
        run: |
          git fetch origin main
          git checkout --detach FETCH_HEAD
          python3 -m market_reports.audit > evidence/numeric-audit.json
      - name: Install official browser test package for one-time mobile QA
        run: |
          npm install --no-save playwright@1.62.1
          npx playwright install --with-deps chromium
      - name: Verify public Pages, mobile layout, archives, and original Gold endpoint
        run: |
          node <<'JS'
          const fs=require('fs');
          const {chromium}=require('playwright');
          const base='https://yydsdefi-cmyk.github.io/COMEX-Gold-Tracker/';
          (async()=>{
            const b=await chromium.launch({headless:true});const evidence=[];
            for(const width of [360,390]){
              const p=await b.newPage({viewport:{width,height:844},deviceScaleFactor:1});
              for(const name of ['index','daily','weekly']){
                const response=await p.goto(base+'market/'+name+'.html',{waitUntil:'networkidle',timeout:45000});
                if(response.status()!==200)throw new Error(name+' HTTP '+response.status());
                const layout=await p.evaluate(()=>({viewport:innerWidth,body:document.body.scrollWidth,title:document.title,details:document.querySelectorAll('details').length}));
                if(layout.body>width+1)throw new Error('Horizontal body overflow '+JSON.stringify(layout));
                if(name==='daily' && !await p.getByText('7项总览',{exact:true}).count())throw new Error('Daily summary missing');
                if(name==='weekly' && !await p.getByText(/Crypto Regulatory Timeline/).count())throw new Error('Weekly timeline missing');
                if(name==='daily'){
                  await p.getByText('COMEX Gold',{exact:true}).click();
                  if(!await p.getByText(/Registered Ratio/).isVisible())throw new Error('COMEX detail does not expand');
                }
                await p.screenshot({path:'evidence/'+name+'-'+width+'.png',fullPage:true});
                evidence.push({name,width,status:response.status(),...layout});
              }
              await p.close();
            }
            const clockPage=await b.newPage({viewport:{width:390,height:844}});
            await clockPage.addInitScript(()=>{Date.now=()=>Date.parse('2026-10-25T04:00:00Z');});
            await clockPage.goto(base+'market/index.html',{waitUntil:'networkidle',timeout:45000});
            const clocks=await clockPage.locator('.report-clock').evaluateAll(els=>els.map(el=>({kind:el.dataset.kind,state:el.dataset.state,text:el.textContent})));
            if(clocks.find(x=>x.kind==='daily')?.state!=='OVERDUE'||clocks.find(x=>x.kind==='weekly')?.state!=='CURRENT')throw Error('Independent report freshness failed '+JSON.stringify(clocks));
            const cases=[
              ['daily','2026-10-24','2026-10-25T00:00:00Z','PENDING'],
              ['daily','2026-10-24','2026-10-25T04:00:00Z','OVERDUE'],
              ['weekly','2026-10-24','2026-10-31T01:59:59Z','CURRENT'],
              ['weekly','2026-10-24','2026-10-31T02:00:00Z','PENDING'],
              ['weekly','2026-10-24','2026-10-31T06:00:00Z','OVERDUE'],
              ['daily','2026-11-01','2026-11-01T00:00:00Z','CURRENT']
            ];
            const clockResults=await clockPage.evaluate(cases=>cases.map(([kind,date,at,want])=>({kind,date,at,want,...window.MarketReportClock.assess(kind,date,null,Date.parse(at))})),cases);
            const earlyPreview=await clockPage.evaluate(()=>window.MarketReportClock.assess('daily','2026-10-25','2026-10-24T23:30:00Z',Date.parse('2026-10-25T00:00:00Z')));
            if(earlyPreview.state!=='PENDING')throw Error('Early manual preview accepted as scheduled publication');
            clockResults.push({kind:'daily',date:'2026-10-25',at:'2026-10-25T00:00:00Z',want:'PENDING',...earlyPreview});
            if(clockResults.some(x=>x.state!==x.want))throw Error('Actual browser clock boundaries failed '+JSON.stringify(clockResults));
            fs.writeFileSync('evidence/clock-pages.json',JSON.stringify({simulated_at:'2026-10-25T04:00:00Z',clocks,checks:clockResults},null,2));
            await clockPage.screenshot({path:'evidence/independent-freshness-390.png',fullPage:true});
            await clockPage.close();
            const p=await b.newPage();
            for(const path of ['latest.json','history.csv','market/daily.json','market/weekly.json','market/history.csv','market/source_registry.json','market/quality.json']){
              const r=await p.request.get(base+path);if(r.status()!==200)throw new Error(path+' HTTP '+r.status());
              evidence.push({path,status:r.status()});
            }
            const daily=await (await p.request.get(base+'market/daily.json')).json();
            const weekly=await (await p.request.get(base+'market/weekly.json')).json();
            if(daily.kind!=='daily'||weekly.kind!=='weekly')throw new Error('Wrong report types');
            if(daily.capture_id!==weekly.capture_id)throw new Error('Manual both did not share an identical capture');
            if(daily.method_version!=='1.3.0'||weekly.capture.schema_version!==3)throw Error('Wrong report method/schema');
            const nyfed=weekly.capture.sources.find(x=>x.id==='nyfed_calendar');
            if(nyfed?.status!=='OK')throw Error('Supplementary official calendar not verified');
            const upcoming=weekly.analysis.upcoming_tier1;
            if(upcoming.filter(x=>x.event_id==='eci').length!==1)throw Error('Employment Cost Index missing or duplicated');
            for(const id of ['gdp','pce']){
              const rows=upcoming.filter(x=>x.event_id===id);
              if(rows.length!==1||rows[0].evidence.length<2)throw Error('Primary/NYFed corroboration not preserved '+id);
            }
            const audit=JSON.parse(fs.readFileSync('evidence/numeric-audit.json','utf8'));
            if(audit.failed!==0||audit.verified<10||audit.status!=='PASS_CALCULABLE_ONLY')throw Error('Independent live arithmetic did not pass');
            fs.writeFileSync('evidence/source-calendar-checks.json',JSON.stringify({source:nyfed.id,status:nyfed.status,events:upcoming.map(x=>({id:x.event_id,at_myt:x.at_myt,evidence:x.evidence})),numeric_verified:audit.verified,not_calculable:audit.not_calculable},null,2));
            fs.writeFileSync('evidence/mobile-pages.json',JSON.stringify({checks:evidence,capture_id:daily.capture_id,quality:daily.quality.acceptance},null,2));
            console.log(JSON.stringify({checks:evidence,quality:daily.quality.acceptance}));
            await b.close();
          })().catch(e=>{console.error(e);process.exit(1)});
          JS
      - name: Retain acceptance evidence for one day
        if: always()
        uses: actions/upload-artifact@ea165f8d65b6e75b540449e92b4886f43607fa02 # v4
        with:
          name: market-migration-acceptance
          path: evidence
          retention-days: 1

# Final renderer and date-boundary acceptance revision 2.
# Final provider-timezone acceptance revision 3.
# v1.1 regulatory coverage and incident-handler acceptance.

# v1.2 independent report freshness and archive-linkage acceptance.

# v1.2 final early-manual-preview boundary acceptance.

# v1.3 official supplementary calendar, independent arithmetic and bounded Pages acceptance.
