#!/usr/bin/env python3
"""hl_funding_pull_v1.py (LAYERS, 23 Oct 2026; T04 RESEARCH_COST_MODEL C4; STRATEGY 13:31:02Z Q5: "download now under the owner's
standing yes"). RAW RECORD (protocol 3b): Hyperliquid's SETTLED hourly funding (public info API, type fundingHistory) per coin, as the
exchange gives it, into one TSV per coin and month: <out>/<COIN>/<YYYYMM>.tsv  columns coin, time_ms, funding_rate, premium (the API's
own decimal strings, unchanged), sorted by time, one row per time (a repeated time is dropped and counted). Written whole (tmp + replace)
and only for a month that has ENDED; a month file that exists is skipped (resume). MANIFEST_<first>_<last>.tsv: coin, month, rows,
first and last time, sha16. Not the 2025 store (hl_funding_2025 holds asset-context snapshots, a different source): this is the hourly
rate the exchange charged; its reader comes with it (read_month).
Gate: before EACH request team/FEED/stops/BACKFILL_GATE.txt must say RUN (labcore.jobgate.gate_wait); PAUSE past --gate-limit s: rc 4.
RECORDER_STATE (24 Oct, LIVE4 06:38Z / LAB1 MUST): when stops/RECORDER_STATE.txt exists beside the gate, it is the file waited on (re-read per request).
Pace: at most one request per --every s (default 3.0, LAB1 13:33:50Z MUST 1: HL's info budget is shared with the HL recorder and news).
  python3 -B hl_funding_pull_v1.py --coins AAVE,BTC --first 202601 --last 202605 --out DIR [--gate FILE] [--gate-limit S] [--every S]
  python3 -B hl_funding_pull_v1.py --selftest"""
import argparse, calendar, hashlib, json, os, sys, tempfile, time, urllib.request
sys.path.insert(0, '<LAB_REPO>/forensics/team/RESEARCH/tools')
from labcore.jobgate import gate_wait   # LAB1 13:33:50Z MUST 2: the one gate (labcore)
API = 'https://api.hyperliquid.xyz/info'
GATE = '<LAB_REPO>/forensics/team/FEED/stops/BACKFILL_GATE.txt'
HOUR_MS = 3_600_000


def http_fetch(coin, t0, t1):
    body = json.dumps({'type': 'fundingHistory', 'coin': coin, 'startTime': t0, 'endTime': t1}).encode()
    for i in range(4):
        try:
            req = urllib.request.Request(API, data=body, headers={'Content-Type': 'application/json', 'User-Agent': 'research-provenance-pull'})
            with urllib.request.urlopen(req, timeout=60) as r:
                return json.loads(r.read())
        except Exception:
            time.sleep(5 * (i + 1))
    raise RuntimeError('fetch failed %s %d' % (coin, t0))


def month_ms(m):
    y, mo = int(m[:4]), int(m[4:]); a = calendar.timegm((y, mo, 1, 0, 0, 0)) * 1000
    y2, mo2 = (y + 1, 1) if mo == 12 else (y, mo + 1)
    return a, calendar.timegm((y2, mo2, 1, 0, 0, 0)) * 1000 - 1


def months(first, last):
    out, m = [], first
    while m <= last:
        out.append(m); y, mo = int(m[:4]), int(m[4:]); m = '%04d%02d' % ((y + 1, 1) if mo == 12 else (y, mo + 1))
    return out


def pull_month(coin, m, fetch, wait, every, sleep=time.sleep):
    """every row of the month: pages of the API (up to 500 a reply) from the last time + 1; (rows, dropped repeats)"""
    a, b = month_ms(m); rows = {}; t = a; drop = 0
    while t <= b:
        if not wait():
            return None, drop
        page = fetch(coin, t, b); sleep(every)
        if not page:
            break
        for r in page:
            k = int(r['time'])
            if a <= k <= b:
                if k in rows:
                    drop += 1
                rows[k] = (str(r['fundingRate']), str(r.get('premium', '')))
        nt = max(int(r['time']) for r in page) + 1
        if nt <= t:
            break
        t = nt
    return [(coin, k) + rows[k] for k in sorted(rows)], drop


def write_whole(p, text):
    os.makedirs(os.path.dirname(p), exist_ok=True); tmp = p + '.tmp_%d' % os.getpid()
    with open(tmp, 'x') as f:
        f.write(text); f.flush(); os.fsync(f.fileno())
    os.replace(tmp, p)


def run(coins, first, last, out, fetch=http_fetch, wait=lambda: True, every=1.0, now_ms=None, sleep=time.sleep):
    now_ms = now_ms if now_ms is not None else int(time.time() * 1000); man = []; rc = 0
    for coin in coins:
        for m in months(first, last):
            p = os.path.join(out, coin, '%s.tsv' % m)
            if month_ms(m)[1] >= now_ms:
                man.append((coin, m, 'NOT_ENDED', '', '', '')); continue
            if os.path.exists(p):
                man.append((coin, m, 'SKIP_EXISTS', '', '', hashlib.sha256(open(p, 'rb').read()).hexdigest()[:16])); continue
            rows, drop = pull_month(coin, m, fetch, wait, every, sleep)
            if rows is None:
                man.append((coin, m, 'GATE_PAUSE', '', '', '')); rc = 4; break
            t = 'coin\ttime_ms\tfunding_rate\tpremium\n' + ''.join('%s\t%d\t%s\t%s\n' % r for r in rows)
            write_whole(p, t)
            man.append((coin, m, '%d rows, %d repeats dropped' % (len(rows), drop), str(rows[0][1]) if rows else '', str(rows[-1][1]) if rows else '',
                        hashlib.sha256(t.encode()).hexdigest()[:16]))
        if rc:
            break
    write_whole(os.path.join(out, 'MANIFEST_%s_%s.tsv' % (first, last)), 'coin\tmonth\tstate\tfirst_ms\tlast_ms\tsha16\n' + ''.join('\t'.join(r) + '\n' for r in man))
    return rc, man


