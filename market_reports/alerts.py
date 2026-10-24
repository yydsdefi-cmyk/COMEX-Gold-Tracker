"""One recoverable, bot-owned GitHub incident. No external messaging or credentials."""
import argparse
import json
import os
from datetime import datetime,timedelta
from pathlib import Path
from urllib.parse import urlencode
from urllib.request import Request,urlopen
from .core import MYT,UTC

MARKER='<!-- market-reports-health:v1 -->'
TITLE='Market reports: pipeline needs attention'
CRITICAL={'comex','srf','crypto','vix','vix3m'}


def problems(data,now,pipeline_result='success'):
    data=Path(data);local=now.astimezone(MYT);out=[]
    if pipeline_result not in ('success','skipped'):out.append('Report workflow result: '+pipeline_result)
    targets=[]
    if local.hour>=8:targets.append(('daily',local.date()))
    days=(local.weekday()-5)%7
    last_sat=local.date()-timedelta(days=days)
    if days==0 and local.hour<10:last_sat-=timedelta(days=7)
    # Do not alert for weeks preceding installation; current project begins 2026-10-24.
    if last_sat.isoformat()>='2026-10-24':targets.append(('weekly',last_sat))
    for kind,day in targets:
        path=data/'reports'/kind/day.isoformat()/'latest.json'
        if not path.exists():out.append(kind+' report missing for MYT '+day.isoformat());continue
        try:
            ptr=json.loads(path.read_text());q=json.loads((path.parent/ptr['revision']/'quality.json').read_text())
            bad=CRITICAL&set(q['missing_or_unverified'])
            if bad:out.append(kind+' critical sources incomplete: '+', '.join(sorted(bad)))
        except (OSError,KeyError,ValueError) as exc:out.append(kind+' health record unreadable: '+type(exc).__name__)
    return sorted(set(out))


def reconcile(call,issues,run_url):
    """Never edit a human issue or an unrelated bot issue with a matching title."""
    match=None
    for page in range(1,6):
        rows=call('/issues?'+urlencode({'state':'open','sort':'updated','direction':'desc','per_page':100,'page':page}))
        for row in rows:
            if row.get('title')==TITLE and row.get('user',{}).get('login')=='github-actions[bot]' and MARKER in (row.get('body') or '') and 'pull_request' not in row:
                match=row;break
        if match or len(rows)<100:break
    else:
        # Do not risk duplicate incidents if bounded issue discovery cannot finish.
        raise ValueError('Open-issue lookup exceeded bounded 500 entries')
    if issues:
        body=MARKER+'\nAutomated report health incident.\n\n'+'\n'.join('- '+s for s in issues)+'\n\nRun: '+run_url+'\n\nKnown noncritical source restrictions remain visible in the report quality record. No missing value is zero.'
        if match:
            call('/issues/'+str(match['number']),'PATCH',{'body':body});return 'UPDATED'
        call('/issues','POST',{'title':TITLE,'body':body});return 'OPENED'
    if match:
        call('/issues/'+str(match['number']),'PATCH',{'state':'closed','state_reason':'completed'});return 'RESOLVED'
    return 'HEALTHY_NO_INCIDENT'


def main():
    a=argparse.ArgumentParser(description=__doc__);a.add_argument('--data-dir',default='market_data');args=a.parse_args()
    repo=os.environ['GITHUB_REPOSITORY'];token=os.environ['GITHUB_TOKEN'];run_id=os.environ['GITHUB_RUN_ID']
    if '/' not in repo or any(x in repo for x in ['?','#','..']):raise ValueError('Invalid repository identity')
    base='https://api.github.com/repos/'+repo
    def call(path,method='GET',payload=None):
        req=Request(base+path,data=json.dumps(payload).encode() if payload is not None else None,method=method,
            headers={'Authorization':'Bearer '+token,'Accept':'application/vnd.github+json','User-Agent':'MarketReports-health'})
        with urlopen(req,timeout=20) as r:return json.load(r)
    failed=problems(args.data_dir,datetime.now(UTC),os.environ.get('PIPELINE_RESULT','success'))
    outcome=reconcile(call,failed,'https://github.com/'+repo+'/actions/runs/'+run_id)
    print(json.dumps({'incident_action':outcome,'problems':failed}))

if __name__=='__main__':main()
