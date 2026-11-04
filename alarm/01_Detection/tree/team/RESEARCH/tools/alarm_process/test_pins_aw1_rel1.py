#!/usr/bin/env python3
"""test_pins_aw1_rel1.py (SCOUT, K12, 31 Oct 2026; TEST, NOT REVIEWED): test_pins_v2_rel1.py (the GRADE pins' test) for the MONTH pins:
I2G_PINS_AW1_REL1.json and its maker release_pins_aw1_rel1.py, the relative pins of idea_to_grade_aw1_rel1's command (the MONTH chain
v2_2_2's grade step). The run refuses before staging when a pinned file differs (KERNEL_DRIFT) or when a process executes a file the pins
do not list (UNPINNED_MODULE, as job 20264797 was with v2_0_1 from the install).
On the files beside this one (the team/ layout of the dev tree), no lab data, no settings file: seconds.
  T1 the file: schema, count, every path relative to the tree root and inside team/, every pinned file here at its sha16;
  T2 idea_to_grade_aw1_rel1.load_pins maps it to this tree's real paths; recheck_pins passes (every pinned file as released);
  T3 the census (release_pins_aw1_rel1.pins_now in a fresh process: the run process after warm-up and a spawned worker) equals the pins
     exactly: no executed file unpinned, no pin that no run executes;
  T4 against I2G_PINS_AW1.json: the same 39 files with exactly the 11 clean editions in place of the old ones, the 28 others at the
     same sha16;
  T5 check_against_pins with these pins: the census passes; one more executed file is UNPINNED_MODULE; a changed hash is KERNEL_DRIFT;
  T6 the maker refuses a run that executed a file outside the tree root (one planted in the engine's files loaded by path).
Then planted bugs (in a copy of the pins file, and in the maker's text run in place of the maker): each must make a test fail.
  python3 -B test_pins_aw1_rel1.py           (exit 0: every test passed and every planted bug was caught)"""
import json, os, subprocess, sys, tempfile
sys.dont_write_bytecode = True
HERE = os.path.dirname(os.path.realpath(__file__)); sys.path.insert(0, HERE)
FO = os.path.realpath(os.path.join(HERE, '..', '..', '..', '..'))          # the tree root: FO/team/RESEARCH/tools/alarm_process
PINS = os.path.join(HERE, 'I2G_PINS_AW1_REL1.json'); OLD_PINS = os.path.join(HERE, 'I2G_PINS_AW1.json')
MAKER = os.path.join(HERE, 'release_pins_aw1_rel1.py')
SWAPS = {'team/RESEARCH/tools/alarm_process/idea_to_grade_aw1.py': 'team/RESEARCH/tools/alarm_process/idea_to_grade_aw1_rel1.py',
         'team/RESEARCH/tools/idea_to_grade/i2g_engine.py': 'team/RESEARCH/tools/idea_to_grade/i2g_engine_rel1.py',
         'team/RESEARCH/tools/idea_to_grade/i2g_grade.py': 'team/RESEARCH/tools/idea_to_grade/i2g_grade_rel1.py',
         'team/RESEARCH/tools/idea_to_grade/detect.py': 'team/RESEARCH/tools/idea_to_grade/detect_v2.py',
         'team/RESEARCH/tools/alarm_design/alarm_design_v2.py': 'team/RESEARCH/tools/alarm_design/alarm_design_v3.py',
         'team/RESEARCH/tools/alarm_stamp/alarm_stamp.py': 'team/RESEARCH/tools/alarm_stamp/alarm_stamp_ed1_1.py',
         'team/RESEARCH/tools/alarm_context/alarm_context.py': 'team/RESEARCH/tools/alarm_context/alarm_context_ed1_1.py',
         'team/OUTSIDE/COORD/development/DEV1/b2_performance_v1/alarm_stamp_projection_v1.py': 'team/OUTSIDE/COORD/development/DEV1/b2_performance_v1/alarm_stamp_projection_v2.py',
         'team/OUTSIDE/COORD/development/DEV1/b2_performance_v1/draw_prepared_v1.py': 'team/OUTSIDE/COORD/development/DEV1/b2_performance_v1/draw_prepared_v2.py',
         'team/OUTSIDE/COORD/development/DEV1/b2_performance_v1/prepared_activity_v1.py': 'team/OUTSIDE/COORD/development/DEV1/b2_performance_v1/prepared_activity_v2.py',
         'team/OUTSIDE/COORD/development/DEV1/opportunity_compare_v1/compare.py': 'team/OUTSIDE/COORD/development/DEV1/opportunity_compare_v1/compare_v2.py'}
