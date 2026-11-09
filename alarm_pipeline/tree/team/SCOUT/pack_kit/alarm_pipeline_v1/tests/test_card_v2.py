#!/usr/bin/env python3
"""test_card_v2.py (SCO-A154; c5 to c7 SCO-A170 V1_3_2: hypothesis at CLAIM from the meta, never the mechanism json): smallest tests of card_v2.py (card_v1 with the INDEX version column). Fake card inputs only; the real
alarm_cards_v1.side_hits is imported read-only by the tool. Scratch tests/scratch/cv2_<test>_<ns>/ (kept). env CARD_V2_UNDER_TEST."""
import sys
sys.dont_write_bytecode = True
import glob, json, os, subprocess, time
T = os.path.dirname(os.path.realpath(__file__)); HERE = os.path.dirname(T)
TOOL = os.environ.get('CARD_V2_UNDER_TEST', os.path.join(HERE, 'card_v2.py'))
H8 = 'alarm\tmechanism\tcard_sha16\tutc\trole\tcard\thandoff_sha16\tsource_jobs'


def world(name, index_text, tool='mechanism_v2.py', m_extra=None, meta_extra=None):
    W = os.path.join(T, 'scratch', 'cv2_%s_%d' % (name, time.time_ns())); os.makedirs(W)
    tsv = os.path.join(W, 'C.tsv'); md = os.path.join(W, 'C.md'); mj = os.path.join(W, 'M.json'); mt = os.path.join(W, 'META.json')
    open(tsv, 'w').write('alarm\tq\tanswer\tnumber\tsource\tsha16\tstrength\n' + ''.join('A\t%s\tan answer\t1\tX.tsv\t%s\tSOLID\n' % (q, '0' * 16) for q in ('Q1', 'Q2', 'GRADE')))
    open(md, 'w').write('# cards\n\n### A (fake)\n\n- after the fire (description): the price stays\n\n## Part B\n\n1. a line\n')
    M = dict(mechanism='FORCED_OUT', share=1.0, map_sha16='2f1131b39bd554a5', threshold=0.9, shares={'FORCED_OUT': {'share': 1.0}}, q3={}, q4={})
    if tool:
        M['tool'] = tool
    M.update(m_extra or {})
    json.dump(M, open(mj, 'w'))
    meta = dict(kit=dict(race='PASS'), jobs=dict(MECHANISM='1'), role='test'); meta.update(meta_extra or {})
    json.dump(meta, open(mt, 'w'))
    root = os.path.join(W, 'ROOT'); os.makedirs(root)
    if index_text is not None:
        open(os.path.join(root, 'INDEX.tsv'), 'w').write(index_text)
    r = subprocess.run([sys.executable, '-B', TOOL, '--alarm', 'A', '--cards-tsv', tsv, '--cards-md', md, '--mechanism-json', mj, '--meta', mt,
                        '--root', root, '--out', os.path.join(W, 'OUT')], stdout=subprocess.PIPE, stderr=subprocess.STDOUT, universal_newlines=True, timeout=30)
    return r, root


def claim_line(root):
    L = [l for p in glob.glob(os.path.join(root, '*', 'A', 'ALARM_CARD_A.md')) for l in open(p).read().splitlines() if 'hypothesis at CLAIM:' in l]
    assert len(L) == 1, L
    return L[0].split('hypothesis at CLAIM:')[1].strip()


def c1_version_column_v2():
    r, root = world('c1', H8 + '\tversion\nB\tNONE\tx\tu\tr\tc\th\t1\tmechanism_v1\n')
    L = open(os.path.join(root, 'INDEX.tsv')).read().splitlines()
    assert r.returncode == 0 and len(L) == 3 and L[2].split('\t')[8] == 'mechanism_v2' and len(L[2].split('\t')) == 9, (r.stdout, L)
    assert len(glob.glob(os.path.join(root, 'INDEX.tsv.pre_SCO_*'))) == 1


def c2_eight_columns_kept():
    r, root = world('c2', H8 + '\nB\tNONE\tx\tu\tr\tc\th\t1\n')
    L = open(os.path.join(root, 'INDEX.tsv')).read().splitlines()
    assert r.returncode == 0 and len(L[2].split('\t')) == 8, (r.stdout, L)


def c3_bad_header_writes_nothing():
    r, root = world('c3', 'x\ty\n')
    assert r.returncode == 2 and 'BAD_INDEX' in r.stdout, r.stdout
    assert sorted(os.listdir(root)) == ['.INDEX.lock', 'INDEX.tsv'] or sorted(os.listdir(root)) == ['INDEX.tsv'], os.listdir(root)


def c4_v1_json_version():
    r, root = world('c4', H8 + '\tversion\n', tool=None)
    L = open(os.path.join(root, 'INDEX.tsv')).read().splitlines()
    assert r.returncode == 0 and L[1].split('\t')[8] == 'mechanism_v1', (r.stdout, L)


def c5_claim_from_meta_not_null_result():
    # R1-11 planted: the card job's MECHANISM.json holds hypothesis null, the sealed INPUT (meta) FORCED_OUT
    r, root = world('c5', H8 + '\tversion\n', m_extra=dict(hypothesis=None), meta_extra=dict(hypothesis='FORCED_OUT'))
    assert r.returncode == 0 and claim_line(root) == 'FORCED_OUT', (r.stdout, claim_line(root))


def c6_claim_never_the_result():
    # the result names another mechanism: the card still prints the value at CLAIM
    r, root = world('c6', H8 + '\tversion\n', m_extra=dict(hypothesis='LEVERAGE_FLUSH'), meta_extra=dict(hypothesis='FORCED_OUT'))
    assert r.returncode == 0 and claim_line(root) == 'FORCED_OUT', (r.stdout, claim_line(root))


def c7_no_claim_value_is_dash():
    # no hypothesis in the meta: '-', never filled from the mechanism json
    r, root = world('c7', H8 + '\tversion\n', m_extra=dict(hypothesis='FORCED_OUT'), meta_extra=dict(hypothesis=None))
    assert r.returncode == 0 and claim_line(root) == '-', (r.stdout, claim_line(root))


ok = 0; TS = [(k, f) for k, f in sorted(globals().items()) if k[:1] == 'c' and k[1:2].isdigit()]
for k, f in TS:
    try:
        f(); ok += 1; print('PASS', k)
    except Exception as e:
        print('FAIL', k, type(e).__name__, str(e)[:300])
print('RESULT %d of %d (tool %s)' % (ok, len(TS), TOOL)); sys.exit(0 if ok == len(TS) else 1)
