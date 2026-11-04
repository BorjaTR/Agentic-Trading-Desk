"""test_proof_plan_v1.py (BUILD1, 23 Oct 2026; OX-SKEPTIC FROZEN_1 proof plan, A09-S04a): a PASS proof row certifies an EPI value only
when its scope names the proof plan (PROOFS table) the output was built with. Run with PROFILE_DIR=<alarm_profile folder to test>."""
import hashlib, os, sys
sys.path.insert(0, os.environ.get('PROFILE_DIR') or '<LAB_REPO>/forensics/team/RESEARCH/tools/alarm_profile')
import alarm_profile as AP  # noqa: E402

SCOPE = dict(output_release_sha16='0000000000000001', definition_sha16='0000000000000002', input_vintage_sha16='0000000000000003', subject='A02N')


def plant(tmp, plan_sha=None):
    c = AP.columns()[0][2]
    pr = tmp / 'PROOFS.tsv'; pr.write_text('value\tproof\n%s\tP1\n' % c)
    ps = hashlib.sha256(pr.read_bytes()).hexdigest()[:16]
    sc = dict(SCOPE, proof_plan_sha16=plan_sha or ps)
    rs = tmp / 'RESULTS.tsv'; rs.write_text('value\tproof\tresult\t' + '\t'.join(sorted(sc)) + '\n' + '%s\tP1\tPASS\t' % c + '\t'.join(sc[k] for k in sorted(sc)) + '\n')
    return c, str(pr), str(rs), {c: dict(SCOPE, proof_plan_sha16=ps)}


def test_same_plan_certifies(tmp_path):
    c, pr, rs, want = plant(tmp_path)
    assert AP.proof_status(proofs=pr, results=rs, expected_scope=want)[('EPI', c)][0] == 'PROVEN'


def test_other_plan_does_not_certify(tmp_path):
    c, pr, rs, want = plant(tmp_path, plan_sha='00000000000000ff')
    assert AP.proof_status(proofs=pr, results=rs, expected_scope=want)[('EPI', c)][0] == 'OPEN'
