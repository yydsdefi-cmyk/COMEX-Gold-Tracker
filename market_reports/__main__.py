import argparse
import json
import sys
from datetime import datetime, timedelta
from pathlib import Path
from .core import DATA, MYT, ROOT, UTC, atomic, commit_bundle, digest, due_reports, encoded, immutable, rebuild_history, stamp, verify_bundle
from .sources import collect, registry
from .comex import collect_comex
from .report import daily,weekly
from .render import publish


def validate_archive(data):
    data=Path(data)
    checked=0
    for manifest in sorted((data/'reports').glob('*/*/*/MANIFEST.json')):
        verify_bundle(manifest.parent);checked+=1
    for pointer in sorted((data/'reports').glob('*/*/latest.json')):
        p=json.loads(pointer.read_text())
        verify_bundle(pointer.parent/p['revision']);checked+=1
    for p in sorted((data/'captures').glob('*.json')):
        raw=p.read_bytes()
        if p.stem!=digest(raw):raise ValueError('Capture hash mismatch '+p.name)
        c=json.loads(raw)
        if c['schema_version']!=1:raise ValueError('Unknown capture schema')
        sources={r['id']:r for r in c['sources']}
        if set(sources)!={s['id'] for s in registry(datetime.now(UTC))}|{'comex'}:
            raise ValueError('Capture source set mismatch')
        for o in c['observations']:
            r=sources[o['source']]
            if not o.get('source_url') or o.get('response_sha256')!=r.get('response_sha256'):
                raise ValueError('Missing or mismatched provenance')
            if o not in r['observations']:raise ValueError('Capture observation/source mismatch')
        checked+=1
    return checked


def run(kinds,data=DATA,now=None,collector=collect,comex_collector=collect_comex):
    data=Path(data);fixed_now=now is not None;now=now or datetime.now(UTC)
    validate_archive(data)
    if kinds==['due']:
        kinds=due_reports(now,data)
    if not kinds:
        print('No report due; existing archive verified.');return None
    started_at=stamp(now)
    receipts=collector(now)+[comex_collector(now)]
    if not fixed_now:now=datetime.now(UTC)
    capture={'schema_version':1,'collection_started_at_utc':started_at,'generated_at_utc':stamp(now),'timezone':'Asia/Kuala_Lumpur',
             'sources':receipts,'observations':[o for r in receipts for o in r['observations']]}
    raw=encoded(capture);capture_id=digest(raw)
    immutable(data/'captures'/(capture_id+'.json'),raw)
    quality={'generated_at_utc':stamp(now),'sources':[{k:r.get(k) for k in ['id','status','url','fetched_at_utc','response_sha256','error']} for r in receipts],
             'missing_or_unverified':[r['id'] for r in receipts if r['status']!='OK'],
             'semantic_limits':['Full regulatory legal-effect review is not automated','No paid economic consensus or WI Treasury quotes',
                                'Missing publication dates remain null; fetch/modified times not substituted',
                                'Calendar-day staleness limits are conservative; no holiday calendar claimed'],
             'acceptance':'DEGRADED' if any(r['status']!='OK' for r in receipts) else 'DATA_CHECKS_PASSED'}
    older=[]
    today=now.astimezone(MYT).date()
    for p in sorted((data/'reports'/'daily').glob('*/latest.json')):
        day=datetime.fromisoformat(p.parent.name).date()
        if today-timedelta(days=6)<=day<today:
            info=json.loads(p.read_text());b=p.parent/info['revision'];verify_bundle(b)
            older.append(json.loads((b/'report.json').read_text())['capture'])
    outputs=[]
    for kind in kinds:
        md=daily(capture) if kind=='daily' else weekly(capture,older)
        payload={'kind':kind,'intended_local_date':today.isoformat(),'target_time_myt':'08:00' if kind=='daily' else '10:00',
                 'capture_id':capture_id,'capture':capture,'quality':quality,'method_version':'1.0.0'}
        folder=data/'reports'/kind/today.isoformat()
        files={'report.md':md,'report.json':encoded(payload),'quality.json':encoded(quality)}
        revision=commit_bundle(folder,files)
        # Pointer is the only mutable archive object and is written after a full verified revision.
        pointer={'revision':revision,'generated_at_utc':stamp(now),'degraded':quality['acceptance']!='DATA_CHECKS_PASSED','capture_id':capture_id}
        atomic(folder/'latest.json',encoded(pointer));outputs.append({'kind':kind,'date':today.isoformat(),**pointer})
    count=rebuild_history(data)
    atomic(data/'quality.json',encoded(quality))
    atomic(data/'source_registry.json',encoded({'generated_at_utc':stamp(now),'sources':registry(now)+[{'id':'comex','url':'https://github.com/yydsdefi-cmyk/COMEX-Gold-Tracker','method':'commit-pinned latest.json plus collection workflow run verification'}]}))
    atomic(data/'health.json',encoded({'last_generated_at_utc':stamp(now),'outputs':outputs,'quality':quality['acceptance'],'historical_rows':count,'requires_clock_recheck':True}))
    validate_archive(data)
    print(json.dumps({'outputs':outputs,'quality':quality['acceptance'],'missing':quality['missing_or_unverified'],'historical_rows':count},ensure_ascii=False,indent=2))
    return quality


def main():
    a=argparse.ArgumentParser(description='No-cost market reports')
    a.add_argument('command',choices=['run','publish','verify'])
    a.add_argument('--report',choices=['daily','weekly','both','due'],default='due')
    a.add_argument('--data-dir',type=Path,default=DATA)
    a.add_argument('--site',type=Path,default=ROOT/'public-data')
    a.add_argument('--strict',action='store_true',help='Exit 2 AFTER preserving degraded reports, for Actions failure alerts')
    args=a.parse_args()
    if args.command=='run':
        q=run(['daily','weekly'] if args.report=='both' else [args.report],args.data_dir)
        if q and q['missing_or_unverified'] and args.strict:return 2
    elif args.command=='verify':
        print('Verified archive objects:',validate_archive(args.data_dir))
    else:
        print('Published report dates:',publish(args.data_dir,args.site))
    return 0

if __name__=='__main__':
    sys.exit(main())
