"""Public NYFed editorial calendar; supplementary evidence, not a BLS access fix."""
import calendar
import re
from datetime import datetime,timedelta
from urllib.parse import urljoin,urlparse
from .core import ET,MYT,stamp
from .parsers import text

URL='https://www.newyorkfed.org/research/calendars/nationalecon_cal'
KINDS=[('cpi',r'Consumer Price'),('ppi',r'Producer Price'),('jobs',r'Employment Situation'),
       ('eci',r'Employment Cost'),('gdp',r'Gross Domestic|\bGDP\b'),
       ('pce',r'Personal Income|\bPCE\b'),('fomc',r'FOMC|利率决定')]
NAMES={'cpi':'CPI消费物价指数','ppi':'PPI生产物价指数','jobs':'就业报告',
       'eci':'雇佣成本指数','gdp':'GDP','pce':'个人收入与PCE','fomc':'FOMC利率决定'}


def event_kind(name):
    return next((k for k,pattern in KINDS if re.search(pattern,name,re.I)),None)


def parse_calendar(body,url=URL):
    s=body.decode('utf-8-sig')
    if not re.search('all Eastern Time',s,re.I):raise ValueError('NYFed calendar timezone label missing')
    heading=re.search(r'class=["\']ts-data-table-head[^"\']*["\'][^>]*>\s*<div[^>]*>\s*([A-Z][a-z]+)\s+(\d{4})',s)
    if not heading:raise ValueError('NYFed calendar month identity missing')
    month=datetime.strptime(heading[1]+' '+heading[2],'%B %Y').date();last=calendar.monthrange(month.year,month.month)[1]
    cells=re.findall(r'<td\b[^>]*class=["\'][^"\']*\bsomatdR\b[^"\']*["\'][^>]*>(.*?)</td>',s[heading.end():],re.S)
    days=set();events=[]
    for cell in cells:
        day=re.match(r'\s*<div[^>]*>\s*(\d{1,2})\s*(?:<br\s*/?>|</div>)',cell)
        if not day:continue
        date=month.replace(day=int(day[1]))
        if date in days:raise ValueError('Duplicate NYFed calendar day')
        days.add(date)
        pattern=r'<a\b[^>]*href=["\']([^"\']+)["\'][^>]*>(.*?)</a>((?:(?!<a\b).){0,500}?)\((\d{2}:\d{2})\)'
        for link,name,_,clock in re.findall(pattern,cell,re.S|re.I):
            at=datetime.combine(date,datetime.strptime(clock,'%H:%M').time(),tzinfo=ET)
            name=text(name);kind=event_kind(name);release=urljoin(url,link)
            events.append({'name':name,'at_myt':at.astimezone(MYT).isoformat(),'source':'NYFed calendar',
                'tier1':kind is not None,'event_id':kind,'calendar_url':url,
                'release_url':release if release.startswith('https://') else None,
                'publication_date':None,'time_basis':'NYFed editorial calendar, Eastern Time; dates/times tentative'})
    expected={month.replace(day=d) for d in range(1,last+1) if month.replace(day=d).weekday()<5}
    if days!=expected:raise ValueError('NYFed calendar weekday coverage incomplete')
    if not events:raise ValueError('NYFed calendar has no timed releases')
    nxt=re.search(r'<a\b[^>]*href=["\']([^"\']+)["\'][^>]*>\s*NEXT MONTH',s,re.I)
    next_url=urljoin(url,nxt[1]) if nxt else None
    if next_url:
        u=urlparse(next_url)
        if u.scheme!='https' or u.netloc!='www.newyorkfed.org' or not re.fullmatch(r'/research/calendars/i-[a-z]{3}\d{2}\.html',u.path) or u.query or u.fragment:
            raise ValueError('NYFed next-month link outside documented calendar path')
    return {'events':events,'month':month.isoformat()[:7],'from':month.isoformat(),
            'through':month.replace(day=last).isoformat(),'next_url':next_url}


def collect_calendar(now,downloader):
    local=now.astimezone(MYT).date();end=(local+timedelta(days=7)).isoformat()
    receipt={'id':'nyfed_calendar','url':URL,'kind':'official_editorial_calendar','max_age_days':4,
             'fetched_at_utc':stamp(now),'status':'MISSING','observations':[],'details':{}}
    pages=[];events=[];issues=[];url=URL;prior=None
    try:
        for _ in range(2):
            body,meta=downloader(url);page=parse_calendar(body,url)
            if not pages:receipt.update({k:meta[k] for k in ['fetched_at_utc','response_sha256']})
            if prior and datetime.fromisoformat(page['from']).date()!=datetime.fromisoformat(prior['through']).date()+timedelta(days=1):
                raise ValueError('NYFed linked month is not consecutive')
            pages.append({'url':url,'month':page['month'],'from':page['from'],'through':page['through'],**meta})
            events += [{**e,'source_response_sha256':meta['response_sha256']} for e in page['events']]
            if page['through']>=end:break
            if not page['next_url']:raise ValueError('Next NYFed month not published/linked')
            prior=page;url=page['next_url']
        complete=bool(pages) and pages[0]['from']<=local.isoformat() and pages[-1]['through']>=end
        receipt['status']='OK' if complete else 'INCOMPLETE'
        if not complete:issues.append('Calendar month coverage does not cover today through next seven MYT dates')
    except Exception as exc:
        issues.append(type(exc).__name__+': '+str(exc)[:250]);receipt['status']='PARTIAL' if pages else 'MISSING'
        receipt['error']=issues[-1]
    start=(local-timedelta(days=7)).isoformat()
    receipt['details']={'events':[e for e in events if start<=e['at_myt'][:10]<=end],
        'pages':pages,'coverage_issues':issues,'calendar_covers_through':pages[-1]['through'] if pages else None,
        'coverage':'Supplementary NYFed public editorial calendar; underlying BLS page remains independently unavailable when denied',
        'publication_note':'Calendar first publication time not supplied; fetched_at is not publication time'}
    return receipt
