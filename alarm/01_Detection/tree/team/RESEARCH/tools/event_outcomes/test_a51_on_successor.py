"""The independent A51 regression tests run against the VERSION 3 successor (STRATEGY/LEAD builder, 25 Oct 2026).
The outside file team/OUTSIDE/A51/outcomes_review_v1/test_a51.py stays untouched (pinned below by sha16). This runner executes that exact
text with the substitutions listed in SUBS, each asserted to apply exactly once. Every assertion of A51 is kept byte for byte except the
one the owner's instruction overrides (S5). Why each substitution:
  S1 import: A51 imports the reviewed snapshot (or its own unapplied proposal); here it imports the successor in this folder.
  S2 settings: the successor requires the caller's authorized outcome window (A51-04: a run setting) and, for exit labels, the static cost
     table of the frozen exit boundary (A51-05/07); build_fake's synthetic settings name both (the window is the synthetic event's day).
  S3 price source: build_fake replaces the canonical PriceCache by a stub without a PRICE index; the successor also reads each day's
     listing state and index vintage (A51-07). The stub answers LISTED and a fixed vintage.
  S4 (none of the tests' calls or inputs change otherwise).
  S5 forward support: A51 expected the unapplied proposal's refusal of the whole submission (PermissionError). The owner's instruction of
     25 Oct 11:18Z overrides it: "Preserve boundary-event identities with explicit unavailable/embargo reasons rather than silently
     dropping them". The successor publishes the boundary event's row with EMBARGO_SUPPORT on every column and never constructs a price
     reader (A51's NoRead stub stays armed: any read still fails the test).
  python3 -m pytest -q -p no:cacheprovider test_a51_on_successor.py"""
import hashlib, os, pathlib, sys
HERE = pathlib.Path(__file__).resolve().parent
A51 = HERE.parents[2] / 'OUTSIDE' / 'A51' / 'outcomes_review_v1' / 'test_a51.py'
A51_SHA16 = '4f2211c60d43e618'
sys.path.insert(0, str(HERE))
_src = A51.read_text()
assert hashlib.sha256(A51.read_bytes()).hexdigest()[:16] == A51_SHA16, 'the A51 test file changed: rebind this runner explicitly'
SUBS = [
    ('S1', "sys.path.insert(0,str(Q/'snapshot/tools/event_outcomes'))\nif os.environ.get('A51_PROPOSAL'):\n spec=importlib.util.spec_from_file_location('event_outcomes',Q/'snapshot/tools/event_outcomes/event_outcomes_proposed.py'); EO=importlib.util.module_from_spec(spec); sys.modules['event_outcomes']=EO; spec.loader.exec_module(EO)\nelse:\n import event_outcomes as EO\n",
     "import event_outcomes as EO\n"),
    ('S2', "s=dict(name='SYN',entry={'delay_s':6,'gap_s':60},directions=['LONG'],labels=labels or [label('return')])\n",
     "s=dict(name='SYN',entry={'delay_s':6,'gap_s':60},directions=['LONG'],labels=labels or [label('return')],run_window={'first':'20251015','last':'20251015'},cost={'table':'team/RESEARCH/QUANT/receipts/COSTS_PER_COIN_V1.tsv','sha16':'ff157578098a2f47','gap_pct':0.144})\n"),
    ('S3', " monkeypatch.setattr(EO.XE,'bars',lambda root,coin,g0,g1,cache: (g0+np.arange(len(c))*3_000_000,c,h,l))\n",
     " monkeypatch.setattr(EO.XE,'bars',lambda root,coin,g0,g1,cache: (g0+np.arange(len(c))*3_000_000,c,h,l))\n monkeypatch.setattr(EO.PriceSource,'index_sha16',lambda self,day:'0123456789abcdef'); monkeypatch.setattr(EO.PriceSource,'state',lambda self,coin,day:'LISTED')\n"),
    ('S5', " p=tmp_path/'s.json'; p.write_text(json.dumps(s)); e=tmp_path/'e.tsv'; e.write_text('coin\\tt\\tside\\nBTC\\t1760572790\\t1\\n')\n class NoRead:\n  def __init__(self,*a,**k): raise AssertionError('price reader reached before forward embargo')\n monkeypatch.setattr(EO.prices,'PriceCache',NoRead)\n with pytest.raises(PermissionError): EO.build('synthetic',CODE,str(e),str(p),'SYN','20251015','20251015',str(tmp_path/'out'))\n",
     " p=tmp_path/'s.json'; p.write_text(json.dumps(s)); e=tmp_path/'e.tsv'; e.write_text('coin\\tt\\tside\\nBTC\\t1760572790\\t1\\n')\n class NoRead:\n  def __init__(self,*a,**k): raise AssertionError('price reader reached before forward embargo')\n monkeypatch.setattr(EO.prices,'PriceCache',NoRead)\n sys.path.insert(0,CODE); from lab3 import write as LW\n captured=[]; monkeypatch.setattr(LW,'write_part',lambda *a,**kw:captured.append((a,kw)))\n EO.build('synthetic',CODE,str(e),str(p),'SYN','20251015','20251015',str(tmp_path/'out'),log=lambda *a:None)\n codes=captured[0][0][3]\n assert set(codes)=={'OUT.SYN.entry__px','OUT.SYN.entry__s','OUT.SYN.X__LONG'}\n for code in codes.values():\n  rr=code['rows']['BTC']; assert rr['as_of_us']==[1760572790*1_000_000] and rr['empty_reason']==['EMBARGO_SUPPORT'] and rr['value_kind']==[0]\n"),
]
for name, old, new in SUBS:
    assert _src.count(old) == 1, '%s: the A51 text moved (%d matches): rebind this runner explicitly' % (name, _src.count(old))
    _src = _src.replace(old, new)
exec(compile(_src, str(A51) + ' [run on the VERSION 3 successor; substitutions S1-S3, S5]', 'exec'), globals())
