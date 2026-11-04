#!/usr/bin/env python3
"""d1_mem_v2.py (SCOUT, 31 Oct 2026; TEST, NOT REVIEWED; d1_mem_v1.py d7e4abf140fa1333 with only its type-check findings fixed:
the dynamic import of lab3 marked for pyright, no attribute set on the replacement read; speed stage 2, D1: team/SCOUT/D1_BUILD_PLAN_V1.md 9b9edfc8a0e2de3f): the rows an
Outcomes run writes, kept in memory as they are written, and event_outcomes.read's answer made from them, exact by construction.
  Capture(write)   a write function for event_outcomes(_rel1).run(0, ..., inprocess_write=Capture(lab3.write.write_part)): each day's
                   rows are kept (a copy of the lists the run hands its writer), then the real writer writes them as before.
  mem_read(EO, cap, out_root, code_dir, subject, cols=None, first=None, last=None)
                   event_outcomes.read with the same refusals (SUBJECT, COLUMN; the research seal and NotBuilt through lab3.days'
                   own Days(out_root, 'research').index) and the same decode, sort and arrays, with each day's rows taken from the
                   capture in place of the day's block files; the capture must hold the store's days and coins (else MEM_MISMATCH).
  install(EO, mem) EO.read answers mem_read for the roots in mem ({realpath(out_root): (cap, subject)}) and the real read otherwise.
Reads only the run's catalog, its day folders and index files; writes nothing."""
import os, sys
import numpy as np


class Capture:
    def __init__(self, write):
        self.write = write; self.days = {}; self.part = None

    def __call__(self, root, day, part, codes, coins, **kw):
        if self.part not in (None, part):
            raise ValueError('MEM_MISMATCH: one capture holds one part, got %s and %s' % (self.part, part))
        if int(day) in self.days:
            raise ValueError('MEM_MISMATCH: day %s written twice' % day)
        kept = {code: {'kind': c['kind'], 'rows': {coin: {k: list(v) for k, v in rr.items()} for coin, rr in c['rows'].items()}}
                for code, c in codes.items()}
        self.part = part; self.days[int(day)] = (kept, list(coins))
        return self.write(root, day, part, codes, coins, **kw)


def mem_read(EO, cap, out_root, code_dir, subject, cols=None, first=None, last=None):
    part = 'OUT.%s' % subject
    if cap.part != part:
        raise EO.Refused('SUBJECT', 'run is %s, not %s' % ((cap.part or 'OUT.?')[4:], subject))
    if code_dir not in sys.path:
        sys.path.insert(0, code_dir)
    from lab3 import days as LD  # pyright: ignore[reportMissingImports]  (lab3 is found at run time, code_dir on sys.path)
    cat = {}
    for l in open(os.path.join(out_root, 'OUT_CATALOG_%s.tsv' % subject)):
        if l.startswith('OUT.'):
            f = l.rstrip('\n').split('\t'); cat[f[0].split('.', 2)[2]] = f
    cols = cols or list(cat)
    R = LD.Days(out_root, 'research'); out = {}
    days = [d for d in R.days() if (first is None or d >= first) and (last is None or d <= last) and part in R.parts(d)]
    coins_of = {}
    for d in days:
        coins = list(R.index(d, part)['coins'])                    # the research seal and NotBuilt, as the real read meets them
        if int(d) not in cap.days or cap.days[int(d)][1] != coins:
            raise ValueError('MEM_MISMATCH: day %s of %s: the store and the capture differ (days or coins)' % (d, out_root))
        coins_of[d] = coins
    for c in cols:
        if c not in cat:
            raise EO.Refused('COLUMN', '%s not in the catalog' % c)
        word = cat[c][6] == 'word'; acc = {k: [] for k in ('coin', 'as_of_us', 'known_at_us', 'value', 'reason')}
        code = '%s.%s' % (part, c)
        for d in days:
            kept = cap.days[int(d)][0]
            if code not in kept:
                raise ValueError('MEM_MISMATCH: %s day %s not in the capture' % (code, d))
            rr = kept[code]['rows']
            for coin in coins_of[d]:
                x = rr.get(coin)
                if x is None:
                    continue
                for vk, b, tx, er, ka, a in zip(x['value_kind'], x['value_bits'], x['value_txt'], x['empty_reason'], x['known_at_us'], x['as_of_us']):
                    acc['coin'].append(coin); acc['as_of_us'].append(int(a)); acc['known_at_us'].append(int(ka)); acc['reason'].append(er or '')
                    acc['value'].append((tx if vk == 3 else '') if word else (float(np.array([b], '<u8').view('<f8')[0]) if vk == 1 else np.nan))
        o = np.lexsort((np.array(acc['coin'], str), np.array(acc['as_of_us'], np.int64))) if acc['coin'] else np.zeros(0, int)
        out[c] = dict(coin=np.array(acc['coin'], object)[o], as_of_us=np.array(acc['as_of_us'], np.int64)[o],
                      known_at_us=np.array(acc['known_at_us'], np.int64)[o], reason=np.array(acc['reason'], object)[o],
                      value=(np.array(acc['value'], object) if word else np.array(acc['value'], float))[o], unit=cat[c][6],
                      kind='word' if word else 'number')
    return out


def install(EO, mem):
    real = EO.read

    def read(out_root, code_dir, subject, cols=None, first=None, last=None):
        k = os.path.realpath(out_root)
        if k in mem:
            cap, subj = mem[k]
            return mem_read(EO, cap, out_root, code_dir, subject, cols, first, last)
        return real(out_root, code_dir, subject, cols, first, last)
    EO.read = read
    return real
