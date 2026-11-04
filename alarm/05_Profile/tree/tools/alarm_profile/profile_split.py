"""tools/alarm_profile PROFILE SPLIT (QUANT 22 Oct 2026; the owner 15:39 Berlin: "how are you going to design the alarm?"). Counts the alarms that
meet named rules over the profile's values (EPI, this tool) and the context values (CTX, tools/alarm_context), so candidate alarms and cause
flags can be counted from inputs known at the alarm BEFORE any outcome is read. Writes nothing. Kept apart from alarm_profile.py so the builder's
code (and so the built part's sources) does not change.
RULES TSV: name, rule, meaning ('#' lines are notes). A rule is an expression over value names with comparisons, & (and), | (or), ~ (not)
and parentheses; an alarm where any input of the rule is unknown counts as UNKNOWN for that rule (never as met or not met).
  python3 -B profile_split.py <out root> <lab3 code dir> <subject> <first> <last> <rules tsv>"""
import ast, os, sys
import numpy as np
HERE = os.path.dirname(os.path.realpath(__file__)); sys.path.insert(0, HERE)
import alarm_profile as AP


def rule_names(expr):
    """the value names a rule expression reads"""
    return sorted({nd.id for nd in ast.walk(ast.parse(expr, mode='eval')) if isinstance(nd, ast.Name)})


def split(out_root, code_dir, subject, first, last, rules_path, epi=None, ctx=None, log=print):
    """per rule: met, not met, unknown, and the met share per month; then the FIRST rule against every other (both, first only, other
    only, neither, on alarms known for both). -> {name: (met, unknown)} boolean arrays"""
    rules = AP._tsv(rules_path)
    names = sorted({v for r in rules for v in rule_names(r['rule'])})
    epi_cols = {c[2] for c in AP.columns()}
    if epi is None:
        epi = AP.read(out_root, code_dir, subject, first, last)
    want = [v for v in names if v not in epi_cols]
    if ctx is None and want and AP.SUBJECTS[subject][1]:
        sys.path.insert(0, AP.CTX_DIR)
        import alarm_context as AC
        ctx = AC.read(out_root, code_dir, AP.SUBJECTS[subject][1], first, last, values=want)
    cj = AP._join(epi, ctx); env = {}
    for v in names:
        a = epi.get(v) if v in epi_cols else cj.get(v)
        if a is None:
            raise ValueError('rule input %s is neither an EPI nor a CTX value read' % v)
        env[v] = np.asarray(a, float)
    n = len(epi['coin']); months = np.array([AP.utc_day(t)[:6] for t in epi['t_alarm']]); mos = sorted(set(months.tolist()))
    log('SPLIT %s  subject %s  %s..%s  alarms %d  (no outcome read)' % (os.path.basename(rules_path), subject, first, last, n))
    res = {}
    for r in rules:
        unk = np.zeros(n, bool)
        for v in rule_names(r['rule']):
            unk |= ~np.isfinite(env[v])
        with np.errstate(invalid='ignore'):
            met = np.asarray(eval(r['rule'], {'__builtins__': {}}, dict(env)), bool) & ~unk
        res[r['name']] = (met, unk); k = ~unk
        by = '  '.join('%s %d/%d' % (m[2:], int((met & (months == m)).sum()), int((k & (months == m)).sum())) for m in mos)
        log('RULE %-16s met %5d (%5.1f pct of known)  not met %5d  unknown %5d  | %s | %s' % (
            r['name'], int(met.sum()), 100.0 * met.sum() / max(1, k.sum()), int((k & ~met).sum()), int(unk.sum()), by, r['meaning']))
    if rules:
        p = rules[0]['name']; pm, pu = res[p]
        for r in rules[1:]:
            m, u = res[r['name']]; k = ~pu & ~u
            log('CROSS %s x %-16s both %5d  %s only %5d  %s only %5d  neither %5d  (known both %d)' % (
                p, r['name'], int((k & pm & m).sum()), p, int((k & pm & ~m).sum()), r['name'], int((k & ~pm & m).sum()),
                int((k & ~pm & ~m).sum()), int(k.sum())))
    return res


if __name__ == '__main__':
    split(*sys.argv[1:7])
