"""labcore.briefs (BUILD2, 23 Oct 2026): the metric brief as a call (spec LEAD/LABCORE_STEP2_SPEC_V1.md b75998c5 sec 6). It CALLS the
reading-metrics skill's metric_brief.py (its tables, its readers, its flag words), never reads the trap table its own way.
  v2 (SKEPTIC 02-07, 02-08): a code with no LAB4 status row, or a status the skill does not flag and that is not PROVEN, is UNPROVEN
  (refused in a decision line, like CAUTION); decision_codes is read once (a generator works).
  v3 (metric_brief 77d2f63e, STRATEGY 14:19:56Z): the skill now flags every status that is not PROVEN (blank or unknown = CAUTION,
  WITHDRAWN = STOP); a code with NO LAB4 row stays UNPROVEN here (no status to read at all); every other status takes the skill's word.
  brief(code) -> {code, flag STOP|RULE|CAUTION|UNPROVEN|OK, status, never_read_as, empty_means, read_it_as}; an unknown code is REFUSED (ValueError)
  refuse_inputs(codes, decision_codes=()) -> {code: brief}: raises on any STOP; raises on a CAUTION among decision_codes (a CAUTION metric is
  a described reading only, never the basis of a decision line); a RULE passes with its rule in the brief."""
import importlib.util, os

MB_PATH = os.path.realpath(os.path.join(os.path.dirname(os.path.realpath(__file__)), '..', '..', 'LEAD', 'skills', 'reading-metrics',
                                        'scripts', 'metric_brief.py'))


class MetricRefused(ValueError):
    pass


def _mb():
    sp = importlib.util.spec_from_file_location('metric_brief', MB_PATH); m = importlib.util.module_from_spec(sp); sp.loader.exec_module(m)
    return m


_TABLES = {}


def _tables():
    if not _TABLES:
        MB = _mb(); cards = {r['code']: r for r in MB.rows(MB.METRICS)}
        for p in MB.CATALOGS:
            for r in MB.rows(p):
                cards.setdefault(r['code'], r)
        _TABLES.update(MB=MB, cards=cards, traps={r['code']: r for r in MB.rows(MB.TRAPS)})
    return _TABLES


def brief(code):
    T = _tables()
    card, trap = T['cards'].get(code), T['traps'].get(code)
    if card is None and trap is None:
        raise MetricRefused('%s: not in METRICS_V1, METRIC_TRAPS_V1 or the CTX / EPI catalogues: refused (find it with where_v2)' % code)
    status = (trap or {}).get('status') or ''
    f = T['MB'].flag(status)
    if trap is None:                                                    # SKEPTIC 02-07: no LAB4 row at all
        flag = 'UNPROVEN'
    else:                                                               # the skill's word (it flags every status that is not PROVEN)
        flag = f.split(':', 1)[0] if f else ('OK' if status.upper().startswith('PROVEN') else 'UNPROVEN')
    return {'code': code, 'flag': flag, 'status': status or 'NO LAB4 ROW',
            'never_read_as': (trap or {}).get('never_read_as') or '', 'empty_means': (trap or {}).get('empty_means') or '',
            'read_it_as': (trap or {}).get('read_it_as') or ''}


def refuse_inputs(codes, decision_codes=()):
    codes, decision_codes = list(codes), list(decision_codes)            # SKEPTIC 02-08: a generator is read once, here
    out = {c: brief(c) for c in list(dict.fromkeys(codes + decision_codes))}
    stop = [c for c, b in out.items() if b['flag'] == 'STOP']
    if stop:
        raise MetricRefused('STOP metrics refused: %s' % ', '.join('%s (%s)' % (c, out[c]['status']) for c in stop))
    caution = [c for c in decision_codes if out[c]['flag'] in ('CAUTION', 'UNPROVEN')]
    if caution:
        raise MetricRefused('CAUTION or UNPROVEN metrics in a decision line refused: %s' % ', '.join('%s (%s)' % (c, out[c]['status']) for c in caution))
    return out
