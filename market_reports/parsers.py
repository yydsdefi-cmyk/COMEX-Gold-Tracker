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
                          'publication_date':pub.isoformat(),'event_date':None,'legal_status':'UNRESOLVED',
                          'effective_date':None,'note':'Treasury official dated release index'})
    if not rows:
        raise ValueError('No dated Treasury release rows parsed; coverage unconfirmed')
    return [],{'items':items,'coverage':'current dated press-release index only; older pagination not exhaustive'}


def parse_ici_workbook(body, now):
    """Public ICI workbook: exact same universe, units explicitly USD millions."""
    from comex_gold.parser import read_workbook
    sheets,_=read_workbook(body)
    candidates=[rows for _,rows in sheets if any('Weekly Total Net Assets' in str(c) for r in rows for c in r)]
    if len(candidates)!=1:raise ValueError('ICI workbook identity missing/ambiguous')
    rows=candidates[0]
    if not any('(millions of dollars)' in str(c).lower() for r in rows[:6] for c in r):
        raise ValueError('ICI workbook units missing')
    heads=[r for r in rows[:10] if r and str(r[0]).strip()=='DATE']
    if len(heads)!=1:raise ValueError('ICI workbook DATE heading missing')
    groups=heads[0]
    total_start=next((i for i,c in enumerate(groups) if str(c).strip()=='TOTAL - ALL MONEY MARKET FUNDS'),None)
    if total_start is None:raise ValueError('ICI all-fund universe not found')
    end=next((i for i in range(total_start+1,len(groups)) if str(groups[i]).strip()),len(groups))
    tna_heads=[r for r in rows[:10] if any(str(c).strip()=='TNA' for c in r)]
    if len(tna_heads)!=1:raise ValueError('ICI TNA labels missing')
    tnas=[i for i in range(total_start,end) if str(tna_heads[0][i]).strip()=='TNA']
    if len(tnas)<4:raise ValueError('ICI all-fund TNA columns incomplete')
    labels=next((r for r in rows[:10] if any(str(c).strip()=='TAX-EXEMPT' for c in r)),None)
    if labels is None:raise ValueError('ICI category labels missing')
    def col(label):
        i=next((i for i in range(total_start,end) if str(labels[i]).strip()==label),None)
        if i is None or i+1 not in tnas:raise ValueError('ICI category/TNA heading changed')
        return i+1
    total_col=col('TOTAL');components=[col(k) for k in ['TAX-EXEMPT','GOVERNMENT','PRIME']]
    points={}
    for row in rows:
        raw=str(row[0]).strip() if row else ''
        if not re.fullmatch(r'\d{2}/\d{2}/\d{4}',raw):continue
        # The dated caption is not a data row.
        if len(row)<=total_col or row[total_col]=='':continue
        day=datetime.strptime(raw,'%m/%d/%Y').date().isoformat()
        value=number(row[total_col])
        if value<=0 or abs(value-sum(number(row[c]) for c in components))>2:
            raise ValueError('ICI workbook component reconciliation failed')
        if day in points:raise ValueError('Duplicate ICI workbook week')
        points[day]=value*1e6
    if len(points)<2:raise ValueError('ICI workbook too few dated rows')
    ordered=sorted(points);obs=[];changes=[]
    for i,day in enumerate(ordered):
        obs.append(observation('mmf_assets_usd',points[day],day,'USD',basis='ICI public workbook, TNA, USD millions'))
        if i and (datetime.fromisoformat(day)-datetime.fromisoformat(ordered[i-1])).days==7:
            delta=points[day]-points[ordered[i-1]]
            obs.append(observation('mmf_weekly_asset_change_usd',delta,day,'USD',basis='Difference of adjacent 7-day TNA rows; not net flow'))
            changes.append({'date':day,'asset_change_usd':delta})
    trend=None
    if len(ordered)>=14:
        last14=ordered[-14:]
        if all((datetime.fromisoformat(b)-datetime.fromisoformat(a)).days==7 for a,b in zip(last14,last14[1:])):
            start,finish=last14[0],last14[-1]
            v=points[finish]-points[start]
            trend={'weeks':13,'baseline_date':start,'end_date':finish,'asset_change_usd':v,
                   'asset_change_pct':100*v/points[start],'net_flow_usd':None}
    return obs, {'source_format':'ICI public XLS/XLSX','net_flow_usd':None,'verified_weeks':len(ordered),
                 'asset_trend_13w':trend,'weekly_asset_changes':changes,
                 'note':'总资产及资产差额；不是精确资金净流入。工作簿未单列发布时间，保持null。'}


def parse_bill(body, now, identity):
    root=XML.fromstring(body.decode('utf-8-sig'));bill=root.find('bill')
    if bill is None:raise ValueError('GovInfo BILLSTATUS bill missing')
    actual={k:(bill.findtext(k) or '').strip() for k in ['congress','type','number']}
    if actual!={k:str(v) for k,v in identity.items()}:raise ValueError('GovInfo bill identity mismatch')
    updated=bill.findtext('updateDate')
    if updated and datetime.fromisoformat(updated.replace('Z','+00:00'))>now:raise ValueError('Future BILLSTATUS update')
    title=bill.findtext('title') or ''
    actions=[]
    for a in bill.findall('./actions/item'):
        day=a.findtext('actionDate');description=a.findtext('text') or ''
        if not day:continue
        if datetime.strptime(day,'%Y-%m-%d').date()>now.astimezone(ET).date():raise ValueError('Future Congressional action')
        actions.append({'date':day,'text':description,'type':a.findtext('type')})
    if not actions:raise ValueError('GovInfo action history missing')
    latest_node=bill.find('latestAction')
    latest={'date':latest_node.findtext('actionDate'),'text':latest_node.findtext('text')} if latest_node is not None else max(actions,key=lambda a:a['date'])
    if latest['date']!=max(a['date'] for a in actions):raise ValueError('BILLSTATUS latest action/history mismatch')
    laws=[{'type':x.findtext('type'),'number':x.findtext('number')} for x in bill.findall('./laws/item')]
    enacted=any(x.get('type')=='Public Law' and x.get('number') for x in laws)
    start=(now.astimezone(MYT).date()-timedelta(days=7)).isoformat();end=now.astimezone(MYT).date().isoformat()
    items=[{'title':title+' — '+a['text'],'url':'https://www.govinfo.gov/app/details/BILLS-'+actual['congress']+actual['type'].lower()+actual['number'],
            'publication_date':None,'event_date':a['date'],'event_date_basis':'Congress actionDate',
            'legal_status':'CongressAction','effective_date':None,'action_type':a['type'],
            'note':'正式国会行动记录；不把程序行动当作成法或实施规则'}
           for a in actions if start<=a['date']<end]
    # Use the exact XML URL for traceability; app/details is version-specific and not guessed.
    xml_url='https://www.govinfo.gov/bulkdata/BILLSTATUS/'+actual['congress']+'/'+actual['type'].lower()+'/BILLSTATUS-'+actual['congress']+actual['type'].lower()+actual['number']+'.xml'
    for item in items:item['url']=xml_url
    return [], {'items':items,'bill_title':title,'bill_identity':actual,'bulk_updated_at':updated,
                'latest_action':latest,'laws':laws,'enactment_record':'ENACTED' if enacted else 'NO_ENACTMENT_RECORD',
                'actions_in_window':len(items),'coverage':'Only this identified bill; current official action history, not new-bill discovery'}
