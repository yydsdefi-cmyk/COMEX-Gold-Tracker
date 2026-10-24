"""Small escaped Markdown subset; no external scripts, fonts, or analytics."""
import html
import json
import re
import shutil
from datetime import datetime
from pathlib import Path
from .core import atomic, encoded, digest, verify_bundle
from .schedule import CLOCK_JS

CSS='''
:root{color-scheme:light;--ink:#16252e;--muted:#536975;--line:#dbe5e9;--accent:#087c75;--bg:#f3f7f8}
*{box-sizing:border-box}body{margin:0;background:var(--bg);font:15px/1.65 system-ui,-apple-system,BlinkMacSystemFont,"Segoe UI",sans-serif;color:var(--ink)}
main{max-width:860px;margin:auto;padding:22px 18px 60px}header{border-bottom:3px solid var(--accent);padding:14px 0 22px}h1{font-size:26px;line-height:1.3;letter-spacing:-.5px}h2{font-size:18px;margin:30px 0 10px;padding-top:15px;border-top:1px solid var(--line)}a{color:#086a73;overflow-wrap:anywhere}p,li{overflow-wrap:anywhere}ul{padding-left:22px}nav{display:flex;flex-wrap:wrap;gap:12px;margin:14px 0}nav a,.card{background:white;padding:12px 16px;border:1px solid var(--line);border-radius:12px;text-decoration:none}.card{margin:14px 0}.muted{color:var(--muted)}.warn{background:#fff0d6;border-left:4px solid #b7791f;padding:12px 14px;border-radius:5px}.table-scroll{max-width:100%;overflow-x:auto;margin:14px 0;background:white;border-radius:8px;border:1px solid var(--line)}table{border-collapse:collapse;font-size:13px;width:100%;min-width:380px}th,td{padding:9px 10px;border-bottom:1px solid var(--line);text-align:left;white-space:normal}th{background:#e9f2f3}pre{white-space:pre-wrap;overflow-wrap:anywhere}small{color:var(--muted)}details{background:#fff;padding:12px;border-radius:8px;margin:12px 0}summary{cursor:pointer;font-weight:600}.overview p{margin:5px 0}@media(max-width:400px){main{padding:14px 12px 40px}h1{font-size:23px}body{font-size:14px}th,td{padding:7px 8px}}
'''
CSS+='\n.report-clock{font-size:13px}.report-clock[data-state="CURRENT"]{background:#e8f4f1;border-left-color:#087c75}\n'


def freshness_banner(kind,day,generated):
    fields={'kind':kind,'report-date':day,'generated':generated}
    attrs=' '.join('data-'+k+'="'+html.escape(v,quote=True)+'"' for k,v in fields.items())
    return '<div class="warn report-clock" role="status" '+attrs+'>报告日期 '+html.escape(day or '缺失')+'；MYT目标：每日08:00／周六10:00。启用JavaScript可按设备时钟检查本期是否到期；来源质量另列。</div>'


def inline(s):
    s=html.escape(s)
    s=re.sub(r'\[([^\]]+)\]\(([^\s)]+)\)',lambda m: '<a href="'+m[2]+'">'+m[1]+'</a>' if m[2].startswith(('https://','../','./')) else m[1],s)
    return re.sub(r'\*\*([^*]+)\*\*',r'<strong>\1</strong>',s)


def markdown(s, compact=False):
    lines=s.splitlines();out=[];i=0
    while i<len(lines):
        line=lines[i].strip()
        if not line:
            i+=1;continue
        if line.startswith('|'):
            rows=[]
            while i<len(lines) and (lines[i].strip().startswith('|') or not lines[i].strip()):
                if lines[i].strip():rows.append(lines[i].strip())
                i+=1
            out.append('<small>表格可左右滑动查看全部列</small><div class="table-scroll"><table>')
            for n,row in enumerate(rows):
                if re.fullmatch(r'[|:\-\s]+',row):continue
                tag='th' if n==0 else 'td'
                out.append('<tr>'+''.join('<'+tag+'>'+inline(c.strip())+'</'+tag+'>' for c in row.strip('|').split('|'))+'</tr>')
            out.append('</table></div>');continue
        if line.startswith('#'):
            n=len(line)-len(line.lstrip('#'));n=min(n,4)
            out.append(f'<h{n}>'+inline(line.lstrip('# '))+f'</h{n}>')
        elif line.startswith('- '):
            out.append('<p>• '+inline(line[2:])+'</p>')
        else:
            out.append('<p>'+inline(line)+'</p>')
        i+=1
    result='\n'.join(out)
    if compact:
        sections=re.split(r'<h2>(.*?)</h2>',result)
        result=sections[0]
        for n in range(1,len(sections),2):
            title=sections[n];content=sections[n+1]
            if title=='7项总览':
                result+='<h2>'+title+'</h2><div class="overview">'+content+'</div>'
            else:
                result+='<details><summary>'+title+'</summary>'+content+'</details>'
    return result


