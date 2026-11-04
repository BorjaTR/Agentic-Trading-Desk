"""release_pins_v3_2_rel1.py: Owner STRATEGY/LEAD (the grader thread). New edition by SCOUT for the clean release (K6, 31 Oct 2026; the owner 30 Oct 2026 23:07 Berlin: "All alarm tools should work from the
release folder only"). Old file: release_pins_v3_2.py
e9067752ca5fbb93, never edited. Changed: it pins the rel1 chain (idea_to_grade_v3_2_rel1 and idea_to_grade_rel1)
and writes every path relative to the tree root F (the folder above team/: idea_to_grade_rel1.F), so a pins file holds on any machine
and in any copy of the Alarm folder; an executed file outside F is refused. The rest of this text is release_pins_v3_2.py's.
[V3.2, 26 Oct 2026: a NEW name for the signed V3.1 file release_pins_v3.py d468565d04d9fa01 (kept unchanged; exit engine ED3 imports i2g_rules_v1). Changes: the two blockers of REVIEW_IDEA_TO_GRADE_V3_1_EXT_V1 (net FILL_SHARE without NO_COST parents; a resting entry whose decision price is older than MAX_STALE_S is NO_PRICE) and the V3.2 file names.]
release_pins_v3_2.py (idea_to_grade V3 and V3.1, ALARMLIB seat, 25 Oct 2026): writes a V3 pins file: every Python file of the forensics tree a run
of idea_to_grade_v3_2 executes (the run process after warm-up, a spawned pool worker, and the detector's own code list), path -> sha16.
release_pins.py (V2.3.1) is unchanged and still writes V2 pins. A pins file is never overwritten.
  python3 -B release_pins_v3_2.py <new pins file>"""
import datetime as dt, json, multiprocessing as mp, os, sys
sys.dont_write_bytecode = True
HERE = os.path.dirname(os.path.realpath(__file__)); sys.path.insert(0, HERE)
import idea_to_grade_v3_2_rel1 as I3
import idea_to_grade_rel1 as I2


def main(path):
    if os.path.exists(path):
        raise SystemExit('REFUSED: %s exists (a pins file is never overwritten)' % path)
    I3.warm(); pins = I2.census_modules()
    import i2g_engine_rel1 as E2
    from concurrent.futures import ProcessPoolExecutor
    with ProcessPoolExecutor(1, mp_context=mp.get_context('spawn'), initializer=I3._worker_init) as ex:
        worker = ex.submit(E2.process_modules, True).result()
    for q, h in worker.items():
        if q in pins and pins[q] != h:
            raise SystemExit('REFUSED: %s differs between the run process and a worker' % q)
        pins[q] = h
    pins.pop(os.path.realpath(__file__), None)
    for f in ('idea_to_grade_v3_2_rel1.py', 'idea_to_grade_rel1.py', 'i2g_universe_v1.py', 'i2g_rules_v1.py', 'alarm_contract_v1.py'):   # the universe writer makes a run input
        pins[os.path.realpath(os.path.join(HERE, f))] = I2.sha16(os.path.join(HERE, f))
    out = [q for q in pins if not q.startswith(I2.F + os.sep)]
    if out:
        raise SystemExit('REFUSED: executed files outside the tree root %s: %s' % (I2.F, sorted(out)[:5]))
    pins = {os.path.relpath(q, I2.F): h for q, h in pins.items()}                # rel1: relative to the tree root
    doc = {'schema': 'I2G_PINS_V1', 'written_utc': dt.datetime.now(dt.timezone.utc).strftime('%Y-%m-%dT%H:%M:%SZ'), 'by': os.path.basename(sys.argv[0]),
           'paths': 'relative to the tree root (the folder above team/)', 'files': len(pins), 'pins': dict(sorted(pins.items()))}
    with open(path, 'x') as f:
        json.dump(doc, f, indent=1, sort_keys=True); f.write('\n')
    print('PINS %d files -> %s %s' % (len(pins), path, I2.sha16(path)))


if __name__ == '__main__':
    main(sys.argv[1])
