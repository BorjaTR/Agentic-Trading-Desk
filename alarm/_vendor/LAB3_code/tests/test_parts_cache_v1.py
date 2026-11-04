"""test_parts_cache_v1.py (BUILD5, D2.1 for ALARM_V1_10, 31 Oct 2026; SCOUT 14:15:39Z: parts() listed each day about 6 times, 150,891
isfile, 30.1 s of a 66.8 s Outcomes run): Days.parts(day) keeps a day's listing while the day folder's mtime_ns is unchanged and at
least SETTLE_NS old (a younger mtime is re-listed every time: a second change in the same clock tick would not move it).
Tests first; planted, seconds; writes only in a temporary folder.
  python3 -B test_parts_cache_v1.py <lab3 code dir (holds lab3/)>"""
import os, sys, tempfile, time, unittest
CODE = os.path.realpath(sys.argv.pop(1) if len(sys.argv) > 1 else os.environ['LAB3_CODE']); sys.path.insert(0, CODE)
from lab3 import days as DY

OLD = 1_600_000_000 * 10**9                                          # a day-folder mtime far in the past (settled)


def mkpart(root, day, part, index=True):
    p = os.path.join(root, 'day=%s' % day, part); os.makedirs(p)
    if index:
        open(os.path.join(p, 'index.json'), 'w').close()


def age(root, day, ns=OLD):
    os.utime(os.path.join(root, 'day=%s' % day), ns=(ns, ns))


class Count:
    def __enter__(self):
        self.n = 0; self.real = os.listdir
        def ls(p='.'):
            self.n += 1; return self.real(p)
        DY.os.listdir = ls; return self

    def __exit__(self, *a):
        DY.os.listdir = self.real


def reader(root):
    r = object.__new__(DY.Days); r.root = root; r.purpose = 'research'; r._ix = {}; r._cp = {}
    if hasattr(DY.Days, '_PC'):
        r._pc = {}
    return r


class PartsCache(unittest.TestCase):
    def setUp(self):
        self.t = tempfile.TemporaryDirectory(); self.root = self.t.name

    def tearDown(self):
        self.t.cleanup()

    def test_same_answer_as_a_fresh_listing(self):
        mkpart(self.root, 20251001, 'A'); mkpart(self.root, 20251001, 'B.tmp_x'); mkpart(self.root, 20251001, 'C', index=False)
        mkpart(self.root, 20251001, 'D.aside_y'); age(self.root, 20251001)
        R = reader(self.root)
        self.assertEqual(R.parts('20251001'), ['A']); self.assertEqual(R.parts('20251001'), ['A'])
        self.assertEqual(R.parts('20251002'), [])

    def test_settled_day_listed_once(self):
        mkpart(self.root, 20251001, 'A'); age(self.root, 20251001); R = reader(self.root)
        with Count() as c:
            for _ in range(6):
                R.parts('20251001')
        self.assertEqual(c.n, 1)

    def test_young_day_relisted_every_time(self):
        mkpart(self.root, 20251001, 'A'); R = reader(self.root)              # mtime now: inside SETTLE_NS
        with Count() as c:
            R.parts('20251001'); R.parts('20251001')
        self.assertEqual(c.n, 2)

    def test_part_renamed_in_is_seen(self):                          # write.py / evt.py commit: rename .tmp_ -> part
        mkpart(self.root, 20251001, 'A'); age(self.root, 20251001); R = reader(self.root)
        self.assertEqual(R.parts('20251001'), ['A'])
        mkpart(self.root, 20251001, 'B.tmp_1')
        os.rename(os.path.join(self.root, 'day=20251001', 'B.tmp_1'), os.path.join(self.root, 'day=20251001', 'B'))
        self.assertEqual(R.parts('20251001'), ['A', 'B'])

    def test_same_mtime_after_a_change_is_never_trusted_when_young(self):
        """a change inside the same clock tick keeps the mtime: only a settled mtime is cached"""
        mkpart(self.root, 20251001, 'A'); now = time.time_ns(); age(self.root, 20251001, now); R = reader(self.root)
        self.assertEqual(R.parts('20251001'), ['A'])
        mkpart(self.root, 20251001, 'B'); age(self.root, 20251001, now)     # mtime forced back to the same value
        self.assertEqual(R.parts('20251001'), ['A', 'B'])

    def test_aside_rename_drops_the_part(self):
        mkpart(self.root, 20251001, 'A'); age(self.root, 20251001); R = reader(self.root)
        self.assertEqual(R.parts('20251001'), ['A'])
        os.rename(os.path.join(self.root, 'day=20251001', 'A'), os.path.join(self.root, 'day=20251001', 'A.aside_1'))
        self.assertEqual(R.parts('20251001'), [])

    def test_a_day_folder_that_appears_is_seen(self):
        R = reader(self.root); self.assertEqual(R.parts('20251003'), [])
        mkpart(self.root, 20251003, 'A'); self.assertEqual(R.parts('20251003'), ['A'])

    def test_both_writers_commit_by_rename_into_the_day_folder(self):
        """the cache's premise (CONDUCTOR 14:31:14Z item): a commit renames <PART>.tmp_ into the day folder"""
        w = open(os.path.join(CODE, 'lab3', 'write.py')).read(); e = open(os.path.join(CODE, 'lab3', 'evt.py')).read()
        self.assertIn('os.rename(tmp, final)', w)
        self.assertTrue('os.rename(tmp, final)' in e or 'os.rename(tmp, os.path.join(ddir, part))' in e, 'evt.py commits by rename')
        self.assertIn('RELIES ON', open(os.path.join(CODE, 'lab3', 'days.py')).read())


if __name__ == '__main__':
    unittest.main(verbosity=1)
