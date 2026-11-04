"""test_release_v23.py (BUILD1 for LAB1, 23 Oct 2026): labcore.release V2_3, planted graphs only.
  V1 a table pinned by value columns: a prose-column edit passes; a value-column edit refuses; a header edit refuses; a missing column refuses
  V2 declared closure (OX-SKEPTIC FROZEN_1): a root refuses while a declared unpinned file is pinned nowhere; pinned in a child: passes
  V3 code files stay pinned whole (an edit of a .py refuses even if a table beside it is value-pinned)
Run with LABCORE_DIR=<folder holding the labcore package to test> (default: the forensics one)."""
import json, os, sys
import pytest
sys.path.insert(0, os.environ.get('LABCORE_DIR') or '<LAB_REPO>/forensics/team/RESEARCH/tools')
from labcore import release, ids  # noqa: E402

TAB = '# note\ncode\tunit\tmeaning\tnotes\nA\tbp\tthe meaning\told words\nB\tpct\tmore\tmore words\n'


def man(tmp, files, **kw):
    m = dict(release='T', files=files, runtime={}, **kw); p = tmp / ('R_%d.json' % len(list(tmp.iterdir()))); p.write_text(json.dumps(m))
    return str(p)


def vpin(tmp, name, cols=('code', 'unit', 'meaning')):
    p = str(tmp / name)
    return {'role': 't', 'schema_sha16': release.schema_sha16(p), 'value_columns': list(cols), 'value_sha16': release.value_sha16(p, list(cols))}


def test_V1_value_pinned_table(tmp_path):
    t = tmp_path / 'CAT.tsv'; t.write_text(TAB); p = man(tmp_path, {'CAT.tsv': vpin(tmp_path, 'CAT.tsv')})
    assert release.check(p, root=str(tmp_path))
    t.write_text(TAB.replace('old words', 'new, corrected words'))                    # prose only: passes
    assert release.check(p, root=str(tmp_path))
    t.write_text(TAB.replace('A\tbp', 'A\tbp per 8h'))                                   # a unit: refused
    with pytest.raises(release.ReleaseRefused, match='value columns'):
        release.check(p, root=str(tmp_path))
    t.write_text(TAB.replace('code\tunit\tmeaning\tnotes', 'code\tunit\tmeaning\tnotes\textra'))      # header: refused
    with pytest.raises(release.ReleaseRefused, match='schema'):
        release.check(p, root=str(tmp_path))
    t.write_text(TAB.replace('code\tunit', 'kode\tunit'))                                # a value column gone: refused
    with pytest.raises(release.ReleaseRefused):
        release.check(p, root=str(tmp_path))


def test_V2_declared_closure(tmp_path):
    (tmp_path / 'used.py').write_text('x = 1\n'); (tmp_path / 'm.py').write_text('y = 1\n')
    pm = {'role': 'm', 'sha16': ids.sha16_file(str(tmp_path / 'm.py'))}
    root = man(tmp_path, {'m.py': pm}, unpinned_other_tools={'used.py': 'another tool'})
    with pytest.raises(release.ReleaseRefused, match='unbound: used.py'):
        release.check(root, root=str(tmp_path))
    child = man(tmp_path, {'used.py': {'role': 'u', 'sha16': ids.sha16_file(str(tmp_path / 'used.py'))}})
    root2 = man(tmp_path, {'m.py': pm}, unpinned_other_tools={'used.py': 'another tool'}, releases={os.path.basename(child): ids.sha16_file(child)})
    assert release.check(root2, root=str(tmp_path))


def test_V3_code_stays_whole(tmp_path):
    (tmp_path / 'CAT.tsv').write_text(TAB); (tmp_path / 'm.py').write_text('y = 1\n')
    p = man(tmp_path, {'CAT.tsv': vpin(tmp_path, 'CAT.tsv'), 'm.py': {'role': 'm', 'sha16': ids.sha16_file(str(tmp_path / 'm.py'))}})
    (tmp_path / 'm.py').write_text('y = 1  # a comment\n')
    with pytest.raises(release.ReleaseRefused, match='m.py'):
        release.check(p, root=str(tmp_path))


def test_V4_semantic_columns_must_be_pinned(tmp_path):
    """OX-SKEPTIC A36-C02: a value pin that leaves out an operative semantic column of its header (meaning, read_it_as, ...) refuses;
    a meaning edit then refuses like a value edit"""
    t = tmp_path / 'CAT.tsv'; t.write_text(TAB)
    p = man(tmp_path, {'CAT.tsv': vpin(tmp_path, 'CAT.tsv', cols=('code', 'unit'))})
    with pytest.raises(release.ReleaseRefused, match='semantic'):
        release.check(p, root=str(tmp_path))
    p2 = man(tmp_path, {'CAT.tsv': vpin(tmp_path, 'CAT.tsv')})
    assert release.check(p2, root=str(tmp_path))
    t.write_text(TAB.replace('the meaning', 'the opposite meaning'))
    with pytest.raises(release.ReleaseRefused, match='value columns'):
        release.check(p2, root=str(tmp_path))
