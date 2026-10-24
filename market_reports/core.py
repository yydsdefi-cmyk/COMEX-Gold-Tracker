import csv
import hashlib
import io
import json
import math
import os
from datetime import datetime, timedelta, timezone
from pathlib import Path
from zoneinfo import ZoneInfo

UTC = timezone.utc
MYT = ZoneInfo('Asia/Kuala_Lumpur')
ET = ZoneInfo('America/New_York')
ROOT = Path(__file__).resolve().parents[1]
DATA = ROOT / 'market_data'


def stamp(value):
    return value.astimezone(UTC).isoformat()


def parse_time(value):
    d = datetime.fromisoformat(value.replace('Z', '+00:00'))
    if d.tzinfo is None:
        raise ValueError('Timestamp has no timezone')
    return d


def number(x):
    v = float(str(x).replace(',', '').replace('%', ''))
    if not math.isfinite(v):
        raise ValueError('Non-finite value')
    return v


def digest(b):
    return hashlib.sha256(b).hexdigest()


def encoded(obj):
    return (json.dumps(obj, ensure_ascii=False, sort_keys=True, indent=2, allow_nan=False) + '\n').encode()


def atomic(path, body):
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    tmp = path.with_name(path.name + '.tmp')
    with tmp.open('wb') as f:
        f.write(body if isinstance(body, bytes) else body.encode())
        f.flush()
        os.fsync(f.fileno())
    tmp.replace(path)


def immutable(path, body):
    path = Path(path)
    if path.exists() and path.read_bytes() != body:
        raise ValueError('Immutable archive conflict: ' + str(path))
    if not path.exists():
        atomic(path, body)


def srf_level(usd):
    v = number(usd)
    if v < 0:
        raise ValueError('Negative usage')
    return 'Normal' if v < 10e9 else 'Stress' if v < 50e9 else 'Red Alert' if v <= 100e9 else 'Severe'


def inventory_level(pct):
    if pct is None:
        return 'UNKNOWN'
    return 'RED' if pct < -5 else 'ORANGE' if pct < -3 else 'YELLOW' if pct < -1 else 'NORMAL'


def assess_date(observation_date, now, max_days):
    age = (now.date() - datetime.fromisoformat(observation_date[:10]).date()).days
    if age < 0:
        return 'FUTURE'
    return 'STALE' if age > max_days else 'OK'


def observation(metric, value, date, unit, published=None, **kw):
    return dict(metric=metric, value=number(value), observation_date=date[:10],
                publication_date=published, unit=unit, **kw)


def verify_bundle(folder):
    folder = Path(folder)
    manifest = json.loads((folder / 'MANIFEST.json').read_text())
    actual = {p.relative_to(folder).as_posix() for p in folder.rglob('*') if p.is_file() and p.name != 'MANIFEST.json'}
    if actual != set(manifest['sha256']):
        raise ValueError('Report archive file set mismatch')
    for rel, expected in manifest['sha256'].items():
        p = (folder / rel).resolve()
        if not p.is_relative_to(folder.resolve()) or digest(p.read_bytes()) != expected:
            raise ValueError('Report archive hash mismatch: ' + rel)
    return manifest


def commit_bundle(folder, files):
    """Complete immutable content-addressed revision first; pointer is written last."""
    hashes = {k: digest(v if isinstance(v, bytes) else v.encode()) for k, v in files.items()}
    revision = digest(encoded(hashes))[:20]
    dest = Path(folder) / revision
    for name, body in files.items():
        immutable(dest / name, body if isinstance(body, bytes) else body.encode())
    immutable(dest / 'MANIFEST.json', encoded({'sha256': hashes, 'revision': revision}))
    verify_bundle(dest)
    return revision


def rebuild_history(data):
    """CSV is a derived view; immutable captures keep every revision of every value."""
    data = Path(data)
    rows = {}
    for p in sorted((data / 'captures').glob('*.json')):
        capture = json.loads(p.read_text())
        for o in capture['observations']:
            # source/metric/date/revision retained; repeated reads of identical values collapse.
            k = (o['source'], o['metric'], o['observation_date'], str(o['value']), str(o.get('publication_date')))
            row = {k: o.get(k) for k in ['source','metric','observation_date','publication_date','value','unit','fetched_at_utc','response_sha256','quality']}
            rows.setdefault(k, row)
    fields = ['source','metric','observation_date','publication_date','value','unit','fetched_at_utc','response_sha256','quality']
    stream = io.StringIO(newline='')
    w = csv.DictWriter(stream, fieldnames=fields)
    w.writeheader()
    w.writerows(rows[k] for k in sorted(rows))
    atomic(data / 'history.csv', stream.getvalue())
    return len(rows)


def due_reports(now, data=DATA):
    local = now.astimezone(MYT)
    due = []
    for kind, hour in [('daily',8), ('weekly',10)]:
        if local.hour < hour or (kind == 'weekly' and local.weekday() != 5):
            continue
        day = local.date().isoformat()
        pointer = Path(data) / 'reports' / kind / day / 'latest.json'
        if not pointer.exists():
            due.append(kind)
            continue
        info = json.loads(pointer.read_text())
        bundle = pointer.parent / info['revision']
        verify_bundle(bundle)
        # Retry degraded reports within 4 hours; don't refetch healthy duplicate runs.
        if info['degraded'] and local.hour < hour + 4:
            due.append(kind)
    return due
