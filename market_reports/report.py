import json
import re
from datetime import datetime, timedelta
from .core import MYT, parse_time, number
from .regulation import timeline_day,asset_relevance,KEY


def compose(lines):
    # GFM tables require adjacent rows, even though normal paragraphs use blank lines.
    return re.sub(r'(?m)(\|[^\n]*\|)\n\n(?=\|)',r'\1\n','\n\n'.join(lines))+'\n'


def fmt(v, digits=2, signed=False):
    if v is None:
        return '待确认'
    return format(v, ('+' if signed else '')+',.'+str(digits)+'f')


def latest(capture, metric):
    rows=[o for o in capture['observations'] if o['metric']==metric and not o.get('scheduled')]
    return max(rows,key=lambda x:x['observation_date']) if rows else None


def series(capture,metric):
    return sorted([o for o in capture['observations'] if o['metric']==metric],key=lambda x:x['observation_date'])


def value(capture,metric):
    o=latest(capture,metric)
    return o['value'] if o else None


def quality(o):
    return '' if o and o.get('quality')=='OK' else ' ⚠'+(o.get('quality','待确认') if o else '待确认')


def dates(o):
    if not o:
        return '观察/发布：待确认'
    return '观察 '+o['observation_date']+'｜发布 '+str(o.get('publication_date') or '未提供')+quality(o)


def source_link(receipt):
    return '['+receipt['id']+']('+receipt['url']+')'


def event_list(capture, future=False):
    now=parse_time(capture['generated_at_utc'])
    local=now.astimezone(MYT)
    events=[]
    for r in capture['sources']:
        for e in r.get('details',{}).get('events',[]):
            at=parse_time(e['at_myt'])
            in_window=local.date()<=at.date()<=local.date()+timedelta(days=7) if future else at.date()==local.date()
            if e.get('tier1') and in_window:
                events.append(e)
    return sorted(events,key=lambda x:x['at_myt'])


def event_lines(capture,future=False):
    src={r['id']:r for r in capture['sources']}
    events=event_list(capture,future)
    lines=[]
    for e in events[:8 if future else 3]:
        lines.append('- '+e['at_myt'].replace('T',' ')[:16]+' MYT｜'+e['name']+'（'+e['source']+'）')
    if not events:
        lines.append('已读取日历内未发现符合筛选的Tier-1事件；不等于完整全球经济日历无事件。')
    failed=[k for k in ['bls','bea','fomc'] if src.get(k,{}).get('status')!='OK']
    if failed:
        lines.append('⚠ 日历覆盖待确认：'+', '.join(failed))
    lines.append('范围：美国BLS/BEA/FOMC；不含付费共识预期与自动因果归因。FOMC时刻按14:00 ET惯例估计，临时变更待核验。')
    return lines


