#!/usr/bin/env python3
"""mutants of true_gate_v1's key rules: each is one text change; the test suite must fail on it. Prints killed, survived, not found."""
import os, shutil, subprocess, sys, tempfile
HERE = os.path.dirname(os.path.abspath(__file__)); CODE = os.path.join(HERE, '..', 'true_gate_v1.py'); TEST = os.path.join(HERE, 'test_true_gate_v1.py')
M = [
 ('stale values kept', "    if a < 0 or a > max_age:\n        return NAN\n", ""),
 ('age boundary', "if a < 0 or a > max_age:", "if a < 0 or a >= max_age:"),
 ('missing read as 0', "    if not math.isfinite(v) or int(d['e'][i, j]) != 0:\n        return NAN", "    if not math.isfinite(v):\n        return 0.0\n    if int(d['e'][i, j]) != 0:\n        return NAN"),
 ('a reason ignored', "if not math.isfinite(v) or int(d['e'][i, j]) != 0:", "if not math.isfinite(v):"),
 ('known-after-t kept', "    if need_known_by is not None and d['k'] is not None and int(d['k'][i, j]) > int(need_known_by) * 1_000_000:\n        return NAN\n", ""),
 ('known_at boundary', "int(d['k'][i, j]) > int(need_known_by)", "int(d['k'][i, j]) >= int(need_known_by)"),
 ('footprint row counted', "first = (math.ceil(lo / step) + 1) * step", "first = math.ceil(lo / step) * step"),
 ('row beyond the end counted', "last = math.floor(hi / step) * step", "last = (math.floor(hi / step) + 1) * step"),
 ('present reads one step ahead', "return t - lab['end_s'], t\n", "return t - lab['end_s'], t + 60\n"),
 ('sign same ignored', "val *= side if sg == 'same' else -side", "val *= -side"),
 ('sign opposite wrong', "val *= side if sg == 'same' else -side", "val *= side"),
 ('side 0 allowed under sign', "        if side not in (1, -1):\n            return NAN\n        val *=", "        val *="),
 ('falling is rising', "return float(val < -abs(thr))", "return float(val > abs(thr))"),
 ('falling counts zero', "return float(val < -abs(thr))", "return float(val <= -abs(thr))"),
 ('rising counts zero', "return float(val > abs(thr))", "return float(val >= abs(thr))"),
 ('>= strict', "return float(val >= thr)", "return float(val > thr)"),
 ('<= strict', "return float(val <= thr)", "return float(val < thr)"),
 ('NaN hit is false', "    if not (math.isfinite(val) and math.isfinite(thr)):\n        return NAN\n    tst", "    if not (math.isfinite(val) and math.isfinite(thr)):\n        return 0.0\n    tst"),
 ('threshold ignores known_at', "v = cell(src, lab['thr_code']['code'], coin, t, lab['max_age_s'], need_known_by=t)", "v = cell(src, lab['thr_code']['code'], coin, t, lab['max_age_s'])"),
 ('threshold read one step later', "v = cell(src, lab['thr_code']['code'], coin, t, lab['max_age_s'], need_known_by=t)", "v = cell(src, lab['thr_code']['code'], coin, t + 60, lab['max_age_s'])"),
 ('present known_at off', "kb = t if lab['when'] == 'present' else None", "kb = None"),
 ('hole in a sum ignored', "if not vals or not all(math.isfinite(x) for x in vals):", "vals = [x for x in vals if math.isfinite(x)]\n        if not vals:"),
 ('pct on zero base', "            if a == 0:\n                return NAN\n", "            if a == 0:\n                return 0.0\n"),
 ('same code allowed', "        if c in reads['codes']:\n            raise Refused('SAME_CODE', 'the label reads %s and so does the trigger' % c)\n", ""),
 ('same family allowed', "        if hit:\n            raise Refused('SAME_FAMILY'", "        if False:\n            raise Refused('SAME_FAMILY'"),
 ('price label allowed', "if e['px'] or 'PRICE' in e['fam']:", "if False:"),
 ('price flag only', "if e['px'] or 'PRICE' in e['fam']:", "if 'PRICE' in e['fam']:"),
 ('price family only', "if e['px'] or 'PRICE' in e['fam']:", "if e['px']:"),
 ('unknown label allowed', "        if e is None or e['status'] == 'UNKNOWN':\n            raise Refused('UNKNOWN_SOURCE', 'the label reads %s", "        if e is None:\n            continue\n        if False:\n            raise Refused('UNKNOWN_SOURCE', 'the label reads %s"),
 ('unknown trigger allowed', "        if e is None or e['status'] == 'UNKNOWN':\n            raise Refused('UNKNOWN_SOURCE', 'the trigger reads %s", "        if e is None:\n            continue\n        if False:\n            raise Refused('UNKNOWN_SOURCE', 'the trigger reads %s"),
 ('event list passes', "        if not ef:\n            raise Refused('UNKNOWN_SOURCE', 'the trigger reads the event list", "        if not ef:\n            continue\n        if False:\n            raise Refused('UNKNOWN_SOURCE', 'the trigger reads the event list"),
 ('unknown op passes', "                if x['op'] not in KNOWN_OPS:\n                    raise Refused('UNKNOWN_OP', 'op %r: its reads cannot be known' % x['op'])\n", ""),
 ('fire side not read', "for k in ('inputs', 'conditions', 'fire', 'base'):", "for k in ('inputs', 'conditions', 'base'):"),
 ('mirror not read', "for k, v in (dfn.get('mirror') or {}).items():", "for k, v in {}.items():"),
 ('threshold code not a read', "    if isinstance(lab.get('thr_code'), dict) and lab['thr_code'].get('code'):\n        out.add(lab['thr_code']['code'])\n", ""),
 ('side-picked codes not read', "    for c in (lab.get('code_by_side') or {}).values():\n        out.add(c)\n", ""),
 ('max_age optional', "    if isinstance(ma, bool) or not isinstance(ma, (int, float)) or not math.isfinite(ma) or ma <= 0:\n        raise Refused('BAD_LABEL', 'max_age_s is required and positive')\n", ""),
 ('verdict ignores the gap bar', "if gap >= MIN_EFFECT and lo > 0:", "if lo > 0:"),
 ('verdict gap strict', "if gap >= MIN_EFFECT and lo > 0:", "if gap > MIN_EFFECT and lo > 0:"),
 ('verdict ignores the interval', "if gap >= MIN_EFFECT and lo > 0:", "if gap >= MIN_EFFECT:"),
 ('verdict interval touches 0', "if gap >= MIN_EFFECT and lo > 0:", "if gap >= MIN_EFFECT and lo >= 0:"),
 ('not supported on the gap', "if hi < MIN_EFFECT:", "if gap < MIN_EFFECT:"),
 ('not supported at the bar', "if hi < MIN_EFFECT:", "if hi <= MIN_EFFECT:"),
 ('fires weighted, not waves', "wm = np.bincount(inv, weights=X['e'][sel]) / nw", "wm = X['e'][sel]"),
 ('busy filter ignored', "FL.BUSY_MIN_C = busy_min_c\n", "FL.BUSY_MIN_C = 0.0\n"),
 ('whole window read', "            if lo <= t < hi:\n                rows[k]", "            if True:\n                rows[k]"),
 ('nothing after last opened', "        if day > self.last:\n            return None\n", ""),
 ('perfire sha not checked', "    if sha16(cl['perfire']) != cl['perfire_sha16']:\n        raise Refused('PERFIRE_CHANGED', cl['perfire'])\n", ""),
]
src = open(CODE).read()
tmp = tempfile.mkdtemp(); shutil.copyfile(os.path.join(HERE, '..', 'SOURCE_FAMILIES_V1.tsv'), os.path.join(tmp, 'SOURCE_FAMILIES_V1.tsv'))
ALARM = os.path.realpath(os.path.join(HERE, '..', '..', '..', '..', '..'))
b = os.path.join(tmp, 'base'); os.makedirs(b); open(os.path.join(b, 'true_gate_v1.py'), 'w').write(src)
shutil.copyfile(os.path.join(tmp, 'SOURCE_FAMILIES_V1.tsv'), os.path.join(b, 'SOURCE_FAMILIES_V1.tsv'))
if subprocess.run([sys.executable, '-B', TEST], env=dict(os.environ, TG_CODE=b, TG_REL=ALARM, PYTHONDONTWRITEBYTECODE='1'), capture_output=True).returncode:
    print('BASELINE FAILS: the unchanged copy does not pass, no mutant can be judged'); sys.exit(1)
kill, sv, nf = [], [], []
for name, old, new in M:
    if src.count(old) < 1:
        nf.append(name); continue
    d = os.path.join(tmp, 'm%d' % len(kill + sv)); os.makedirs(d)
    open(os.path.join(d, 'true_gate_v1.py'), 'w').write(src.replace(old, new, 1))
    shutil.copyfile(os.path.join(tmp, 'SOURCE_FAMILIES_V1.tsv'), os.path.join(d, 'SOURCE_FAMILIES_V1.tsv'))
    env = dict(os.environ, TG_CODE=d, TG_REL=ALARM, PYTHONDONTWRITEBYTECODE='1')
    r = subprocess.run([sys.executable, '-B', TEST], env=env, capture_output=True, text=True)
    (kill if r.returncode else sv).append(name)
print('MUTANTS killed %d survived %d not found %d' % (len(kill), len(sv), len(nf)))
for n in sv:
    print('SURVIVED', n)
for n in nf:
    print('NOT FOUND', n)
sys.exit(1 if (sv or nf) else 0)
