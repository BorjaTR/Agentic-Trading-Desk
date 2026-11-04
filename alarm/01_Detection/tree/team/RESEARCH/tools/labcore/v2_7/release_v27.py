"""release_v27.py (ctxprof_shared for STRATEGY/LEAD, 25 Oct 2026; A46R REL-01 item F1/M1): writes labcore/FUNCTIONS_V2.tsv (every
FUNCTIONS_V1 row unchanged + one row per public function of labcore/v2_7, its sha16 = sha16 of the function's source, the rule of test
L11) and labcore/RELEASE_labcore_V2_7_CANDIDATE.json (every file RELEASE_labcore_V2_6.json pins, by the same pin, + the v2_7 files + the
staged candidates they import by path), then runs labcore.release.check on it and on V2_6. A CANDIDATE: promotion is LAB1's (pending).
  python3 -B release_v27.py <reason>"""
import hashlib, importlib, inspect, json, os, sys

HERE = os.path.dirname(os.path.realpath(__file__)); LC = os.path.dirname(HERE); TOOLS = os.path.dirname(LC)
F = os.path.realpath(os.path.join(TOOLS, '..', '..', '..'))
sys.path.insert(0, TOOLS)
from labcore import release, ids                                                       # noqa: E402
from labcore.v2_7 import selection, runs, cache, series, rows as v27rows, quality       # noqa: E402

