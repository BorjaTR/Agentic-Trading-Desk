"""[V3.2, 26 Oct 2026: a NEW name for the signed V3.1 file mutants_i2g_v3.py 8e51b53f4e5181e9 (kept unchanged; exit engine ED3 imports i2g_rules_v1). Changes: the two blockers of REVIEW_IDEA_TO_GRADE_V3_1_EXT_V1 (net FILL_SHARE without NO_COST parents; a resting entry whose decision price is older than MAX_STALE_S is NO_PRICE) and the V3.2 file names.]
mutants_i2g_v3_2.py (idea_to_grade V3.1, ALARMLIB seat, 25 Oct 2026): each mutant breaks ONE V3 rule in a copy of the code (a temporary
folder); test_i2g_v3_2.py must fail on every one of them (the tests are not vacuous). Reads no lab data.
  python3 -B mutants_i2g_v3_2.py      -> one line per mutant, KILLED or SURVIVED; exit 1 if any survived"""
import os, shutil, subprocess, sys, tempfile
HERE = os.path.dirname(os.path.realpath(__file__))
FO = os.path.realpath(os.path.join(HERE, '..', '..', '..', '..'))
FILES = ['test_i2g_v3_2.py', 'alarm_contract_v1.py', 'i2g_rules_v1_2.py', 'i2g_rules_v1.py', 'i2g_grade3_v3_2.py', 'i2g_engine_v3_2.py', 'idea_to_grade_v3_2.py', 'i2g_universe_v1.py', 'i2g_engine.py',
         'idea_to_grade.py', 'i2g_grade.py']