CENSUS = r'''import json, sys, types
sys.dont_write_bytecode = True
if __name__ == '__main__':                          # a spawned worker imports this file again: it must not run the census
    maker, text = sys.argv[1], open(sys.argv[2]).read()
    m = types.ModuleType('release_pins_aw1_rel1'); m.__file__ = maker       # as when the maker runs: one executed file of the tree
    sys.modules['release_pins_aw1_rel1'] = m
    exec(compile(text, maker, 'exec'), m.__dict__)
    if len(sys.argv) > 3:                           # T6: one more executed file, outside the tree (as a kernel loaded by path)
        import i2g_engine_rel1 as E
        E.LOADED_BY_PATH.append(sys.argv[3])
    print(json.dumps(m.pins_now(), sort_keys=True))
'''


def sha16(p):
    import hashlib
    return hashlib.sha256(open(p, 'rb').read()).hexdigest()[:16]


def census(maker_text, tmp, outside=None):
    """the maker's pins_now() in a fresh process (the maker's text run as the maker file, so it finds its tree); outside: one more executed
    file outside the tree"""
    t = os.path.join(tmp, 'maker_text.py'); c = os.path.join(tmp, 'census.py')
    open(t, 'w').write(maker_text); open(c, 'w').write(CENSUS)
    p = subprocess.run([sys.executable, '-B', c, MAKER, t] + ([outside] if outside else []), capture_output=True, text=True, cwd=tmp, timeout=300)
    if p.returncode != 0:
        return None, (p.stdout + p.stderr)[-300:]
    return json.loads(p.stdout.strip().splitlines()[-1]), ''


def outside_refused(maker_text, tmp):
    """T6: the maker refuses an executed file outside the tree root"""
    q = os.path.join(tmp, 'outside_kernel.py'); open(q, 'w').write('# a kernel outside the tree\n')
    got, err = census(maker_text, tmp, outside=q)
    return got is None and 'REFUSED: executed files outside the tree root' in err


def tests(pins_path, maker_text, tmp, cached=None):
    """-> failures (T1-T5) of one pins file and one maker text"""
    import idea_to_grade_aw1_rel1 as I2
    f = []
    try:
        doc = json.load(open(pins_path)); pins = doc['pins']
    except (OSError, ValueError, KeyError) as e:
        return ['T1 unreadable %s' % e]
    # T1
    if doc.get('schema') != 'I2G_PINS_V1' or doc.get('files') != len(pins) or len(pins) != 39 or 'relative' not in doc.get('paths', ''):
        f.append('T1 header %s' % {k: v for k, v in doc.items() if k != 'pins'})
    for q, h in sorted(pins.items()):
        if os.path.isabs(q) or '/../' in '/%s/' % q or not q.startswith('team/'):
            f.append('T1 not relative inside team/: %s' % q); continue
        p = os.path.join(FO, q)
        if not os.path.isfile(p) or sha16(p) != h:
            f.append('T1 %s is %s here, pinned %s' % (q, sha16(p) if os.path.isfile(p) else 'MISSING', h))
    # T2
    try:
        real = I2.load_pins(pins_path)
        if sorted(real) != sorted(os.path.realpath(os.path.join(FO, q)) for q in pins) or any(not q.startswith(FO + os.sep) for q in real):
            f.append('T2 load_pins paths')
        I2.recheck_pins(real)
    except Exception as e:
        f.append('T2 %s' % str(e)[:200]); real = None
    # T3
    (got, err), t6 = cached if cached is not None else (census(maker_text, tmp), outside_refused(maker_text, tmp))
    if got is None:
        f.append('T3 census failed: %s' % err)
    elif got != pins:
        f.append('T3 census differs: unpinned %s, never executed %s, other hash %s' % (sorted(set(got) - set(pins))[:3], sorted(set(pins) - set(got))[:3],
                 sorted(q for q in set(got) & set(pins) if got[q] != pins[q])[:3]))
    # T6
    if not t6:
        f.append('T6 the maker took an executed file outside the tree root')
    # T4
    old = {q.split('/forensics/', 1)[1]: h for q, h in json.load(open(OLD_PINS))['pins'].items()}
    want = sorted(SWAPS.get(q, q) for q in old)
    if sorted(pins) != want:
        f.append('T4 files: extra %s, missing %s' % (sorted(set(pins) - set(want))[:3], sorted(set(want) - set(pins))[:3]))
    same = [q for q in old if q not in SWAPS]
    if len(same) != 28 or any(pins.get(q) != old[q] for q in same):
        f.append('T4 the 28 unchanged files: %s' % [q for q in same if pins.get(q) != old[q]][:3])
    # T5
    if real is not None and got is not None:
        obs = {os.path.realpath(os.path.join(FO, q)): h for q, h in got.items()}
        try:
            I2.check_against_pins(real, obs, 'test')
        except Exception as e:
            f.append('T5 the census is refused: %s' % str(e)[:200])
        extra = dict(obs); extra[os.path.join(FO, 'team', 'RESEARCH', 'tools', 'alarm_process', 'idea_to_grade_aw1.py')] = '0' * 16
        try:
            I2.check_against_pins(real, extra, 'test'); f.append('T5 an unpinned file passed')
        except Exception as e:
            if 'UNPINNED_MODULE' not in str(e):
                f.append('T5 unpinned: %s' % e)
        drift = dict(obs); k0 = sorted(drift)[0]; drift[k0] = 'f' * 16
        try:
            I2.check_against_pins(real, drift, 'test'); f.append('T5 a changed file passed')
        except Exception as e:
            if 'KERNEL_DRIFT' not in str(e):
                f.append('T5 drift: %s' % e)
    return f