REL = lambda p: os.path.relpath(os.path.realpath(p), F)
DOES = {
    'select': ('the one population selector: list | coin:X | coins:A,B | all | group:NAME | roster over first..last; law-checked days; canonical-roster membership; coverage receipt; EMPTY_SELECTED_POPULATION is a result',
               '(events_path, first, last, selection, group_file, subject, ...) -> Selection dict'),
    'resolve_selection': ("event_situations' interface (--coins A,B|ALL, --group-file F --group NAME) with roster membership checked", '(ev, coins, group, group_file, first, last) -> (set or None, record)'),
    'parse': ('a selection text -> (kind, value); BAD_SELECTION otherwise', 'str -> (str, str|None)'),
    'read_list': ("an event list as written: '#' lines, header, rows with ordinal, coin, t, UTC day", 'path -> dict'),
    'weekly_roster': ('the roster-of-record weeks (ROSTER_<monday>.csv, ROSTER_RULE_V1) touching a range as a dated group document; declared aliases', '(first, last, dir, aliases) -> (doc, info)'),
    'group_document': ('a group file (dated JSON schema 1, or tsv group|sector + coin) as the resolver document', '(path, first, last) -> doc'),
    'roster_document': ('the canonical lab roster (ROSTER_BUILD.json, pinned sha256) + roster-of-record members; its PRICE index pins of the requested days rechecked', '(first, last, extra, ...) -> (doc, info)'),
    'selected_text': ('the text of a list holding the original # lines, header and the selected rows byte-equal (pure)', 'Selection -> str'),
    'manifest_view': ('the Selection as a run plan / manifest records it (rows by count and digest)', 'Selection -> dict'),
    'utc_day': ('UTC day of a unix time', 'float -> YYYYMMDD'), 'canonical': ('canonical JSON text', 'obj -> str'),
    'sha256_bytes': ('full sha256 of bytes', 'bytes -> hex'), 'sha256_file': ('full sha256 of a file', 'path -> hex'),
    'SelectionRefused': ('raised with a code: BAD_SELECTION, UNKNOWN_COIN, UNKNOWN_GROUP, MALFORMED_*, REVERSED_RANGE, SEALED_REQUEST, ROSTER_*, DATED_GROUP', 'exception'),
    'check_stage': ('the whole-run check after every worker exited 0: expected day-parts whole, coins, rows, one seal per part kind, fixed pins equal and frozen, lab indexes unchanged, no partial write/aside/unexpected part', '(root, expect, frozen, lab_root, prefixes) -> dict; RunRefused'),
    'plan_identity': ('sha16 of a run plan (no out_root, no time): the identity resume and UP TO DATE match', 'dict -> sha16'),
    'part_problems': ('what is wrong with one written part against its expectation', '(index, {coins, rows}) -> [str]'),
    'top_files': ('sha16 of a run folder top-level files and _selection/', 'root -> {name: sha16}'),
    'find_resumable': ('the newest kept attempt of the same plan whose process is gone', '(out_root, plan_sha16) -> path|None; RunRefused RUN_ACTIVE'),
    'adopt_for_resume': ('take over a kept attempt: keep whole parts, move partial/aside/failing parts aside (never deleted)', '(old, out_root, expect, frozen, aside_dir) -> (stage, kept, moved)'),
    'replay_diff': ('two run folders byte for byte except the named telemetry (and telemetry-derived index hashes)', '(a, b) -> [differences]'),
    'adopt': ("a consumer's door: verify_committed (every committed byte, every block decoded) before any read", '(root, prefix) -> manifest; RunRefused'),
    'sha16_file': ('sha16 of a file (streamed)', 'path -> sha16'), 'sha16_bytes': ('sha16 of bytes', 'bytes -> sha16'),
    'stage': ('RE-EXPORT run_manifest_candidate.stage (decisions_fixer): a new staging folder', 'out_root -> path'),
    'commit': ('RE-EXPORT run_manifest_candidate.commit: manifest staged, folder renamed, manifest renamed last; part digests', '(pending, out_root, name, body) -> manifest'),
    'abort': ('RE-EXPORT run_manifest_candidate.abort: FAILED.json, kept as <out_root>.failed_<stamp>', '(pending, out_root, error) -> path'),
    'load_complete': ('RE-EXPORT run_manifest_candidate.load_complete', '(root, name, prefix) -> manifest'),
    'verify_committed': ('RE-EXPORT run_manifest_candidate.verify_committed: load_complete + every payload block through lab3', '(root, name, prefix, code_dir) -> manifest'),
    'write_json_atomic': ('RE-EXPORT run_manifest_candidate.write_json_atomic', '(path, obj) -> None'),
    'utc_now': ('RE-EXPORT run_manifest_candidate.utc_now', '() -> str'), 'RunRefused': ('RE-EXPORT run_manifest_candidate.RunRefused (code)', 'exception'),
    'vintage': ('the source vintage of cached reads: (path, size, mtime_ns, inode) of every file a read depends on', 'paths -> tuple'),
    'key': ('sha16 of a complete cache identity (kind, code, entity, dates, clock_s, settings_sha16, source_vintage)', 'dict -> sha16'),
    'IdentityCache': ('a bounded in-memory cache served only for the exact same identity; hits/misses/evictions', 'class'),
    'roster_unknown': ('REGISTERED from alarm_context_ed2 (context_fix2): the coins no PRICE index of a readable built day up to last names, inside the caller window; Context keeps its own copy (frozen) until LAB1 promotion switches its import (alarm_context_ed2.py.PENDING_ctxprof_shared_roster_unknown)', '(R, coins, last, event_days, law, outside) -> [coins]'),
    'parts_holding': ('RE-EXPORT clock_series.parts_holding: the parts of a day whose index names a code (metadata only, no value read)', '(R, code, day) -> [part] or None'),
    'read_day_typed': ('RE-EXPORT clock_series.read_day_typed: one code-day through the one lab3 reader, absence from metadata, every reader error propagates', '(R, code, day, coins, step) -> dict'),
    'read_day': ('RE-EXPORT clock_series.read_day (edition 2 4-tuple API)', '(R, code, day, coins) -> (v, k, sources, pos)'),
    'is_absence': ('RE-EXPORT clock_series.is_absence: an instance of lab3 NotBuilt (by class)', 'exc -> bool'),
    'ClockSeries': ('RE-EXPORT clock_series.ClockSeries: consecutive days of one code, typed states, window / event_window / normal', 'class'),
    'canon_rows': ('FIXED canonical rows of the lookahead guards: a NaN or None cell beside a number sorts (labcore/_rows.py V2_6 raises TypeError)', '(cols, mask) -> sorted rows'),
    'columns': ('RE-EXPORT labcore._rows.columns (unchanged)', 'rows -> {name: array}'),
    'check_window': ('S3 window first: first..last real days, first <= last, inside the caller window; reads nothing; call it first in every entry path', '(first, last, window) -> (first, last, (a, b) or None); SELECTION_OUTSIDE_WINDOW, BAD_WINDOW'),
    'in_window': ('S3: the caller window as a day predicate (every day when None)', 'window -> inside(day) -> bool'),
    'roster_universe': ("S3 event_cause's roster rule, window first: every coin of the PRICE index of each built readable day up to last, opening only window days, never the day before", '(R, last, window, law) -> (coins, days read)'),
    'known': ('S2 THE one quality rule (LAB1): a lab3 clock cell is KNOWN when v finite, e == 0, a >= 0, o >= 0, k set and <= its column time', '(v, e, a, o, k, col_us) -> bool array'),
    'counts': ('S2 (LAB1): why cells are not known, each counted once by the first failing rule', '(v, e, a, o, k, col_us) -> dict'),
}
USED = {'quality': 'every reader of lab3 clock values (S2: Profile clock_series, Context ed2 layer, Outcomes EPI units, idea_to_grade detect)', 'series': 'event_profile (its owner: clock_series.py stays in event_profile; physical move waits for LAB1)', 'rows': 'Context H2 controls (LAB1 request: same fix in labcore/_rows.py V3)', 'selection': 'event_profile/run_parallel.py (Profile, Context); next: event_situations, event_outcomes, event_cause, idea_to_grade',
        'runs': 'event_profile/run_parallel.py (Profile, Context)', 'cache': 'clock_series ClockSeries (phase B adoption), alarm_context_ed2 views (patch request)'}