def read_month(out, coin, m):
    """the reader: [(time_ms, funding_rate float, premium float or None)]"""
    rs = []
    for l in open(os.path.join(out, coin, '%s.tsv' % m)):
        if l.startswith('coin\t'):
            continue
        c = l.rstrip('\n').split('\t'); rs.append((int(c[1]), float(c[2]), float(c[3]) if c[3] else None))
    return rs


def selftest():
    res = []; a, _ = month_ms('202601')
    def fake(coin, t0, t1, calls=[]):
        calls.append(t0); hrs = [h for h in range(a, month_ms('202602')[1] + 1, HOUR_MS) if t0 <= h <= t1]
        page = hrs[:500]
        return [{'coin': coin, 'fundingRate': '0.0000125', 'premium': '-0.0001', 'time': h} for h in page] + ([{'coin': coin, 'fundingRate': '0.0000125', 'premium': '-0.0001', 'time': page[0]}] if page else [])
    with tempfile.TemporaryDirectory() as t:
        rc, man = run(['BTC'], '202601', '202603', t, fake, every=0, now_ms=month_ms('202603')[0] + 5, sleep=lambda s: None)
        r1 = read_month(t, 'BTC', '202601'); r2 = read_month(t, 'BTC', '202602')
        res.append(('H1 pages of 500 joined: January 744 hours, February 672, sorted, one row per time', len(r1) == 744 and len(r2) == 672 and [x[0] for x in r1] == sorted({x[0] for x in r1})))
        res.append(('H2 a repeated time dropped and counted; the decimal kept as the API wrote it', '744 rows' in man[0][2] and 'repeats dropped' in man[0][2] and open(os.path.join(t, 'BTC', '202601.tsv')).read().split('\n')[1].split('\t')[2] == '0.0000125'))
        res.append(('H3 a month not ended (March) is not written', man[2][2] == 'NOT_ENDED' and not os.path.exists(os.path.join(t, 'BTC', '202603.tsv'))))
        s1 = open(os.path.join(t, 'BTC', '202601.tsv'), 'rb').read()
        rc2, man2 = run(['BTC'], '202601', '202602', t, lambda *x: (_ for _ in ()).throw(AssertionError('fetched')), every=0, now_ms=month_ms('202603')[0] + 5)
        res.append(('H4 resume: existing months skipped, nothing fetched, the file unchanged', rc2 == 0 and man2[0][2] == 'SKIP_EXISTS' and open(os.path.join(t, 'BTC', '202601.tsv'), 'rb').read() == s1))
    with tempfile.TemporaryDirectory() as t:
        rc, man = run(['BTC', 'ETH'], '202601', '202601', t, fake, wait=lambda: False, every=0, now_ms=month_ms('202603')[0])
        res.append(('H5 the gate on PAUSE: rc 4, nothing written but the manifest, no .tmp', rc == 4 and not os.path.exists(os.path.join(t, 'BTC')) and man[0][2] == 'GATE_PAUSE'))
    with tempfile.TemporaryDirectory() as t1, tempfile.TemporaryDirectory() as t2:
        for d in (t1, t2):
            run(['BTC'], '202601', '202601', d, fake, every=0, now_ms=month_ms('202603')[0], sleep=lambda s: None)
        res.append(('H6 determinism: two runs, the same bytes', open(os.path.join(t1, 'BTC', '202601.tsv'), 'rb').read() == open(os.path.join(t2, 'BTC', '202601.tsv'), 'rb').read()))
    for n, ok in res:
        print(('OK   ' if ok else 'FAIL ') + n)
    k = sum(1 for _, ok in res if ok); print('%d of %d OK' % (k, len(res)))
    return 0 if k == len(res) else 1


def main():
    if sys.argv[1:] == ['--selftest']:
        return selftest()
    ap = argparse.ArgumentParser(); ap.add_argument('--coins', required=True); ap.add_argument('--first', required=True); ap.add_argument('--last', required=True)
    ap.add_argument('--out', required=True); ap.add_argument('--gate', default=GATE); ap.add_argument('--gate-limit', type=float, default=3600.0); ap.add_argument('--every', type=float, default=3.0)
    a = ap.parse_args()
    def wait():
        try:
            r = os.path.join(os.path.dirname(os.path.abspath(a.gate)), 'RECORDER_STATE.txt')
            gate_wait(r if os.path.basename(a.gate) == 'BACKFILL_GATE.txt' and os.path.exists(r) else a.gate, poll_s=30, max_wait_s=a.gate_limit); return True
        except TimeoutError:
            return False
    rc, man = run(a.coins.split(','), a.first, a.last, a.out, wait=wait, every=a.every)
    print('HL FUNDING %s..%s: %d coin-months, %d written, rc %d' % (a.first, a.last, len(man), sum(1 for r in man if 'rows' in r[2]), rc))
    return rc


if __name__ == '__main__':
    sys.exit(main())