def page(title,body,base='../',generated=None):
    generated=html.escape(generated or '')
    script='<script>'+CLOCK_JS+'</script>' if 'class="warn report-clock"' in body else ''
    return '<!doctype html><html lang="zh-Hans"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><meta name="color-scheme" content="light"><title>'+html.escape(title)+'</title><style>'+CSS+'</style></head><body><main><header><small>MARKET OBSERVATORY · 公开数据 / 可追溯</small><nav><a href="'+base+'index.html">报表首页</a><a href="'+base+'daily.html">晨报</a><a href="'+base+'weekly.html">周报</a><a href="'+base+'quality.json">质量</a></nav></header>'+body+'<footer><small>事实与解读分开 · 无付费API · 生成UTC '+generated+'</small></footer></main>'+script+'</body></html>'


def publish(data,site):
    data,site=Path(data),Path(site)
    target=site/'market'
    target.mkdir(parents=True,exist_ok=True)
    pointers=[]
    for p in sorted((data/'reports').glob('*/*/latest.json')):
        ptr=json.loads(p.read_text());bundle=p.parent/ptr['revision'];verify_bundle(bundle)
        kind=p.parent.parent.name;day=p.parent.name
        destination=target/'archive'/kind/day
        destination.mkdir(parents=True,exist_ok=True)
        for name in ['report.md','report.json','quality.json','MANIFEST.json']:
            shutil.copyfile(bundle/name,destination/name)
        md=(bundle/'report.md').read_text()
        atomic(destination/'index.html',page(kind+' '+day,'<p class="muted">历史档案：'+day+'，不是当前报告。</p>'+markdown(md,compact=True),base='../../../',generated=ptr['generated_at_utc']))
        pointers.append((kind,day,ptr,bundle))
    links=[]
    for kind in ['daily','weekly']:
        matches=[x for x in pointers if x[0]==kind]
        if not matches:
            links.append('<div class="card"><h2>'+('每日08:00 晨报' if kind=='daily' else '周六10:00 周报')+'</h2>'+freshness_banner(kind,'','')+'</div>');continue
        _,day,ptr,bundle=matches[-1]
        md=(bundle/'report.md').read_text()
        banner=freshness_banner(kind,day,ptr['generated_at_utc'])
        atomic(target/(kind+'.html'),page(kind,banner+markdown(md,compact=True),base='./',generated=ptr['generated_at_utc']))
        for ext in ['md','json']:
            shutil.copyfile(bundle/('report.'+ext),target/(kind+'.'+ext))
        links.append(f'<div class="card"><h2>{"每日08:00 晨报" if kind=="daily" else "周六10:00 周报"}</h2><p>{day} · {"部分来源待确认" if ptr["degraded"] else "数据检查通过"}</p>'+banner+f'<a href="{kind}.html">阅读报告 →</a> · <a href="{kind}.md">Markdown</a> · <a href="{kind}.json">JSON</a></div>')
    for name in ['history.csv','quality.json','source_registry.json','health.json']:
        if (data/name).exists():shutil.copyfile(data/name,target/name)
    gen=json.loads((data/'health.json').read_text())['last_generated_at_utc'] if (data/'health.json').exists() else ''
    body='<h1>市场反向指标与监管观察</h1><p class="muted">Malaysia time · 每日08:00 / 周六10:00<br>公开数据、确定性中文分析，持续独立于ChatGPT运行。</p><div class="warn" id="health">生成状态是静态快照；请核对报告日期。调度可能延迟，缺失/未核验不表示风险为零。</div>'+''.join(links)
    body+='<details><summary>历史档案与数据</summary><p><a href="history.csv">CSV历史序列</a> · <a href="source_registry.json">来源登记</a> · <a href="quality.json">质量报告</a> · <a href="../latest.json">原Gold Tracker JSON</a></p>'
    for kind,day,ptr,bundle in reversed(pointers):
        body+=f'<p><a href="archive/{kind}/{day}/index.html">{day} {kind}</a></p>'
    body+='</details><p class="muted">监管：官方公告与Federal Register文种可核验；完整法律语义与资产影响仍须正文核验。CNN被拒时保持缺失。此系统不自动生成交易建议。</p>'
    atomic(target/'index.html',page('市场观察',body,base='./',generated=gen))
    return len(pointers)