TESTS = {'quality': 'labcore/tests/test_v27_quality.py (LAB1)', 'series': 'labcore/tests/test_v27_candidate.py B1-B2; event_profile/test_event_profile.py (owner)', 'rows': 'labcore/tests/test_v27_candidate.py B3', 'selection': 'labcore/tests/test_v27_candidate.py S1-S10; event_profile/test_run_parallel.py selector matrix',
         'runs': 'labcore/tests/test_v27_candidate.py R1-R3; event_profile/test_run_parallel.py K2 K3', 'cache': 'labcore/tests/test_v27_candidate.py C1-C4'}


def rows():
    out = []
    for mod in (selection, runs, cache, series, v27rows, quality):
        short = mod.__name__.split('.')[-1]
        for n, f in sorted(inspect.getmembers(mod, lambda x: inspect.isfunction(x) or inspect.isclass(x))):
            if n.startswith('_') or (f.__module__ != mod.__name__ and n not in DOES) or n not in DOES:
                continue
            reexp = f.__module__ != mod.__name__
            sha = hashlib.sha256(inspect.getsource(f).encode()).hexdigest()[:16]
            owner = ('event_profile (profile_fix2): clock_series.py, re-exported' if short == 'series' else 'LAB1' if short == 'quality'
                     else 'LAB1 (candidate by ctxprof_shared)')
            src = {'series': 'event_profile/clock_series.py (re-exported, not copied)', 'rows': 'labcore/_rows.py (re-exported)',
                   'runs': 'run_manifest_candidate.py (decisions_fixer; imported, not copied)'}.get(short, 'new')
            moved = 'alarm_context_ed2.py 0d70516ee7b5ea5a (context_fix2; its copy stays until LAB1 promotion)' if n == 'roster_unknown' else None
            out.append([n, 'labcore.v2_7.' + short, DOES[n][0], DOES[n][1], USED[short], TESTS[short], owner,
                        moved or (src if reexp else 'new (A46R REL-01)'), sha])
    return out


