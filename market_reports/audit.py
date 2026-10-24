"""Read-only Decimal audit against archived source observations; no network or LLM."""
import argparse
import json
from datetime import date,timedelta
from decimal import Decimal
from pathlib import Path
from .core import DATA

PERCENT={'sp500','nasdaq','dxy','wti','gold','btc'}
ABSOLUTE={'aaii_spread':'pp','cnn_fg':'点','vix':'点','vix3m':'点','vix_ratio':'倍',
          'crypto_fg':'点','srf_usd':'B USD','mmf_assets_usd':'B USD','comex_registered_ratio':'pp'}
SCALE={'srf_usd':Decimal('1000000000'),'mmf_assets_usd':Decimal('1000000000')}
LEVEL_UNITS={**ABSOLUTE,'sp500':'点','nasdaq':'点','dxy':'点','wti':'USD/桶','gold':'USD/oz',
             'btc':'USD','us10y':'%','comex_registered_ratio':'%'}


def decimal(value):
    v=Decimal(str(value))
    if not v.is_finite():raise ValueError('Non-finite audit input')
    return v


def audit_payload(payload,captures):
    rows=payload.get('analysis',{}).get('weekly_comparisons')
    if rows is None:return {'status':'BLOCKED','reason':'No structured weekly comparisons in this historical method version','checks':[]}
    raw=[o for c in captures for o in c['observations']]
    def source_value(p,metric):
        if p['metric']!=metric:raise ValueError('Comparison metric identity mismatch')
        if p.get('quality') in ('FUTURE','UNVERIFIED'):raise ValueError('Unverified/future point cannot support a comparison')
        if metric=='vix_ratio':
            inputs=p['inputs']
            if len(inputs)!=2 or {x['metric'] for x in inputs}!={'vix','vix3m'} or any(x['observation_date']!=p['observation_date'] for x in inputs):
                raise ValueError('VIX tenor inputs must share the identical observation date')
            values={x['metric']:source_value(x,x['metric']) for x in inputs}
            if values['vix3m']<=0:raise ValueError('Invalid VIX3M denominator')
            v=values['vix']/values['vix3m']
            if abs(v-decimal(p['value']))>Decimal('0.000000000001'):raise ValueError('VIX ratio does not match source inputs')
            return v
        match=any(o['metric']==metric and o['observation_date']==p['observation_date'] and
            o.get('source_url')==p.get('source_url') and o.get('response_sha256')==p.get('response_sha256') and
            decimal(o['value'])==decimal(p['value']) for o in raw)
        if not match:raise ValueError('Comparison input is not bound to an archived source observation')
        return decimal(p['value'])
    checks=[];cutoff=date.fromisoformat(payload['intended_local_date'])-timedelta(days=7)
    for row in rows:
        metric=row['metric'];check={'metric':metric}
        if row.get('change') is None:
            checks.append({**check,'status':'NOT_CALCULABLE','reason':row['status']});continue
        try:
            a,b=row['baseline'],row['end'];av=source_value(a,metric);bv=source_value(b,metric)
            if decimal(row['scale'])!=SCALE.get(metric,Decimal(1)) or row['unit']!=LEVEL_UNITS.get(metric):raise ValueError('Display scale/unit mismatch')
            if not a['observation_date']<b['observation_date']<=payload['intended_local_date']:raise ValueError('Invalid comparison date order')
            if row['status']=='OK' and not a['observation_date']<=cutoff.isoformat()<b['observation_date']:raise ValueError('Full-week label lacks a week-start baseline')
            if row['status']=='PARTIAL_WEEK' and not cutoff.isoformat()<a['observation_date']:raise ValueError('Incorrect partial-week label')
            if metric in PERCENT:
                if av==0:raise ValueError('Zero percentage baseline')
                want=(bv-av)*Decimal(100)/av;unit='%'
            elif metric=='us10y':want=(bv-av)*Decimal(100);unit='bp'
            elif metric in ABSOLUTE:want=(bv-av)/SCALE.get(metric,Decimal(1));unit=ABSOLUTE[metric]
            else:raise ValueError('No independent measurement rule for metric')
            if row['change_unit']!=unit:raise ValueError('Change unit mismatch')
            if abs(want-decimal(row['change']))>Decimal('0.0000001'):raise ValueError('Derived change differs from independent Decimal calculation')
            check.update(status='PASS',baseline_date=a['observation_date'],end_date=b['observation_date'],
                         expected_change=str(want),actual_change=row['change'],unit=unit)
        except (KeyError,ValueError,ArithmeticError) as exc:check.update(status='FAIL',error=str(exc))
        checks.append(check)
    passed=sum(c['status']=='PASS' for c in checks);failed=sum(c['status']=='FAIL' for c in checks)
    return {'status':'FAIL' if failed else 'PASS_CALCULABLE_ONLY' if passed else 'BLOCKED',
            'scope':'Numeric comparisons and archived observation binding only; not full source coverage or legal semantics',
            'capture_id':payload['capture_id'],'verified':passed,'failed':failed,'not_calculable':len(checks)-passed-failed,'checks':checks}


def main():
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('--data-dir',type=Path,default=DATA);args=p.parse_args()
    from .__main__ import validate_archive
    validate_archive(args.data_dir)
    pointers=sorted((args.data_dir/'reports/weekly').glob('*/latest.json'))
    if not pointers:result={'status':'BLOCKED','reason':'No weekly archive'}
    else:
        latest=pointers[-1];ptr=json.loads(latest.read_text());payload=json.loads((latest.parent/ptr['revision']/'report.json').read_text())
        captures=[json.loads(p.read_text()) for p in (args.data_dir/'captures').glob('*.json')]
        result=audit_payload(payload,captures)
    print(json.dumps(result,ensure_ascii=False,indent=2))
    return 1 if result['status']=='FAIL' else 0


if __name__=='__main__':raise SystemExit(main())
