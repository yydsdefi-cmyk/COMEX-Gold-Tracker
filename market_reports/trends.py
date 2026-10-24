"""Dated comparisons with units, provenance and explicit incomplete-week status."""
from datetime import date,timedelta
from .core import MYT,parse_time,number

# metric, label, change rule, displayed level unit, scale, precision
SPECS=[('sp500','S&P 500','percent','点',1,2),('nasdaq','Nasdaq','percent','点',1,2),
 ('us10y','US10Y','bp','%',1,3),('dxy','DXY','percent','点',1,2),
 ('wti','WTI期货','percent','USD/桶',1,2),('gold','Gold期货','percent','USD/oz',1,2),
 ('btc','BTC/USD','percent','USD',1,2),('aaii_spread','AAII Spread','absolute','pp',1,1),
 ('cnn_fg','CNN F&G','absolute','点',1,1),('vix','VIX','absolute','点',1,2),
 ('vix3m','VIX3M','absolute','点',1,2),('vix_ratio','VIX/VIX3M','absolute','倍',1,3),
 ('crypto_fg','Crypto F&G','absolute','点',1,0),('srf_usd','SRF','absolute','B USD',1e9,6),
 ('mmf_assets_usd','MMF资产','absolute','B USD',1e9,2),
 ('comex_registered_ratio','Registered Ratio','absolute','%',1,3)]


def dated_series(captures,metric):
    rows={}
    for c in sorted(captures,key=lambda x:parse_time(x['generated_at_utc'])):
        for o in c['observations']:
            if o['metric']!=metric or o.get('scheduled') or o.get('quality') in ('FUTURE','UNVERIFIED'):continue
            if metric=='srf_usd' and not o.get('complete'):continue
            point={**o,'vintage_generated_at':c['generated_at_utc']}
            point['value']=number(point['value'])
            rows[o['observation_date']]=point
    return [rows[d] for d in sorted(rows)]


def paired_vix(captures):
    vx={o['observation_date']:o for o in dated_series(captures,'vix')}
    vm={o['observation_date']:o for o in dated_series(captures,'vix3m')}
    out=[]
    for d in sorted(set(vx)&set(vm)):
        if vm[d]['value']<=0:continue
        out.append({'metric':'vix_ratio','value':vx[d]['value']/vm[d]['value'],
            'observation_date':d,'publication_date':None,'unit':'ratio',
            'inputs':[vx[d],vm[d]],'basis':'Same observation date only; index tenor ratio, not a complete futures curve'})
    return out


def regime(value):
    return 'Backwardation' if value>1 else 'Contango' if value<1 else 'Flat'


def weekly_changes(capture,prior_captures):
    now=parse_time(capture['generated_at_utc']).astimezone(MYT).date()
    cutoff=(now-timedelta(days=7)).isoformat();earliest=(now-timedelta(days=14)).isoformat()
    captures=prior_captures+[capture];sources={r['id']:r['status'] for r in capture['sources']};out=[]
    for metric,label,rule,unit,scale,digits in SPECS:
        series=paired_vix(captures) if metric=='vix_ratio' else dated_series(captures,metric)
        points=[o for o in series if earliest<=o['observation_date']<=now.isoformat()]
        baseline=[o for o in points if o['observation_date']<=cutoff]
        recent=[o for o in points if o['observation_date']>cutoff]
        a=baseline[-1] if baseline else recent[0] if recent else None
        b=recent[-1] if recent else None
        record={'metric':metric,'label':label,'reference_date':cutoff,'unit':unit,'scale':scale,'digits':digits,
                'change_rule':rule,'baseline':a,'end':b,'change':None,'status':'INSUFFICIENT'}
        if a and b and a['observation_date']<b['observation_date']:
            record['status']='OK' if baseline else 'PARTIAL_WEEK'
            record['change']=(b['value']/a['value']-1)*100 if rule=='percent' and a['value'] else (b['value']-a['value'])*100 if rule=='bp' else (b['value']-a['value'])/scale if rule=='absolute' else None
            record['change_unit']='%' if rule=='percent' else 'bp' if rule=='bp' else 'pp' if metric=='comex_registered_ratio' else unit
            if record['change'] is None:record['status']='ZERO_BASELINE'
            record['baseline_gap_days']=(now-timedelta(days=7)-date.fromisoformat(a['observation_date'])).days
        if metric=='vix_ratio':
            record['source_status_current']={k:sources.get(k,'MISSING') for k in ['vix','vix3m']}
            if a and b:
                record['regime_start']=regime(a['value']);record['regime_end']=regime(b['value'])
                window=([a]+recent) if baseline else recent
                record['regime_changes']=[{'from_date':x['observation_date'],'to_date':y['observation_date'],
                    'from':regime(x['value']),'to':regime(y['value'])} for x,y in zip(window,window[1:]) if regime(x['value'])!=regime(y['value'])]
        else:
            source=(b or a or {}).get('source')
            record['source_status_current']=sources.get(source,'MISSING')
        out.append(record)
    return out