def planted(tmp, maker_text, good):
    """-> (killed, total): every planted bug must make tests() fail"""
    doc = json.load(open(PINS)); p0 = dict(doc['pins']); bugs = []
    def pins_bug(name, change):
        d = json.loads(json.dumps(doc)); change(d); q = os.path.join(tmp, 'PINS_%s.json' % name)
        json.dump(d, open(q, 'w'), indent=1, sort_keys=True); bugs.append((name, q, maker_text))
    k = sorted(p0)
    pins_bug('drop_one', lambda d: d['pins'].pop(k[0]) and d.update(files=38))
    pins_bug('drop_engine', lambda d: d['pins'].pop('team/RESEARCH/tools/idea_to_grade/i2g_engine_rel1.py') and d.update(files=38))
    pins_bug('one_hash', lambda d: d['pins'].update({k[1]: '0' * 16}))
    pins_bug('absolute', lambda d: d['pins'].update({FO + '/' + k[2]: d['pins'].pop(k[2])}))
    pins_bug('dotdot', lambda d: d['pins'].update({'team/../' + k[3]: d['pins'].pop(k[3])}))
    pins_bug('old_engine', lambda d: (d['pins'].pop('team/RESEARCH/tools/idea_to_grade/i2g_engine_rel1.py'),
                                      d['pins'].update({'team/RESEARCH/tools/idea_to_grade/i2g_engine.py': '22a029e9b74311a0'})))
    pins_bug('old_detect', lambda d: (d['pins'].pop('team/RESEARCH/tools/idea_to_grade/detect_v2.py'),
                                      d['pins'].update({'team/RESEARCH/tools/idea_to_grade/detect.py': '5ced7c1a40356a7f'})))
    pins_bug('extra_pin', lambda d: (d['pins'].update({'team/RESEARCH/tools/idea_to_grade/detect.py': '5ced7c1a40356a7f'}), d.update(files=40)))
    pins_bug('count', lambda d: d.update(files=38))
    pins_bug('schema', lambda d: d.update(schema='I2G_PINS_V2'))
    def maker_bug(name, a, b):
        assert maker_text.count(a) == 1, ('maker bug target not found once', a)
        bugs.append((name, PINS, maker_text.replace(a, b, 1)))
    maker_bug('maker_keeps_itself', "pins.pop(os.path.realpath(__file__), None)", "pass")
    # not planted: dropping the line that adds idea_to_grade_aw1_rel1.py by name is an equivalent change (the maker imports the module, so the
    # census holds it anyway, as release_pins.py's own line was)
    maker_bug('maker_relative_off', "return {os.path.relpath(q, I.F): h for q, h in pins.items()}", "return dict(pins)")
    maker_bug('maker_outside_ok', "if out:\n        raise SystemExit", "if False:\n        raise SystemExit")
    # the maker names the old command file (in this tree) in place of the new one. Never the old command itself: its built-in dev root
    # would run the dev tree's kernels on the Mac (job 20264833: the hook saw the census open the dev tree's draw_v3, fill_v2, lab3 ...)
    maker_bug('maker_names_old_command', "pins[os.path.realpath(os.path.join(HERE, 'idea_to_grade_aw1_rel1.py'))] = I.sha16(os.path.join(HERE, 'idea_to_grade_aw1_rel1.py'))",
              "pins[os.path.realpath(os.path.join(HERE, 'idea_to_grade_aw1.py'))] = I.sha16(os.path.join(HERE, 'idea_to_grade_aw1.py'))")
    killed = 0
    for name, q, mt in bugs:
        f = tests(q, mt, tmp, cached=good if mt == maker_text else None)
        print('PLANTED BUG %-22s %s' % (name, 'KILLED (%s)' % f[0][:90] if f else 'SURVIVED'))
        killed += bool(f)
    return killed, len(bugs)


def main():
    maker_text = open(MAKER).read()
    with tempfile.TemporaryDirectory() as tmp:
        good = (census(maker_text, tmp), outside_refused(maker_text, tmp))
        f = tests(PINS, maker_text, tmp, cached=good)
        print('PINS TESTS', 'PASS (T1-T6, %d pins, census %d files)' % (len(json.load(open(PINS))['pins']), len(good[0][0] or {})) if not f else 'FAIL %s' % f)
        k, n = planted(tmp, maker_text, good)
        print('PLANTED BUGS %d of %d killed' % (k, n))
    return 0 if not f and k == n else 1


if __name__ == '__main__':
    sys.exit(main())
