#!/usr/bin/env python3
"""download_binance.py: fetch Binance USD-M futures public daily files from data.binance.vision, check each against Binance's own
.CHECKSUM file, and write a manifest (url, file, bytes, sha256, checksum_ok). Standard Python only.

  python3 -B desk/data/download_binance.py <raw folder> --coins BTC,ETH,SOL --first 20250901 --last 20251231 \
      --kinds klines_1m,metrics [--agg-days BTC:20251001,ETH:20251105] [--max-mb 2000] [--dry]

Files land at <raw folder>/<kind>/<SYMBOL>/<file>.zip (never over an existing file: an existing file is re-checked, not fetched again).
MANIFEST.tsv in <raw folder> gets one row per file (appended; a file already listed is not listed twice). A file whose sha256 differs
from Binance's CHECKSUM is kept as <file>.bad and the run ends with exit 3. --max-mb stops before the total would pass the limit
(sizes are read first with HEAD requests). A missing day on the server (404) is listed as MISSING, never invented.
Only https://data.binance.vision/data/futures/um/daily/ is read; nothing is uploaded."""
import argparse, datetime, hashlib, os, sys, urllib.error, urllib.request

BASE = 'https://data.binance.vision/data/futures/um/daily/'
KIND = {'klines_1m': ('klines/{S}/1m/{S}-1m-{D}.zip', 'klines_1m'), 'metrics': ('metrics/{S}/{S}-metrics-{D}.zip', 'metrics'),
        'aggTrades': ('aggTrades/{S}/{S}-aggTrades-{D}.zip', 'aggTrades')}


def days(first, last):
    d = datetime.datetime.strptime(first, '%Y%m%d').date(); e = datetime.datetime.strptime(last, '%Y%m%d').date()
    if e < d:
        raise SystemExit('REFUSED last before first')
    while d <= e:
        yield d.strftime('%Y-%m-%d'); d += datetime.timedelta(days=1)


def head(url):
    try:
        with urllib.request.urlopen(urllib.request.Request(url, method='HEAD'), timeout=60) as r:
            return int(r.headers.get('Content-Length') or 0)
    except urllib.error.HTTPError as e:
        if e.code == 404:
            return None
        raise


def get(url):
    with urllib.request.urlopen(url, timeout=300) as r:
        return r.read()


def sha256_file(p):
    h = hashlib.sha256()
    with open(p, 'rb') as f:
        for b in iter(lambda: f.read(1 << 20), b''):
            h.update(b)
    return h.hexdigest()


def main(argv):
    ap = argparse.ArgumentParser()
    ap.add_argument('raw'); ap.add_argument('--coins', required=True); ap.add_argument('--first', required=True)
    ap.add_argument('--last', required=True); ap.add_argument('--kinds', default='klines_1m,metrics')
    ap.add_argument('--agg-days', default=''); ap.add_argument('--max-mb', type=float, default=2000); ap.add_argument('--dry', action='store_true')
    a = ap.parse_args(argv)
    want = []
    for k in [x for x in a.kinds.split(',') if x]:
        if k not in KIND:
            raise SystemExit('REFUSED kind %s (one of %s)' % (k, ', '.join(KIND)))
        for c in a.coins.split(','):
            for d in days(a.first, a.last):
                want.append((k, c + 'USDT', d))
    for x in [x for x in a.agg_days.split(',') if x]:
        c, d = x.split(':')
        want.append(('aggTrades', c + 'USDT', '%s-%s-%s' % (d[:4], d[4:6], d[6:])))
    mf = os.path.join(a.raw, 'MANIFEST.tsv')
    listed = set()
    if os.path.isfile(mf):
        listed = {l.split('\t')[1] for l in open(mf) if l.strip() and not l.startswith(('#', 'url'))}
    plan, total = [], 0
    for k, s, d in want:
        rel = KIND[k][0].format(S=s, D=d)
        n = head(BASE + rel)
        plan.append((k, s, d, rel, n)); total += n or 0
    print('PLAN %d files, %d missing on the server, %.1f MB' % (len(plan), sum(1 for p in plan if p[4] is None), total / 1e6))
    if total / 1e6 > a.max_mb:
        print('REFUSED: %.1f MB is over --max-mb %.0f' % (total / 1e6, a.max_mb)); return 2
    if a.dry:
        return 0
    os.makedirs(a.raw, exist_ok=True)
    new = not os.path.isfile(mf)
    bad = 0
    with open(mf, 'a') as m:
        if new:
            m.write('# MANIFEST.tsv (download_binance.py): every raw file, its source url, size and sha256; checksum_ok = equal to Binance\'s .CHECKSUM\n')
            m.write('url\tfile\tbytes\tsha256\tchecksum_ok\tkind\tsymbol\tday\n')
        for k, s, d, rel, n in plan:
            dst = os.path.join(a.raw, rel.replace('klines/%s/1m/' % s, 'klines_1m/%s/' % s))
            if n is None:
                key = os.path.relpath(dst, a.raw)
                if key not in listed:
                    m.write('%s\t%s\t0\t-\tMISSING\t%s\t%s\t%s\n' % (BASE + rel, key, k, s, d)); listed.add(key)
                continue
            os.makedirs(os.path.dirname(dst), exist_ok=True)
            if not os.path.isfile(dst):
                data = get(BASE + rel)
                with open(dst + '.part', 'wb') as f:
                    f.write(data)
                os.rename(dst + '.part', dst)
            want_sha = get(BASE + rel + '.CHECKSUM').decode().split()[0]
            got = sha256_file(dst)
            ok = got == want_sha
            if not ok:
                os.rename(dst, dst + '.bad'); bad += 1
            key = os.path.relpath(dst, a.raw)
            if key not in listed:
                m.write('%s\t%s\t%d\t%s\t%s\t%s\t%s\t%s\n' % (BASE + rel, key, os.path.getsize(dst + ('' if ok else '.bad')), got,
                                                            'OK' if ok else 'BAD', k, s, d)); listed.add(key)
    print('DONE %d files, %d bad checksums; manifest %s' % (len(plan), bad, mf))
    return 3 if bad else 0


if __name__ == '__main__':
    sys.exit(main(sys.argv[1:]))