def comex_lines(capture):
    r=next((r for r in capture['sources'] if r['id']=='comex'),{})
    d=r.get('details',{});s=d.get('snapshot',{})
    if not s:
        return ['本次COMEX未核验：'+r.get('error','数据缺失')]
    now=parse_time(capture['generated_at_utc']).astimezone(MYT)
    attempt=s.get('last_update',{}).get('attempted_at_utc')
    attempt=parse_time(attempt).astimezone(MYT).strftime('%m-%d %H:%M:%S') if attempt else '待确认'
    status='数据核验通过' if r['status']=='OK' else '⚠读取/更新异常：'+', '.join(d.get('issues',[]))
    lines=[f"读取：GitHub提交 {d['commit'][:8]}｜核验MYT {now:%m-%d %H:%M}｜采集尝试MYT {attempt}｜{status}",
           'Activity '+str(s.get('activity_date'))+'｜Report '+str(s.get('report_date'))+'｜'+str(s.get('update_status'))+' / '+str(s.get('freshness'))]
    if not s.get('available'):
        return lines+['available=false；不报告库存数。']
    if r['status']!='OK':
        lines.append('以下仅为上次可得旧数据，不代表今日已更新。')
    lines += ['Registered Ratio **'+fmt(s.get('registered_ratio'),3)+'%**｜库存风险 '+str(s.get('status')),
              '|分类|当前 M oz|1D|5D|10D|20D|','|---|---:|---:|---:|---:|---:|']
    for label,key,prefix in [('Total','total_oz',''),('Registered','registered_oz','registered_'),('Eligible','eligible_oz','eligible_')]:
        fields=[]
        for n in [1,5,10,20]:
            v=s.get(prefix+f'change_{n}d_pct')
            fields.append('暂不可算' if v is None else fmt(v,3,True)+'%')
        lines.append('|'+label+'|'+fmt(s.get(key,0)/1e6,3)+'|'+'|'.join(fields)+'|')
    windows=s.get('change_windows',{})
    lines.append('窗口：'+'；'.join(k.upper()+' '+str(v.get('baseline_date') or '官方PREV TOTAL')+' / '+str(v.get('status')) for k,v in windows.items()))
    bad=[x for x in s.get('history_continuity_issues',[]) if x]
    if bad:
        lines.append('历史衔接异常：'+'；'.join(str(x.get('prior_activity_date'))+'→'+str(x.get('next_activity_date'))+' '+str(x.get('status')) for x in bad)+'；不可跨异常自行相减或推断实物出库。')
    reg=s.get('registered_alert',{})
    if reg.get('rapid_decline_1d') or reg.get('persistent_decline_5_consecutive_days'):
        lines.append('⚠ Registered 快速或持续下降：'+json.dumps(reg,ensure_ascii=False))
    if s.get('status')!='NORMAL':
        lines.append('异常绝对量：Total 1D '+fmt(s.get('change_1d_oz'),3,True)+' oz。')
    if not s.get('is_latest_confirmed'):
        lines.append('官方最新发布状态未独立确认。')
    lines.append('Pledged已在Registered内；Eligible单独下降不证明交割短缺；NORMAL仅指Total单日库存阈值。')
    lines.append('[核验快照]('+d['source_json']+')｜[CME官方报告](https://www.cmegroup.com/delivery_reports/Gold_Stocks.xls)')
    return lines


def treasury_lines(capture):
    r=next((r for r in capture['sources'] if r['id']=='treasury'),{})
    if r.get('status')!='OK':
        return ['Treasury待确认：'+r.get('error','无可靠来源')]
    today=parse_time(capture['generated_at_utc']).astimezone(MYT).date()
    auctions=r['details']['auctions']
    upcoming=[a for a in auctions if today.isoformat()<=a['date']<=(today+timedelta(days=7)).isoformat()]
    # Select all announced offerings and show the larger coupons first; never omit bills from totals.
    lines=[]
    for label,rows in [('Bills',[a for a in upcoming if a['type']=='Bill']),('Coupon（含TIPS/FRN）',[a for a in upcoming if a['type']!='Bill'])]:
        amounts=[a['offering_usd'] for a in rows]
        total=fmt(sum(amounts)/1e9)+'B USD' if rows and all(x is not None for x in amounts) else '待确认'
        lines.append(label+'｜已公告未来7日合计 **'+total+'**（非尚未公告的完整供给预测）')
    for a in upcoming[:12]:
        lines.append('- '+a['date']+' ET｜'+a['type']+' '+str(a['term'])+'｜$'+fmt(a['offering_usd']/1e9 if a['offering_usd'] is not None else None)+'B｜公告 '+str(a['announcement_date'])+'｜MYT '+str(a['close_myt'] or '精确时刻待确认'))
    recent=[a for a in auctions if a['type']!='Bill' and (today-timedelta(days=3)).isoformat()<=a['date']<=today.isoformat() and a['bid_to_cover'] is not None]
    for a in recent[-2:]:
        lines.append('最近coupon：'+a['date']+' '+str(a['term'])+'｜Bid-to-cover '+fmt(a['bid_to_cover'])+'｜High yield '+fmt(a['high_yield'],3)+'%｜Tail/stop-through 待确认（无可核验WI收益率）。')
    return lines or ['未来7日已公告拍卖待确认。']


