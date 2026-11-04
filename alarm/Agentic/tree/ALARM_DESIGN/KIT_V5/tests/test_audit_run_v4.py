#!/usr/bin/env python3
"""audit_run_v4's normal entry on a planted run: a missing row, a substituted variant or detector, damage, another variant's PERFIRE in a two-variant seal, a seal gone, a label not the sealed one, an intact UNSURE row; only the intact case finishes. Answers by hand, GPT's witnesses included."""
import contextlib, hashlib, importlib.util, io, os, shutil, sys, tempfile
HERE = os.path.dirname(os.path.abspath(__file__))
sp = importlib.util.spec_from_file_location('a4', os.path.join(HERE, '..', 'tools', 'audit_run_v4.py')); A = importlib.util.module_from_spec(sp); sp.loader.exec_module(A)
V3 = A.V3; RUN = 'TSTA_20261103'; h = tempfile.mkdtemp(); r = os.path.join(h, 'runs', RUN); reg = os.path.join(r, 'registers'); os.makedirs(reg)
for n, cols in V3.HDR.items():
    open(os.path.join(reg, n + '.tsv'), 'w').write('\t'.join(cols) + '\n')
V3.configure = lambda s: V3.CFG.update(H=h, HB=h, RUNNER=None, SETTINGS=s)
def row(n, **k):
    open(os.path.join(reg, n + '.tsv'), 'a').write('\t'.join(str(k.get(c, '-')) for c in V3.HDR[n]) + '\n')
os.makedirs(os.path.join(r, 'ideas')); open(os.path.join(r, 'ideas/CARD.md'), 'w').write('true_label=LLLL true_mirror=MMMM\n')
row('VARIANTS', utc='2026-11-03T00:01:00Z', idea='I1', V='V1', def_sha16='DDDD', lean='FADE', prereg_rel='ideas/CARD.md')
J = '20269999_GRADE_I1'
row('RUNS', job=J, kind='GRADE', idea='I1', variants='V1,V2')
row('DECISIONS', utc='2026-11-03T00:05:00Z', idea='I1', V='V1', state='STOP', grade_job=J)
G = os.path.join(r, 'receipts', J); os.makedirs(G); open(os.path.join(G, 'STAGES.tsv'), 'w').write('stage\trc\nperfire_seal_V1\t0\n')
SEAL = 'V1\tAAAAPERFIRE\t3\t9\t1\t2\t12\t%s\nV2\tBBBBPERFIRE\t3\t9\t1\t2\t12\t%s\n' % (J, J)
def seal(t):
    open(os.path.join(G, 'PERFIRE_SEAL.tsv'), 'w').write(t)
    open(os.path.join(G, 'SHA16.txt'), 'w').write('%s PERFIRE_SEAL.tsv\n' % hashlib.sha256(t.encode()).hexdigest()[:16])
seal(SEAL)
def code():
    with contextlib.redirect_stdout(io.StringIO()) as o:
        c = A.main(['--settings', 'x', RUN])
    return c, o.getvalue()
def plant(d, idea='I1', V='V1', dfn='DDDD', word='UNSURE', perfire='AAAAPERFIRE', lab='LLLL', mir='MMMM'):
    p = os.path.join(r, 'receipts', 'J1', d); os.makedirs(p); open(os.path.join(p, 'TRUE_CARD.txt'), 'w').write('card\n')
    c = hashlib.sha256(b'card\n').hexdigest()[:16]
    t = 'id\tverdict\tidea\tV\tdef_sha16\tperfire_sha16\tlabel_sha16\tmirror_sha16\tcard_sha16\nX\t%s\t%s\t%s\t%s\t%s\t%s\t%s\t%s\n' % (word, idea, V, dfn, perfire, lab, mir, c)
    open(os.path.join(p, 'TRUE_ROW.tsv'), 'w').write(t); open(os.path.join(p, 'TRUE_ROW.sha16'), 'w').write(hashlib.sha256(t.encode()).hexdigest()[:16] + '\n'); return p
def case(want, text, **k):
    p = plant('TRUE_V1_C', **k); c, o = code(); assert c == want and text in o, (k, c, o[-500:]); shutil.move(p, tempfile.mkdtemp())
