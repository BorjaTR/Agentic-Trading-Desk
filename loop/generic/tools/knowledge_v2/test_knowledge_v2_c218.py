"""test_knowledge_v2_c218.py (SCOUT 2026-11-08, C218): review B2 (held-out word order), note 1 (init makes the store folder),
note 2 (EVIDENCE refuses text numbers and bad windows). Kept apart from test_build_knowledge_v2.py (33 tests, unchanged).
Temp only under KNOW_V2_TMP (default <SCRATCH_DISK>/tmp_SCOUT).  cd knowledge_v2 && python3 -B -m unittest -v test_knowledge_v2_c218"""
import io, os, sys, shutil, tempfile, unittest
sys.dont_write_bytecode = True
HERE = os.path.dirname(os.path.abspath(__file__)); sys.path.insert(0, HERE)
import build_knowledge_v2 as K
REL = os.path.dirname(os.path.dirname(os.path.dirname(HERE)))
ALARM = os.path.join(HERE, "packs", "alarm.json")
if not os.path.isfile(ALARM): ALARM = os.path.join(REL, "packs", "alarm", "alarm.json")
TMP = os.environ.get("KNOW_V2_TMP", "<SCRATCH_DISK>/tmp_SCOUT")
def ev(eid, run, mech, t="3.0", waves="400", window="20250910:20260131"):
    return dict(eid=eid, utc="2026-11-08T20:00:00Z", run=run, arm="L", mechanism=mech, alarm="PLANT", variant="R1 V1", test_kind="VARIANT",
                statement="planted", window=window, lead15="12", minus_fdonly15="3.0", lead1h="", t=t, waves=waves,
                months_up="", months_total="", job="", source_file="planted", notes="")
class C218(unittest.TestCase):
    def setUp(self):
        K.load_pack(ALARM); self.d = tempfile.mkdtemp(prefix="know_c218_", dir=TMP); K.init(self.d)
    def tearDown(self):
        shutil.rmtree(self.d, ignore_errors=True)
    def st(self, fid):
        f = {x["fid"]: x for x in K.read(self.d, "FINDINGS.tsv")[0]}[fid]; return f["status"], f["status_rule"]
    def clean(self):
        buf = io.StringIO(); errs, mism = K.check(self.d, out=buf); self.assertEqual((errs, mism), ([], []), buf.getvalue())
    def evs(self, *rows):
        for r in rows: K.apply_op(self.d, "TEST", "EVIDENCE", sets=r, reason="planted")
    def test_holdout_on_unknown_fid_refused(self):   # B2 step 1 (was exit 0 and logged)
        with self.assertRaises(SystemExit) as c: K.apply_op(self.d, "HUNTER", "HOLDOUT_SAME_SIGN", target="F0001", reason="early")
        self.assertIn("UNKNOWN_FID", str(c.exception))
        self.assertEqual([o for o in K.read(self.d, "OPS_LOG.tsv")[0] if o["op"] == "HOLDOUT_SAME_SIGN"], [])
    def test_review_sequence_stays_supported(self):   # B2: a held-out row logged before the finding exists never confirms it (was CONFIRMED/C1)
        K.append(self.d, "OPS_LOG.tsv", K.OP_COLS, {"utc": "u", "who": "HUNTER", "op": "HOLDOUT_SAME_SIGN", "target": "F0001", "old_new": "- -> same sign", "reason": "early"})
        self.evs(ev("E0001", "P1", "FORCED_OUT"), ev("E0002", "P2", "CROWDED_LATE"))
        K.apply_op(self.d, "CUR", "ADD", sets=dict(fid="F0001", type="STATE", statement="s", evidence_eids="E0001,E0002"))
        self.assertEqual(self.st("F0001"), ("SUPPORTED", "S1+C1WAIT")); self.clean()
    def test_evidence_change_after_holdout_needs_a_new_read(self):   # B2 step 2
        self.evs(ev("E0001", "P1", "FORCED_OUT"), ev("E0002", "P2", "CROWDED_LATE"), ev("E0003", "P3", "FORCED_OUT"))
        K.apply_op(self.d, "CUR", "ADD", sets=dict(fid="F0001", type="STATE", statement="s", evidence_eids="E0001,E0002"))
        K.apply_op(self.d, "ORCH", "HOLDOUT_SAME_SIGN", target="F0001", reason="Feb-Mar same sign")
        self.assertEqual(self.st("F0001"), ("CONFIRMED", "C1"))
        K.apply_op(self.d, "CUR", "UPDATE", target="F0001", sets=dict(evidence_eids="E0001,E0002,E0003"), reason="run P3")
        self.assertEqual(self.st("F0001"), ("SUPPORTED", "S1+C1WAIT")); self.clean()
        K.apply_op(self.d, "ORCH", "HOLDOUT_SAME_SIGN", target="F0001", reason="new read on the frozen rule")
        self.assertEqual(self.st("F0001"), ("CONFIRMED", "C1")); self.clean()
    def test_init_makes_missing_folder(self):   # note 1 (was FileNotFoundError)
        d = os.path.join(self.d, "new", "store"); self.assertEqual(K.main(["init", "--pack", ALARM, "--dir", d]), 0)
        self.assertTrue(os.path.isfile(os.path.join(d, "EVIDENCE.tsv")))
    def test_evidence_values_refused(self):   # note 2 (was exit 0; window 20251001:2026 counted inside the design window)
        for kw, code in ((dict(t="abc"), "NOT_A_NUMBER t"), (dict(waves="x"), "NOT_A_NUMBER waves"), (dict(t="nan"), "NOT_A_NUMBER t"),
                         (dict(window="20251001:2026"), "BAD_WINDOW"), (dict(window="20260131:20250910"), "BAD_WINDOW"),
                         (dict(window="20251301:20251302"), "BAD_WINDOW"), (dict(window=""), "BAD_WINDOW")):
            with self.assertRaises(SystemExit) as c: K.apply_op(self.d, "T", "EVIDENCE", sets=ev("E0009", "P9", "FORCED_OUT", **kw))
            self.assertIn(code, str(c.exception))
        self.assertEqual(K.read(self.d, "EVIDENCE.tsv")[0], [])
        self.assertEqual(K.apply_op(self.d, "T", "EVIDENCE", sets=ev("E0001", "P1", "FORCED_OUT", t="", waves="")), "E0001")
if __name__ == "__main__":
    unittest.main(verbosity=1)