def daily(capture):
    now=parse_time(capture['generated_at_utc']).astimezone(MYT)
    sources={r['id']:r for r in capture['sources']}
    missing=[k for k,r in sources.items() if r['status']!='OK']
    lines=[f'# 市场反向指标晨报｜{now:%Y-%m-%d}',f'生成 {now:%H:%M} MYT｜目标08:00 MYT｜规则生成，无LLM/API订阅。',
           '## 7项总览',
           '- 美股情绪：'+('部分数据待确认，极端共振不能确认。' if sources.get('cnn',{}).get('status')!='OK' else '见来源分类；AAII/VIX未预设新极端阈值。'),
           '- Crypto：'+('最新 '+fmt(value(capture,'crypto_fg'),0)+'，与昨日/7日前分开核对。' if latest(capture,'crypto_fg') else '待确认。'),
           '- Event Risk：'+str(len(event_list(capture)))+'项已读取日历候选；覆盖限制见下。',
           '- SRF：'+(str(latest(capture,'srf_usd').get('level')) if latest(capture,'srf_usd') else '待确认')+'，不等同QE判断。',
           '- Treasury：未来7日已公告供给分Bills/Coupon。',
           '- COMEX：'+('当天核验通过；库存风险另列。' if sources.get('comex',{}).get('status')=='OK' else '⚠本次未通过采集核验。'),
           '- Cash Liquidity：'+('周资产变化可得；不是精确净流入。' if value(capture,'mmf_assets_usd') is not None else '待确认。'),
           '## Overnight（各自日期，非同步实时行情）']
    for metric,label in [('sp500','S&P 500'),('nasdaq','Nasdaq'),('us10y','US10Y'),('dxy','DXY'),('wti','WTI期货'),('gold','Gold期货'),('btc','BTC/USD')]:
        rows=series(capture,metric);o=rows[-1] if rows else None
        change=None
        if len(rows)>1:
            a,b=rows[-2]['value'],rows[-1]['value']
            change=(b-a)*100 if metric=='us10y' else (b/a-1)*100 if a else None
        lines.append('- '+label+' **'+fmt(o['value'] if o else None,2)+'** '+fmt(change,2,True)+('bp' if metric=='us10y' else '%')+'｜'+dates(o))
    lines.append('Yahoo为次级来源；期货与现货有差异，最新日线可能仍在交易中，报价时刻见JSON。')
    lines += ['## US Contrarian']
    a=latest(capture,'aaii_bull')
    lines.append('AAII Bull/Neutral/Bear '+ '/'.join(fmt(value(capture,'aaii_'+k),1) for k in ['bull','neutral','bear'])+'%｜Spread '+fmt(value(capture,'aaii_spread'),1,True)+'pp｜'+dates(a))
    cnn=latest(capture,'cnn_fg')
    lines.append('CNN F&G '+fmt(cnn['value'] if cnn else None,0)+' '+str(cnn.get('classification','') if cnn else '')+'｜'+dates(cnn))
    vx={o['observation_date']:o for o in series(capture,'vix')};vm={o['observation_date']:o for o in series(capture,'vix3m')}
    common=sorted(set(vx)&set(vm))
    for metric,label in [('vix','VIX'),('vix3m','VIX3M')]:
        o=latest(capture,metric);lines.append(label+' '+fmt(o['value'] if o else None)+'｜'+dates(o))
    if common and vm[common[-1]]['value']>0:
        d=common[-1];ratio=vx[d]['value']/vm[d]['value']
        lines.append('同日 '+d+' VIX/VIX3M **'+fmt(ratio,3)+'** → '+('Backwardation' if ratio>1 else 'Contango' if ratio<1 else 'Flat')+'（期限比率标签，不代表VIX期货曲线全部形状）')
    else:
        lines.append('VIX/VIX3M同日可比比率：待确认；不混用日期。')
    lines.append('解读：原规格未给AAII/VIX极端情绪数值阈值，三项共同极端状态保留待确认，不新增买卖信号。')
    lines += ['## Crypto F&G（Alternative.me）']
    byday={o['observation_date']:o for o in series(capture,'crypto_fg')}
    for n,label in [(0,'今日'),(1,'昨日'),(7,'7日前')]:
        day=(now.date()-timedelta(days=n)).isoformat();o=byday.get(day)
        lines.append(label+' '+day+'｜'+fmt(o['value'] if o else None,0)+' '+str(o.get('classification','') if o else '待确认'))
    lines.append('观察日期以供应商UTC日戳为准；不拿“最新一条”冒充今日。')
    lines += ['## 今日Event Risk（MYT）']+event_lines(capture)
    lines += ['## SRF（常规隔夜操作）']
    o=latest(capture,'srf_usd')
    if o:
        lines.append('$'+fmt(o['value']/1e9,6)+'B → '+o['level']+'｜'+dates(o)+'｜'+str(o['operation_count'])+'场；'+('完整度规则通过' if o.get('complete') else '⚠仅部分操作，不能视为全天总量'))
        if o['level']!='Normal':
            lines.append('观察：流动性使用量触发用户监控等级；超过$100B也不代表必然QE。')
        excluded=sources['srf']['details'].get('excluded_exercises',[])
        if excluded:
            lines.append('API窗口内排除小额测试 '+str(len(excluded))+'场；逐笔证据见JSON。')
    else:
        lines.append('待确认；缺失不写0。')
    lines += ['## Treasury']+treasury_lines(capture)
    lines += ['## COMEX Gold']+comex_lines(capture)
    lines += ['## Cash Liquidity / ICI']
    a=latest(capture,'mmf_assets_usd');delta=value(capture,'mmf_weekly_asset_change_usd')
    lines.append('总资产 $'+fmt(a['value']/1e12 if a else None,5)+'T｜周资产变化 $'+fmt(delta/1e9 if delta is not None else None,2,True)+'B｜'+dates(a))
    lines.append('精确周净流量、约3个月已核验资金流趋势：待确认。资产高不等于近期逃向现金，也不意味着必然回流股市。')
    lines += ['## 数据质量与来源','⚠ 缺失/过期/未核验：'+(', '.join(missing) if missing else '无')+'。发布时间未提供则明确留空；抓取时间不代替发布时间。',
              '本报告区分观察与解读；排除BTC seasonality、自选股、X讨论和普通财报清单。']
    for r in capture['sources']:
        lines.append('- '+source_link(r)+'｜'+r['status']+'｜抓取 '+r['fetched_at_utc']+(('｜'+r['error']) if r.get('error') else ''))
    return compose(lines)