c, o = code(); assert c == 3 and 'no TRUE row' in o and 'FINISHED NO' in o, o[-400:]
case(3, 'belongs to I2', idea='I2')
case(3, 'definition OTHER', dfn='OTHER')
case(3, "not V1's sealed one", perfire='BBBBPERFIRE')          # GPT's witness: V2's digest, byte-intact
case(3, 'not V1', perfire='ELSE')
case(3, 'word', word='MAYBE')
case(3, 'not the ones sealed', lab='OTHER')
case(3, 'not the ones sealed', mir='OTHER')
p = plant('TRUE_V1_D'); open(os.path.join(p, 'TRUE_ROW.tsv'), 'a').write('\n'); c, o = code(); assert c == 3 and 'row damaged' in o, o[-400:]; shutil.move(p, tempfile.mkdtemp())
p = plant('TRUE_V1_E'); open(os.path.join(p, 'TRUE_CARD.txt'), 'a').write('x'); c, o = code(); assert c == 3 and 'card damaged' in o, o[-400:]; shutil.move(p, tempfile.mkdtemp())
p = plant('TRUE_V1_F'); c, o = code(); assert c == 0 and 'FINISHED:' in o and 'A18  TRUE        PASS' in o, o[-400:]   # the intact UNSURE row
os.rename(os.path.join(G, 'PERFIRE_SEAL.tsv'), os.path.join(G, 'SEAL_AWAY')); c, o = code(); assert c == 3 and 'it is gone' in o, o[-400:]   # GPT's witness: the seal deleted
os.rename(os.path.join(G, 'SHA16.txt'), os.path.join(G, 'SHA_AWAY')); open(os.path.join(G, 'STAGES.tsv'), 'w').write('stage\trc\n'); c, o = code(); assert c == 0 and 'UNVERIFIED' in o, o[-400:]              # a job from before the seal: said, not passed quietly
os.rename(os.path.join(G, 'SEAL_AWAY'), os.path.join(G, 'PERFIRE_SEAL.tsv'))
os.rename(os.path.join(G, 'SHA_AWAY'), os.path.join(G, 'SHA16.txt'))
seal(SEAL + SEAL); c, o = code(); assert c == 3 and 'seal rows' in o, 'two rows of one variant'
seal(SEAL.replace('\t%s\n' % J, '\tOTHER_JOB\n')); c, o = code(); assert c == 3 and 'seal rows' in o, 'another job in the seal'
seal(SEAL.replace('\t12\t', '\t')); c, o = code(); assert c == 3 and 'seal rows' in o, 'not eight columns'
seal(SEAL); c, o = code(); assert c == 0, 'the intact seal again'
SEAL2 = SEAL.replace('AAAAPERFIRE', 'BBBBPERFIRE'); p2 = plant('TRUE_V1_G', perfire='BBBBPERFIRE')
open(os.path.join(G, 'PERFIRE_SEAL.tsv'), 'w').write(SEAL2); shutil.move(p, tempfile.mkdtemp()); c, o = code(); assert c == 3 and 'not the one its job recorded' in o, ('GPT witness: a changed seal agreeing with the row', o[-300:])   # GPT's witness
shutil.move(p2, tempfile.mkdtemp()); p = plant('TRUE_V1_H'); seal(SEAL)
shutil.move(p, os.path.join(h, 'row_away'))
open(os.path.join(reg, 'DECISIONS.tsv'), 'w').write('\t'.join(V3.HDR['DECISIONS']) + '\n'); row('DECISIONS', utc='2026-11-02T22:42:00Z', idea='I1', V='V1', state='STOP'); c, o = code(); assert c == 0, 'a decision before the boundary is not asked'
open(os.path.join(reg, 'DECISIONS.tsv'), 'w').write('\t'.join(V3.HDR['DECISIONS']) + '\n'); row('DECISIONS', utc='2026-11-02T23:00:00Z', idea='I1', V='V1', state='STOP', grade_job=J); c, o = code(); assert c == 3, 'a decision at the boundary is asked'
print('PASS audit_run_v4 (20 cases)')
