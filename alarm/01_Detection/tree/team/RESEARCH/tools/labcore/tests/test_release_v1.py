"""test_release_v1 (BUILD2, 23 Oct 2026; OX-SKEPTIC A04-02, STRATEGY-143459): the release manifest is what runs. labcore.release.check
resolves every pinned file (module, table, policy, re-exported reader) by sha16, the table schemas by their header sha16 and the python and
numpy versions, at run start; any difference or a missing file refuses. Planted manifests in a temp folder; the last test checks the real
RELEASE_labcore_V2.json against the tree (so any change to a pinned file after the freeze fails here: that is a V3).
Mutants killed: skip the sha check; skip the version check; accept a missing file."""
import json, os, sys
import numpy as np
import pytest

TESTS = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.dirname(os.path.dirname(TESTS)))
from labcore import release, ids  # noqa: E402


def plant(tmp, **runtime):
    t = tmp / 'TABLE.tsv'; t.write_text('# note\ncode\tvalue\nA\t1\n'); m = tmp / 'mod.py'; m.write_text('x = 1\n')
    man = {'release': 'TEST', 'files': {'TABLE.tsv': {'sha16': ids.sha16_file(str(t)), 'schema_sha16': release.schema_sha16(str(t)), 'role': 't'},
                                        'mod.py': {'sha16': ids.sha16_file(str(m)), 'role': 'm'}},
           'runtime': dict(release.runtime(), **runtime)}
    p = tmp / 'R.json'; p.write_text(json.dumps(man)); return str(p), t, m


def test_R1_matching_tree_passes(tmp_path):
    p, _, _ = plant(tmp_path)
    assert release.check(p, root=str(tmp_path))['release'] == 'TEST'


def test_R2_changed_or_missing_file_refused(tmp_path):
    p, t, m = plant(tmp_path)
    m.write_text('x = 2\n')
    with pytest.raises(release.ReleaseRefused):
        release.check(p, root=str(tmp_path))
    m.write_text('x = 1\n'); os.rename(str(t), str(tmp_path / 'gone.tsv'))
    with pytest.raises(release.ReleaseRefused):
        release.check(p, root=str(tmp_path))


def test_R3_schema_change_named(tmp_path):
    p, t, _ = plant(tmp_path)
    t.write_text('# note\ncode\tvalue\textra\nA\t1\t2\n')
    with pytest.raises(release.ReleaseRefused, match='schema'):
        release.check(p, root=str(tmp_path))


def test_R4_runtime_versions_refused(tmp_path):
    p, _, _ = plant(tmp_path, numpy='0.0.0')
    with pytest.raises(release.ReleaseRefused, match='numpy'):
        release.check(p, root=str(tmp_path))


def test_R6_named_releases_checked_recursively(tmp_path):
    """STRATEGY-144233: a release names another tool's release by path + sha16; its file and its own check must both hold"""
    p, _, m = plant(tmp_path); sub = tmp_path / 'sub'; sub.mkdir(); q, _, m2 = plant(sub)
    sm = json.load(open(q)); sm['files'] = {'sub/' + k: v for k, v in sm['files'].items()}; open(q, 'w').write(json.dumps(sm))   # paths from root
    man = json.load(open(p)); man['releases'] = {'sub/R.json': ids.sha16_file(q)}; open(p, 'w').write(json.dumps(man))
    assert release.check(p, root=str(tmp_path))
    m2.write_text('x = 3\n')                                           # the named tool changed under its release
    with pytest.raises(release.ReleaseRefused, match='sub/R.json'):
        release.check(p, root=str(tmp_path))
    m2.write_text('x = 1\n'); man['releases'] = {'sub/R.json': '0' * 16}; open(p, 'w').write(json.dumps(man))
    with pytest.raises(release.ReleaseRefused, match='names'):
        release.check(p, root=str(tmp_path))


def test_R5_the_real_release_resolves():
    p = os.path.join(os.path.dirname(TESTS), 'RELEASE_labcore_V2_7.json')
    if not os.path.exists(p):
        pytest.skip('RELEASE_labcore_V2_7.json not written yet')
    man = release.check(p)
    assert man['release'] == 'V2_7' and all(k.startswith('team/') for k in man['files'])
    assert 'interpreter' not in man.get('runtime', {})          # the desk build (desk/build/fix_pins_v2.py E1) drops the lab's path pin


def test_R6_interpreter_path_pinned(tmp_path):
    """another interpreter path than the pinned one refuses (LAB1 17:21:57Z MUST 1)"""
    (tmp_path / 'm.py').write_text('x = 1\n')
    p = tmp_path / 'R.json'
    man = {'release': 'T', 'files': {'m.py': {'sha16': ids.sha16_file(str(tmp_path / 'm.py')), 'role': 'x'}}, 'runtime': release.runtime()}
    p.write_text(json.dumps(man)); assert release.check(str(p), root=str(tmp_path))
    man['runtime']['interpreter'] = '/usr/bin/python3-other'; p.write_text(json.dumps(man))
    with pytest.raises(release.ReleaseRefused, match='interpreter'):
        release.check(str(p), root=str(tmp_path))