CRYPTO=KEY
STATUS={'CongressAction':'正式国会行动记录（不等于已成法）','FinalRuleAnnouncement':'最终规则公告（不自动等于已生效）','ProposalAnnouncement':'提案/征求意见公告（尚非最终规则）','SupervisoryPriorities':'监管检查重点（不是新规则）','GuidanceOrSpeech':'指引/声明/讲话（非正式规则证明）','Rule':'正式规则（生效日期单独核验）','Proposed Rule':'拟议规则（未生效）','Notice':'通知（法律效力逐项核验）','Presidential Document':'总统文件（法律效力逐项核验）'}


def timeline(capture):
    now=parse_time(capture['generated_at_utc']);items={}
    start=(now.astimezone(MYT).date()-timedelta(days=7)).isoformat();end=now.astimezone(MYT).date().isoformat()
    for r in capture['sources']:
        for item in r.get('details',{}).get('items',[]):
            if not CRYPTO.search(item['title']) and not item.get('topic_signal'):continue
            day=timeline_day(item)
            if not day or not start<=day<end:continue
            key=(item['url'],day,item['title'])
            items.setdefault(key,{**item,'source':r['id'],'timeline_date':day})
    return sorted(items.values(),key=lambda x:(x['timeline_date'],x['url'],x['title']))


