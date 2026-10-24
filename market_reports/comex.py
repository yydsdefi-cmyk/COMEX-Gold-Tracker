import base64
import json
from datetime import datetime
from .core import MYT, UTC, parse_time, stamp, number, observation, inventory_level, digest
from .sources import download

BASE='https://api.github.com/repos/yydsdefi-cmyk/COMEX-Gold-Tracker'


def health(snapshot, now, runs):
    issues=[]
    try:
        attempt=parse_time(snapshot['last_update']['attempted_at_utc'])
        local=attempt.astimezone(MYT)
        if attempt>now or (now-attempt).total_seconds()>26*3600:
            issues.append('FUTURE_OR_OVERDUE_ATTEMPT')
        if local.date()!=now.astimezone(MYT).date() or local.hour<5:
            issues.append('NOT_TODAY_AFTER_05_MYT')
    except (ValueError,KeyError,TypeError):
        issues.append('UNCONFIRMED_ATTEMPT_TIME');attempt=None
    if not snapshot.get('available'):
        issues.append('UNAVAILABLE')
    if snapshot.get('update_status') not in ('OK','UNCHANGED') or snapshot.get('freshness')=='STALE':
        issues.append('UPDATE_OR_REPORT_STALE')
    completed=[r for r in runs if r.get('status')=='completed']
    scheduled=[r for r in runs if r.get('event')=='schedule']
    if not completed or not scheduled:
        issues.append('SCHEDULE_UNVERIFIED')
    elif completed[0].get('conclusion')!='success':
        issues.append('LATEST_COLLECTION_FAILED_OR_CANCELLED')
    elif attempt and (parse_time(completed[0]['updated_at'])-attempt).total_seconds()>300:
        issues.append('SNAPSHOT_BEHIND_RUN')
    return issues


def collect_comex(now,downloader=download):
    receipt={'id':'comex','url':BASE,'kind':'primary_via_existing_collector','max_age_days':4,
             'fetched_at_utc':stamp(now),'status':'MISSING','observations':[],'details':{}}
    try:
        def get(url):
            b,meta=downloader(url)
            return json.loads(b),meta
        runs,rm=get(BASE+'/actions/workflows/collect-and-publish.yml/runs?per_page=6')
        runs=runs['workflow_runs']
        snap=None
        for attempt in range(2):
            ref,_=get(BASE+'/git/ref/heads/main')
            sha=ref['object']['sha']
            js,meta=get(BASE+'/contents/data/latest.json?ref='+sha)
            raw=base64.b64decode(js['content'])
            snap=json.loads(raw)
            issues=health(snap,now,runs)
            if not issues:
                break
        receipt.update(response_sha256=digest(raw),fetched_at_utc=meta['fetched_at_utc'])
        # Check accounting identities independently of the collector's rounded output.
        if snap.get('available'):
            total=number(snap['total_oz']);reg=number(snap['registered_oz']);elig=number(snap['eligible_oz'])
            if total<=0 or abs(total-reg-elig)>.002 or abs(100*reg/total-number(snap['registered_ratio']))>.000002:
                raise ValueError('COMEX reconciliation or ratio mismatch')
            if inventory_level(snap.get('change_1d_pct'))!=snap['status']:
                raise ValueError('COMEX Total threshold mismatch')
            for metric,key,unit in [('comex_total','total_oz','troy_oz'),('comex_registered','registered_oz','troy_oz'),
                                    ('comex_eligible','eligible_oz','troy_oz'),('comex_registered_ratio','registered_ratio','percent')]:
                o=observation(metric,snap[key],snap['activity_date'],unit,snap['report_date'],
                              source='comex',source_url=BASE+'/contents/data/latest.json?ref='+sha,
                              fetched_at_utc=receipt['fetched_at_utc'],response_sha256=receipt['response_sha256'],
                              quality='OK' if not issues else 'UNVERIFIED')
                receipt['observations'].append(o)
        receipt['details']={'snapshot':snap,'commit':sha,'issues':issues,
                            'runs':[{'id':r['id'],'event':r['event'],'status':r['status'],'conclusion':r.get('conclusion'),
                                     'updated_at':r['updated_at'],'html_url':r['html_url']} for r in runs],
                            'retrieved_at_utc':stamp(now),'source_json':f'https://github.com/yydsdefi-cmyk/COMEX-Gold-Tracker/blob/{sha}/data/latest.json'}
        receipt['status']='OK' if not issues else 'UNVERIFIED'
    except Exception as e:
        receipt.update(status='MISSING',error=type(e).__name__+': '+str(e)[:350],observations=[])
    return receipt