MUTANTS = [
    # the shared contract (alarm_contract_v1.py, F6)
    ('as-of window open at the moment', 'alarm_contract_v1.py', 'fires_sorted[i] <= t\n', 'fires_sorted[i] < t\n'),
    ('a later alarm drops the control', 'alarm_contract_v1.py', 'fires_sorted[i] <= t\n', 'fires_sorted[i] <= t + 1800\n'),
    ('no span rule', 'alarm_contract_v1.py', 't - prev <= gap_s and t - first <= max_span_s', 't - prev <= gap_s'),
    ('ambiguous bin scored as target', 'alarm_contract_v1.py', "        return 'AMBIGUOUS_STOP' if hit_t else 'STOP'", "        return 'TARGET' if hit_t else 'STOP'"),
    ('resting target fills on a touch', 'alarm_contract_v1.py', 'hit_t = hi > target if strict_target', 'hit_t = hi >= target if strict_target'),
    ('resting entry fills on a touch', 'alarm_contract_v1.py', 'return lo < limit if side > 0', 'return lo <= limit if side > 0'),
    # the grading rules
    ('vector as-of reads the future', 'i2g_rules_v1_2.py', 'hit[ok] = b[i[ok]] <= t[ok]', 'hit[ok] = b[i[ok]] <= t[ok] + 1800'),
    ('parent id without the side', 'i2g_rules_v1_2.py', "return '%s_%d_%+d' % (coin, int(t), int(side))", "return '%s_%d' % (coin, int(t))"),
    ('cluster weight 1', 'i2g_rules_v1_2.py', '1.0 / len(g), len(g)', '1.0, len(g)'),
    ('stop exit always at the level', 'i2g_rules_v1_2.py', 'x = min(sl, px[j]) if side > 0 else max(sl, px[j])', 'x = sl'),
    ('horizon read beyond the known path', 'i2g_rules_v1_2.py', 'if x <= known_end else -1', ''),
    ('time exit beyond the known path', 'i2g_rules_v1_2.py', '    if end > known_end:\n        return None, None, np.nan\n', ''),
    ('features read one bin of the future', 'i2g_rules_v1_2.py', "i = np.searchsorted(te, t, 'right') - 1", "i = np.searchsorted(te, t + 3, 'right') - 1"),
    ('tough ignores busy moments', 'i2g_rules_v1_2.py', 'q = np.asarray(eligible, bool) & ', 'q = '),
    ('tough move not signed by the side', 'i2g_rules_v1_2.py', 'm = side * np.asarray(grid_move, float)', 'm = np.asarray(grid_move, float)'),
    ('tough not seeded by the parent', 'i2g_rules_v1_2.py', "zlib.crc32(('tough|' + pid).encode())", "zlib.crc32(pid[::-1].encode()) + len(pid)"),
    ('taker leg without the gap', 'i2g_rules_v1_2.py', 'cost_bp / 200.0 + gap_pct / 2.0', 'cost_bp / 200.0'),
    ('interval with rows as the unit', 'i2g_rules_v1_2.py', 'keys.setdefault(c, []).append(i)', 'keys.setdefault(i, []).append(i)'),
    ('ledger accepts a closed ask', 'i2g_rules_v1_2.py', '    if closed:\n        raise', '    if False:\n        raise'),
    # F1 feed holes
    ('horizon reads a stale close', 'i2g_rules_v1_2.py', 'if j >= 0 and x - int(tl[j]) > max_stale_s * US:', 'if False:'),
    ('barrier walks across a hole', 'i2g_rules_v1_2.py', 'if int(tl[j]) - prev > stale:', 'if False:'),
    ('time exit after a hole', 'i2g_rules_v1_2.py', 'if end - int(tl[j]) > stale:', 'if False:'),
    # F2 universe
    ('universe rows not re-derived', 'i2g_rules_v1_2.py', 'if sorted(got) != sorted(want):', 'if False:'),
    ('universe header not checked', 'i2g_rules_v1_2.py', "if not head or head[0] != UNIVERSE_HEADER:", 'if not head:'),
    ('universe sha16 not rechecked', 'idea_to_grade_v3_2.py', '        if now != h:\n', '        if False:\n'),
    # F3 ledger
    ('ledger ignores the idea', 'i2g_rules_v1_2.py', "if idea is not None and row.get('idea') != idea:", 'if False:'),
    ('ledger ignores the days', 'i2g_rules_v1_2.py', "if first is not None and (row.get('days_from'), row.get('days_to')) != (first, last):", 'if False:'),
    ('ask not consumed', 'i2g_rules_v1_2.py', '    if ledger_used(path, ask_id):\n', '    if False:\n'),
    ('scratch ledger counts as graded', 'idea_to_grade_v3_2.py', "return 'GRADED' if canon and a.universe", "return 'GRADED' if a.universe"),
    # F4 move sign
    ('move signed by the traded side', 'i2g_engine_v3_2.py', 'values3[i, m15] = side * mv0', 'values3[i, m15] = eff[1] * mv0'),
    # F5 alarm id
    ('any alarm id accepted', 'i2g_rules_v1_2.py', '    if alarm_id not in registry:\n', '    if False:\n'),
    ('definition not checked', 'i2g_rules_v1_2.py', "if definition_sha16 is not None and row['definition_sha16'] != definition_sha16:", 'if False:'),
    ('event list not bound to the universe', 'i2g_rules_v1_2.py', '        elif events_subset:\n', '        elif True:\n'),
    ('event reader drops the side from the identity', 'idea_to_grade_v3_2.py', 'key = (c.upper(), tt, sd)', 'key = (c.upper(), tt)'),
    ('no-cost coin gets a zero cost', 'idea_to_grade_v3_2.py', "(costs[c][0] if c in costs else float('nan'))", "(costs[c][0] if c in costs else 0.0)"),
    ('no alarm id argument', 'idea_to_grade_v3_2.py', "p.add_argument('--alarm-id', required=True,", "p.add_argument('--alarm-id', required=False,"),
    # grade tables, engine, command
    ('slices rebuild weights', 'i2g_grade3_v3_2.py', 'r = RU.clustered_mean(vals[st], w[ix], cl[ix])', 'r = RU.clustered_mean(vals[st], np.ones(len(ix)), cl[ix])'),
    ('resting exit pays the taker leg on a target', 'i2g_grade3_v3_2.py', "exit_leg = np.where(code == RU.EXIT_CODES['TARGET'], rs, tk)", 'exit_leg = tk'),
    ('engine uses the fixed delay', 'i2g_engine_v3_2.py', "delay = float(v3['delay_s'])", 'delay = S.DELAY_S'),
    ('stale decision price kept (V3.2)', 'i2g_rules_v1_2.py', "if i0 < 0 or int(t_dec_us) - int(tl[i0]) > int(max_stale_s * US):", "if i0 < 0:"),
    ('stale limit off by one (V3.2)', 'i2g_rules_v1_2.py', "int(t_dec_us) - int(tl[i0]) > int(max_stale_s * US)", "int(t_dec_us) - int(tl[i0]) >= int(max_stale_s * US)"),
    ('no-cost parents in net fill share (V3.2)', 'i2g_grade3_v3_2.py', "F = fill[prow] if cname == 'GROSS' else np.where(np.isfinite(legs[cname][0][prow]), fill[prow], np.nan)", "F = fill[prow]"),
    ('no ledger argument', 'idea_to_grade_v3_2.py', "p.add_argument('--ledger-ask', required=True,", "p.add_argument('--ledger-ask', required=False,"),
]


def main():
    bad = 0
    for name, fn, old, new in MUTANTS:
        with tempfile.TemporaryDirectory() as d:
            for f in FILES:
                shutil.copy2(os.path.join(HERE, f), d)
            p = os.path.join(d, fn); s = open(p).read()
            if s.count(old) != 1:
                print('BROKEN %-45s pattern found %d times' % (name, s.count(old))); bad += 1; continue
            open(p, 'w').write(s.replace(old, new))
            r = subprocess.run([sys.executable, '-B', '-W', 'ignore', os.path.join(d, 'test_i2g_v3_2.py')], capture_output=True, text=True,
                               env=dict(os.environ, I2G_IMPL='v3', I2G_FORENSICS=FO, PYTHONDONTWRITEBYTECODE='1'), cwd=d)
            killed = r.returncode != 0
            bad += not killed
            print('%s %-45s %s' % ('KILLED  ' if killed else 'SURVIVED', name, (r.stderr.strip().split('\n') or [''])[-1][:80]))
    print('%d of %d mutants killed' % (len(MUTANTS) - bad, len(MUTANTS)))
    sys.exit(1 if bad else 0)


if __name__ == '__main__':
    main()