def regulatory_upcoming(capture):
    now=parse_time(capture['generated_at_utc']).astimezone(MYT).date();out=[]
    for r in capture['sources']:
        for item in r.get('details',{}).get('items',[]):
            for key,label in [('effective_date','所载生效日'),('comments_close_on','意见截止日')]:
                day=item.get(key)
                if day and now.isoformat()<=day<=(now+timedelta(days=7)).isoformat():
                    out.append('- '+day+'｜'+label+'｜['+item['title'].replace('[','(').replace(']',')')+']('+item['url']+')（原文件日期；截止时刻/时区未提供时不猜）')
    return list(dict.fromkeys(out))


def weekly(capture, daily_captures):
    now=parse_time(capture['generated_at_utc']).astimezone(MYT)
    lines=[f'# 每周市场与Crypto监管周报｜{now:%Y-%m-%d}',f'生成 {now:%H:%M} MYT｜目标周六10:00 MYT｜市场数据截至本次抓取；监管覆盖此前7个完整日期（来源发布日期口径），延迟抓取不冒充准点发布。',
           '## 一周市场变化',f'已累积 {len(daily_captures)} 个不同MYT日期的日报档案；少于7天时不冒充完整晨报周总结。',
           '|指标|可核验期初→期末|变化|','|---|---|---|']
    for metric,label in [('sp500','S&P 500'),('nasdaq','Nasdaq'),('aaii_spread','AAII Spread pp'),('cnn_fg','CNN F&G'),('vix','VIX'),('vix3m','VIX3M'),('crypto_fg','Crypto F&G'),('srf_usd','SRF USD'),('mmf_assets_usd','MMF资产 USD')]:
        rows={}
        for c in daily_captures+[capture]:
            for o in c['observations']:
                if o['metric']==metric and (now.date()-timedelta(days=14)).isoformat()<=o['observation_date']<=now.date().isoformat():
                    rows[o['observation_date']]=o
        ordered=[rows[k] for k in sorted(rows)]
        baseline=[o for o in ordered if o['observation_date']<=(now.date()-timedelta(days=7)).isoformat()]
        current=[o for o in ordered if o['observation_date']>(now.date()-timedelta(days=7)).isoformat()]
        ordered=([baseline[-1]] if baseline else [])+current
        if len(ordered)<2:
            lines.append('|'+label+'|已核验独立日期不足|待确认|');continue
        a,b=ordered[0],ordered[-1]
        lines.append('|'+label+'|'+a['observation_date']+' '+fmt(a['value'])+' → '+b['observation_date']+' '+fmt(b['value'])+'|'+fmt(b['value']-a['value'],2,True)+'（原单位）|')
    srf=series(capture,'srf_usd');srf=[o for o in srf if (now.date()-timedelta(days=6)).isoformat()<=o['observation_date']<=now.date().isoformat()]
    if srf:
        lines.append('SRF已取得日期的使用量合计 $'+fmt(sum(o['value'] for o in srf)/1e9,6)+'B；最大单日 $'+fmt(max(o['value'] for o in srf)/1e9,6)+'B。按操作日期去重，测试操作排除；缺日不补0，合计不是未偿存量。')
    summary=[]
    spread=series(capture,'aaii_spread')
    if len(spread)>=2:
        a,b=spread[-2],spread[-1];change=b['value']-a['value']
        summary.append('AAII Bull-Bear Spread '+fmt(a['value'],1)+'→'+fmt(b['value'],1)+'pp，'+('悲观程度上升' if change<0 else '悲观程度下降' if change>0 else '没有变化')+'（调查情绪，非收益预测）。')
    crypto=series(capture,'crypto_fg')
    cutoff=(now.date()-timedelta(days=7)).isoformat()
    past=[o for o in crypto if o['observation_date']<=cutoff]
    if past and crypto:
        a,b=past[-1],crypto[-1]
        summary.append('Crypto F&G '+fmt(a['value'],0)+'→'+fmt(b['value'],0)+'；最新 '+b.get('classification','')+'，'+('风险偏好降温' if b['value']<a['value'] else '风险偏好回升' if b['value']>a['value'] else '维持不变')+'（情绪解读）。')
    cr=next((r for r in capture['sources'] if r['id']=='comex'),{})
    cs=cr.get('details',{}).get('snapshot',{})
    if cs.get('registered_change_20d_pct') is not None:
        summary.append('Registered 20D '+fmt(cs['registered_change_20d_pct'],3,True)+'%；'+('持续观察库存收缩' if cs['registered_change_20d_pct']<0 else '观察库存增加')+'，不单独推断交割短缺。')
    if summary:
        lines += ['## 本周最重要变化']+['- '+x for x in summary[:3]]
    lines.append('趋势解释：变化方向可核验；“改善/恶化”不自动等同风险增减。三项情绪共振阈值未定义、拍卖后收益率反应未建立可核验事件窗口，均待确认。')
    lines += ['## Gold库存与现金流动性']
    if cs.get('available'):
        lines.append('Activity '+str(cs.get('activity_date'))+' / Report '+str(cs.get('report_date'))+'｜Ratio '+fmt(cs.get('registered_ratio'),3)+'%｜读取 '+cr.get('status','待确认')+'｜库存风险 '+str(cs.get('status')))
        lines += ['|分类|当前 M oz|5D|20D|','|---|---:|---:|---:|']
        for label,key,prefix in [('Total','total_oz',''),('Registered','registered_oz','registered_'),('Eligible','eligible_oz','eligible_')]:
            changes=[cs.get(prefix+f'change_{n}d_pct') for n in (5,20)]
            lines.append('|'+label+'|'+fmt(cs[key]/1e6,3)+'|'+'|'.join(fmt(x,3,True)+'%' if x is not None else '暂不可算' for x in changes)+'|')
        lines.append('四窗口、基准日与衔接异常见当天晨报和JSON。官方最新发布状态'+('已确认' if cs.get('is_latest_confirmed') else '未独立确认')+'；Pledged已包含Registered，Eligible下降不证明短缺。')
        lines.append('[本次COMEX同提交快照]('+cr['details']['source_json']+')')
    else:
        lines.append('COMEX待确认；缺失不填0。')
    a=latest(capture,'mmf_assets_usd');delta=value(capture,'mmf_weekly_asset_change_usd')
    lines.append('ICI总资产 $'+fmt(a['value']/1e12 if a else None,5)+'T；周资产变化 $'+fmt(delta/1e9 if delta is not None else None,2,True)+'B。'+dates(a)+'。资产变化不等于净流入；3个月流趋势待积累。')
    lines += ['## Treasury / Fed']+treasury_lines(capture)
    lines += ['## Crypto Regulatory Timeline（国会行动日／机构发布日期）']
    items=timeline(capture)
    if not items:
        lines.append('本次已读取且可筛选的官方源中，没有确认到符合条件的条目；覆盖不完整，不能解释为本周无监管变化。')
    for item in items:
        status=STATUS.get(item['legal_status'],'官方公告候选／法律状态待确认')
        effective=item.get('effective_date')
        if item['legal_status']=='Rule' and effective:
            status='正式规则，'+('尚未生效' if effective>now.date().isoformat() else '已到所载生效日期，修订状态另核验')
        lines.append('- '+item['timeline_date']+'｜['+item['title'].replace('[','(').replace(']',')')+']('+item['url']+')｜'+item['source']+'｜'+status+'｜生效 '+str(effective or '待核验')+'；行动/事件日期 '+str(item.get('event_date') or '未另提供')+(('｜[正式PDF]('+item['official_pdf']+')') if item.get('official_pdf') else ''))
        if item.get('topics'):
            lines.append('主题：'+' / '.join(item['topics'])+'（确定性主题归类，不是价格影响结论）。')
    lines += ['## Congress：指定法案的官方状态']
    for key,label in [('clarity_bill','CLARITY'),('genius_bill','GENIUS')]:
        receipt=next((r for r in capture['sources'] if r['id']==key),{})
        d=receipt.get('details',{})
        if receipt.get('status')!='OK' or not d.get('latest_action'):
            lines.append(label+'：待确认（官方行动源未取得）。');continue
        a=d['latest_action'];laws=d.get('laws',[])
        state='存在成法记录：'+', '.join(str(x['type'])+' '+str(x['number']) for x in laws) if d['enactment_record']=='ENACTED' else '当前官方文件未见成法记录'
        identity=d['bill_identity']
        lines.append(label+'｜第'+identity['congress']+'届 '+identity['type']+identity['number']+'｜'+state+'｜[官方BILLSTATUS]('+receipt['url']+')')
        lines.append('最新已登记行动 '+a['date']+'：'+a['text']+'；本周行动 '+str(d['actions_in_window'])+'条。文件更新 '+str(d.get('bulk_updated_at') or '未提供')+'，本次读取 '+receipt['fetched_at_utc']+'。成法与实施规则、生效日期分开。')
    review=[]
    for receipt in capture['sources']:
        for i in receipt.get('details',{}).get('items',[]):
            day=timeline_day(i)
            if i.get('review_candidate') and not i.get('topic_signal') and day and (now.date()-timedelta(days=7)).isoformat()<=day<now.date().isoformat():
                review.append('- '+day+'｜['+i['title']+']('+i['url']+')｜官方公告候选：仅有Feed元数据，Crypto相关正文尚未核验，不当作已生效规则。')
    if review:lines += ['## 待正文核验的监管线索']+review[:5]
    coverage={r['id']:r['status'] for r in capture['sources'] if r['id'] in ['sec','cftc','fed','occ','treasury_news','congress','clarity_bill','genius_bill','whitehouse','federal_register']}
    lines.append('来源覆盖：'+json.dumps(coverage,ensure_ascii=False)+'。Federal Register按完整日期窗口有界分页后本地筛选；Congress指定法案行动记录与一般发布Feed分开。机构时间戳转美东日期，FR用原刊登日期；未知事件日不猜。关键词筛选及新法案发现仍可能遗漏。')
    lines += ['## 下周已知事件与风险']+event_lines(capture,True)
    deadlines=regulatory_upcoming(capture)
    lines += deadlines if deadlines else ['下周监管生效/意见截止节点：本次结构化官方记录未确认到；不等于没有节点。']
    lines += ['## 结构性影响与未决问题',
              '事实：上列公告的发布日期和Federal Register文种可追溯。解读：标题与文种不足以证明已通过、已生效或市场因果关系。',
              '|资产|直接/间接影响|','|---|---|']
    for asset in ['BTC','ETH','Stablecoin','Tokenized Securities']:
        lines.append('|'+asset+'|'+asset_relevance(items,asset)+'|')
    lines.append('结构性监管变化以已列文种和生效日期为事实基础；标题主题关联不是完整法律影响评估，下周监管截止日缺少可核验信息时保留待确认。')
    lines.append('方法变更：免费确定性系统提供可审计数据与公告线索；不冒充原LLM的完整法律语义研究。详见METHOD_CHANGES.md。')
    lines += ['## 来源与质量','[完整来源登记](https://yydsdefi-cmyk.github.io/COMEX-Gold-Tracker/market/source_registry.json)｜[数据质量](https://yydsdefi-cmyk.github.io/COMEX-Gold-Tracker/market/quality.json)；各条目附原始官方链接。']
    return compose(lines)
