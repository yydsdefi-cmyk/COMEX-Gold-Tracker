"""Bounded, traceable regulatory discovery. No generated legal facts or paid models."""
import json
import re
from datetime import timedelta
from urllib.parse import urlencode
from .core import MYT,ET,parse_time

KEY=re.compile(r'\bbitcoin\b|\bethereum\b|\bether\b|\bcrypto(?:currency|currencies|assets?)?\b|stablecoin|tokeniz|tokenis|digital asset|\bGENIUS\b|\bCLARITY Act\b|Digital Asset Market Clarity|blockchain|24.?7 markets',re.I)
TOPICS=[(r'stablecoin|GENIUS','稳定币'),(r'tokeniz|tokenis','代币化证券'),(r'CLARITY Act|Digital Asset Market Clarity|digital asset.*market|crypto.*market structure','市场结构'),(r'derivative|24.?7','衍生品/交易时段'),(r'\bbitcoin\b','BTC'),(r'\bethereum\b','ETH')]


def topics(value):
    return [label for pattern,label in TOPICS if re.search(pattern,value,re.I)]


def status_from_title(title):
    # Staff statements/speeches about a proposal are still statements, not agency rulemaking.
    if re.search(r'\bstaff\b|guidance|statement|remarks|speech',title,re.I):return 'GuidanceOrSpeech'
    if re.search(r'examination priorities',title,re.I):return 'SupervisoryPriorities'
    if re.search(r'propos|seeks? (?:public )?comment|request.*comment',title,re.I):return 'ProposalAnnouncement'
    if re.search(r'final rule|finalizes|finalises',title,re.I):return 'FinalRuleAnnouncement'
    return 'UNRESOLVED'


def fr_page_url(now,page):
    end=now.astimezone(MYT).date();start=end-timedelta(days=7)
    # No text query: fetch the whole seven-day publication window, then filter locally.
    return 'https://www.federalregister.gov/api/v1/documents.json?'+urlencode({
        'conditions[publication_date][gte]':start.isoformat(),
        'conditions[publication_date][lte]':(end-timedelta(days=1)).isoformat(),
        'order':'oldest','per_page':100,'page':page})


def timeline_day(item):
    if item.get('event_date'):return item['event_date'][:10]
    raw=item.get('publication_date')
    if not raw:return None
    if len(raw)==10:return raw
    return parse_time(raw).astimezone(ET).date().isoformat()


def collect_register(now,downloader):
    from .core import digest,stamp
    from .parsers import parse_federal_register
    receipt={'id':'federal_register','url':fr_page_url(now,1),'kind':'official_metadata',
             'fetched_at_utc':stamp(now),'max_age_days':4,'status':'MISSING','observations':[],
             'details':{'items':[],'page_responses':[],'coverage_issues':[]}}
    d=receipt['details'];seen=set();expected=None
    try:
        for page in range(1,11):
            url=fr_page_url(now,page);body,meta=downloader(url);js=json.loads(body)
            pages=int(js['total_pages']);count=int(js['count'])
            if pages<0 or pages>10:raise ValueError('Federal Register window exceeds bounded 1000-document coverage')
            if expected is None:
                expected=(pages,count);receipt.update({k:meta[k] for k in ['fetched_at_utc','response_sha256']})
            elif expected!=(pages,count):raise ValueError('Federal Register page count changed mid-collection')
            d['page_responses'].append({'url':url,**meta})
            for r in js['results']:
                identity=r['document_number']
                if identity in seen:raise ValueError('Duplicate Federal Register document across pages')
                seen.add(identity)
                if not KEY.search(r['title']+' '+(r.get('abstract') or '')):continue
                _,details=parse_federal_register(json.dumps({'results':[r],'count':1,'total_pages':1}).encode(),now)
                for item in details['items']:
                    item['topics']=topics(r['title']+' '+(r.get('abstract') or ''))
                    item['search_response_sha256']=meta['response_sha256']
                    item['source_abstract']=r.get('abstract') or ''
                    d['items'].append(item)
            if page>=pages:break
        if expected and len(seen)!=expected[1]:raise ValueError('Federal Register result count incomplete')
        d.update(scanned_documents=len(seen),total_pages=expected[0] if expected else 0,coverage_complete=True,
                 window='previous seven complete source publication dates; no OR/stemming search semantics')
        receipt['status']='OK'
    except Exception as exc:
        d['coverage_complete']=False;d['coverage_issues'].append(type(exc).__name__+': '+str(exc)[:250])
        receipt['status']='PARTIAL' if d['items'] or d['page_responses'] else 'MISSING'
        receipt['error']=str(exc)[:300]
    # Enrichment failures keep already verified search facts, but don't imply known effective dates.
    for item in d['items'][:20]:
        url='https://www.federalregister.gov/api/v1/documents/'+item['document_number']+'.json'
        try:
            body,meta=downloader(url);doc=json.loads(body)
            if doc['document_number']!=item['document_number'] or doc['type']!=item['legal_status']:
                raise ValueError('Federal Register detail identity/type mismatch')
            item.update(effective_date=doc.get('effective_on'),comments_close_on=doc.get('comments_close_on'),
                        official_pdf=doc.get('pdf_url'),action=doc.get('action'),
                        detail_response_sha256=meta['response_sha256'],detail_fetched_at_utc=meta['fetched_at_utc'])
        except Exception as exc:item['detail_error']=type(exc).__name__+': '+str(exc)[:250]
    if len(d['items'])>20:d['coverage_issues'].append('Only first 20 relevant documents received detail enrichment')
    return receipt



def asset_relevance(items,asset):
    """Subject-matter relevance, never a price forecast or inferred new legal duty."""
    texts=[i['title']+' '+i.get('source_abstract','')+' '+i.get('summary','') for i in items]
    specific={'BTC':r'\bbitcoin\b|\bBTC\b','ETH':r'\bethereum\b|\bether\b|\bETH\b',
              'Stablecoin':r'stablecoin|GENIUS Act','Tokenized Securities':r'(?:tokeniz|tokenis).*(?:securit|stock|equiti|bond)|(?:securit|stock|equiti|bond).*(?:tokeniz|tokenis)'}
    if any(re.search(specific[asset],value,re.I) for value in texts):
        return '直接相关主题：官方标题/摘要明确涉及该资产或规则对象；具体义务与生效范围仍须核正式文件。'
    if asset in ('BTC','ETH') and any(KEY.search(i['title']+' '+i.get('source_abstract','')) for i in items):
        return '间接影响可能：加密资产交易/中介或稳定币生态事项；尚未证实该币种新增专属义务（推断，不是价格方向）。'
    return '未确认本周直接法律影响；本次未查到不等于不存在。'