def main(reason):
    v1 = os.path.join(LC, 'FUNCTIONS_V1.tsv'); v2 = os.path.join(LC, 'FUNCTIONS_V2.tsv')
    text = open(v1, encoding='utf-8').read()
    if not text.endswith('\n'):
        text += '\n'
    text += ''.join('\t'.join(r) + '\n' for r in rows())
    tmp = v2 + '.tmp'; open(tmp, 'w', encoding='utf-8').write(text); os.replace(tmp, v2)
    base = json.load(open(os.path.join(LC, 'RELEASE_labcore_V2_6.json')))
    files = dict(base['files'])
    hdr = release.schema_sha16(v2); cols = ['function', 'module', 'sha16']
    files[REL(v2)] = {'role': 'labcore registry V2 = V1 rows + labcore/v2_7 rows (sha16 of each function source)', 'schema_sha16': hdr,
                      'value_columns': cols, 'value_sha16': release.value_sha16(v2, cols)}
    for f in sorted(os.listdir(HERE)):
        if f.endswith('.py') or f.endswith('.json') or f.endswith('.md'):
            files[REL(os.path.join(HERE, f))] = {'role': 'labcore V2_7 candidate (labcore/v2_7)', 'sha16': ids.sha16_file(os.path.join(HERE, f))}
    for p in (os.path.join(LC, 'tests', 'test_v27_candidate.py'), os.path.join(LC, 'tests', 'fault_child_wrapper.py'),
              os.path.join(LC, 'tests', 'test_v27_quality.py')):
        files[REL(p)] = {'role': 'labcore V2_7 candidate test', 'sha16': ids.sha16_file(p)}
    for p, why in ((runs.RM_PATH, 'imported by labcore.v2_7.runs (decisions_fixer candidate; LAB1 moves it into labcore in one step)'),
                   (selection.RESOLVER_PATH, 'imported by labcore.v2_7.selection (DEV2 shared resolver, OX-CODE1 approved L1)'),
                   (selection.EVSEL_PATH, 'imported by labcore.v2_7.selection (performance_v2 event_selection)'),
                   (selection.ROSTER_DOC, 'the canonical lab roster document read by labcore.v2_7.selection (also pinned by sha256 in its code)'),
                   (series.CS_PATH, 're-exported by labcore.v2_7.series (event_profile/clock_series.py, FROZEN 5b5a331ccd81c605, owner event_profile)')):
        files[REL(p)] = {'role': why, 'sha16': ids.sha16_file(p)}
    man = dict(base, release='V2_7_CANDIDATE', files=files, replaces='none: V2_6 stays the released labcore; this is a candidate beside it',
               status='CANDIDATE: NOT RELEASED. Promotion = a LAB1 release cycle; LAB1 is stopped: LAB1 authorization PENDING (never done).',
               by='ctxprof_shared for STRATEGY/LEAD (A46R REL-01), 25 Oct 2026', reason=reason,
               changes_from_V2_6='new files only: labcore/v2_7 (selection, runs, cache, ROSTER_WEEK_ALIASES_V1.json, release_v27.py, README), '
                                 'FUNCTIONS_V2.tsv, tests/test_v27_candidate.py, tests/fault_child_wrapper.py; every V2_6 pin unchanged',
               open_review=['labcore no-write contract: v2_7.runs re-exports the run-publication writers (stage/commit/abort) and moves parts '
                            'aside on resume: LAB1 architecture review before promotion', 'run_manifest_candidate.part_digest hashes every '
                            'payload block at commit (26.7 s Profile / 18.8 s Context at full A02P): patch request to decisions_fixer'],
               tests_result='filled by the cutter after the run (see HANDBACK_ctxprof_shared_V1.md)', written_utc=runs.utc_now())
    man.pop('signoff', None); man.pop('a36', None); man.pop('changes_from_V2_1', None)
    out = os.path.join(LC, 'RELEASE_labcore_V2_7_CANDIDATE.json')
    tmp = out + '.tmp'; open(tmp, 'w').write(json.dumps(man, indent=1, sort_keys=True) + '\n'); os.replace(tmp, out)
    release.check(out); release.check(os.path.join(LC, 'RELEASE_labcore_V2_6.json'))
    print('WROTE %s %s (%d files); FUNCTIONS_V2 %s; release.check PASS on V2_7_CANDIDATE and V2_6' % (out, ids.sha16_file(out), len(files),
                                                                                                 ids.sha16_file(v2)))


if __name__ == '__main__':
    main(' '.join(sys.argv[1:]) or 'unspecified')
