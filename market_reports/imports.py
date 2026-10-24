"""Preserve historical exports with explicit snapshot dates and unverified provenance."""
import argparse
import csv
import hashlib
import html
import io
import json
import re
from datetime import date
from decimal import Decimal, InvalidOperation
from pathlib import Path
from .core import atomic, encoded

FIELDS = ['index', '日期', 'AAII多空差(pp)', 'CNN恐惧贪婪', 'VIX', '加密恐惧贪婪', 'COMEX Registered(M oz)']
METRICS = [('AAII多空差(pp)', 'aaii_spread', 'pp', -100, 100),
           ('CNN恐惧贪婪', 'cnn_fg', '点', 0, 100),
           ('VIX', 'vix', '点', 0, None),
           ('加密恐惧贪婪', 'crypto_fg', '点', 0, 100),
           ('COMEX Registered(M oz)', 'comex_registered', 'M oz', 0, None)]
NOTES = ['日期沿用旧导出的每日快照日期，不能直接当作各指标的观测日或发布日期。',
         'AAII是周度指标；每日重复值表示当时沿用的周值，不能当作每日调查。',
         'COMEX日期与Activity Date/Report Date尚未逐行核对；M oz为百万盎司。',
         '旧导出未逐项重新回源核验；空白保留为缺失，不填0；分析时优先采用可追溯的官方源历史。']


def parse_csv(text):
    reader = csv.DictReader(io.StringIO(text))
    if reader.fieldnames != FIELDS:
        raise ValueError('Unsupported historical export columns')
    rows = []
    seen = set()
    for raw in reader:
        if None in raw or any(v is None for v in raw.values()):
            raise ValueError('Malformed historical row')
        if not re.fullmatch(r'[0-9]+', raw['index']):
            raise ValueError('Invalid historical row index')
        day = raw['日期']
        if date.fromisoformat(day).isoformat() != day or day in seen:
            raise ValueError('Invalid or duplicate snapshot date')
        seen.add(day)
        values = {}
        for col, key, unit, low, high in METRICS:
            value = raw[col].strip()
            if not value:
                values[key] = None
                continue
            try:
                number = Decimal(value)
            except InvalidOperation as error:
                raise ValueError('Non-numeric historical cell') from error
            if not number.is_finite() or number < low or (high is not None and number > high):
                raise ValueError('Historical cell outside supported range')
            values[key] = value
        rows.append({'snapshot_date': day, 'values': values})
    if not rows:
        raise ValueError('Empty historical export')
    return sorted(rows, key=lambda row: row['snapshot_date'])


def import_csv(text, data_dir, source_name):
    text = text.lstrip('\ufeff').replace('\r\n', '\n').replace('\r', '\n')
    if not text.endswith('\n'):
        text += '\n'
    rows = parse_csv(text)
    if Path(source_name).name != source_name or len(source_name) > 160:
        raise ValueError('Use a public source filename without a local path')
    sha = hashlib.sha256(text.encode()).hexdigest()
    identity = 'legacy-' + sha[:16]
    bundle = {'schema_version': 1, 'import_id': identity, 'source_name': source_name,
              'source_kind': 'historical_user_export', 'verification_status': 'LEGACY_NOT_REVERIFIED',
              'normalized_csv_sha256': sha, 'csv_utf8': text, 'rows': rows,
              'date_semantics': 'snapshot_date_as_recorded_not_individual_observation_or_publication_date',
              'notes': NOTES}
    output = Path(data_dir) / 'imports' / (identity + '.json')
    content = encoded(bundle)
    if output.exists() and output.read_bytes() != content:
        raise ValueError('Conflicting historical import; existing object was preserved')
    if not output.exists():
        atomic(output, content)
    return bundle


def load_imports(data_dir):
    result = []
    for path in sorted((Path(data_dir) / 'imports').glob('*.json')):
        bundle = json.loads(path.read_text())
        sha = hashlib.sha256(bundle['csv_utf8'].encode()).hexdigest()
        identity = 'legacy-' + sha[:16]
        if (not re.fullmatch(r'legacy-[a-f0-9]{16}', bundle['import_id'])
                or path.stem != identity or bundle['import_id'] != identity
                or bundle['normalized_csv_sha256'] != sha
                or bundle['verification_status'] != 'LEGACY_NOT_REVERIFIED'
                or bundle['rows'] != parse_csv(bundle['csv_utf8'])):
            raise ValueError('Historical import identity/content mismatch: ' + path.name)
        result.append(bundle)
    return result


def publish_imports(data_dir, target, page):
    bundles = load_imports(data_dir)
    if not bundles:
        return ''
    links = '<details><summary>导入的旧数据（历史快照）</summary>'
    index = []
    for bundle in bundles:
        identity = bundle['import_id']
        destination = Path(target) / 'imports' / identity
        body = '<h1>旧指标历史快照</h1><p class="warn">旧导出保留，尚未逐项重新回源核验；不是当日新生成的完整晨报。</p>'
        body += '<p>来源：' + html.escape(bundle['source_name']) + '</p>'
        body += '<p><a href="data.csv">下载原导出CSV（仅规范换行）</a> · <a href="data.json">读取JSON</a></p>'
        body += ''.join('<p class="muted">' + html.escape(note) + '</p>' for note in NOTES)
        links += '<p>' + html.escape(bundle['source_name']) + '</p>'
        for row in bundle['rows']:
            day = row['snapshot_date']
            body += '<h2 id="snapshot-' + day + '">' + day + '</h2><div class="table-scroll"><table class="compact-three"><tr><th>指标</th><th>旧导出值</th><th>单位</th></tr>'
            for label, key, unit, low, high in METRICS:
                value = row['values'][key]
                body += '<tr><td>' + html.escape(label) + '</td><td>' + html.escape(value if value is not None else '缺失') + '</td><td>' + html.escape(unit) + '</td></tr>'
            body += '</table></div>'
            links += '<p><a href="imports/' + identity + '/index.html#snapshot-' + day + '">' + day + ' 旧指标快照</a></p>'
        atomic(destination / 'index.html', page('旧指标历史快照', body, base='../../'))
        atomic(destination / 'data.csv', bundle['csv_utf8'].encode())
        atomic(destination / 'data.json', encoded(bundle))
        index.append({'import_id': identity, 'source_name': bundle['source_name'],
                      'first_date': bundle['rows'][0]['snapshot_date'], 'last_date': bundle['rows'][-1]['snapshot_date'],
                      'row_count': len(bundle['rows']), 'verification_status': bundle['verification_status'],
                      'json': identity + '/data.json', 'csv': identity + '/data.csv'})
    atomic(Path(target) / 'imports/index.json', encoded({'schema_version': 1, 'imports': index}))
    return links + '<p>这些快照独立保存；不自动并入已回源的history.csv，不用于新报告的风险阈值或定时完成判定。</p></details>'


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('csv_file', type=Path)
    parser.add_argument('--data-dir', type=Path, default=Path('market_data'))
    args = parser.parse_args()
    result = import_csv(args.csv_file.read_text(encoding='utf-8-sig'), args.data_dir, args.csv_file.name)
    print(result['import_id'], len(result['rows']), result['verification_status'])
