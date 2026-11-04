"""release_pins_aw1_rel1.py: Owner STRATEGY/LEAD (the grader thread). New by SCOUT for the clean release (K12, 31 Oct 2026; the owner 30 Oct
2026 23:07 Berlin: "All alarm tools should work from the release folder only"): idea_to_grade/release_pins_rel1.py 69394675bc8671f0 for the
aw1 command (alarm_process/idea_to_grade_aw1_rel1.py: the MONTH chain v2_2_2's grade step) in place of idea_to_grade_rel1; its pins file
is I2G_PINS_AW1_REL1.json beside it (paths relative to the tree root F; I2G_PINS_AW1.json, by STRATEGY's mk_aw1.py, named the dev tree's
absolute paths). Everything else is release_pins_rel1.py's: release_pins_rel1.py's text follows.
release_pins_rel1.py: it pins the rel1 edition of the V2.3.1 command and writes every path relative to the tree root F (the folder above
team/), so the pins file holds on any machine and in any copy of the Alarm folder; an executed file outside F is refused.
The rest of this text is release_pins.py's.
release_pins.py (i2g_grader, 25 Oct 2026): writes the release's pins file: every Python file of the forensics tree a run of
idea_to_grade executes (the run process after warm-up, a spawned pool worker, and the detector's own code list), path -> sha16. The run
refuses before staging when a pinned file differs (KERNEL_DRIFT) or when any process executes a file the pins do not list (UNPINNED_MODULE).
A changed file is a new release: run this again into a NEW file and point --pins at it.
  python3 -B release_pins_aw1_rel1.py <new pins file>"""
import datetime as dt, json, multiprocessing as mp, os, sys
sys.dont_write_bytecode = True
HERE = os.path.dirname(os.path.realpath(__file__)); sys.path.insert(0, HERE)
import idea_to_grade_aw1_rel1 as I


def pins_now():
    """{path relative to F: sha16} of every Python file of the tree F an aw1 rel1 run executes: the run process after warm-up, a spawned
    pool worker, the detector's own code list, and the command file itself; refused when a file differs between the two processes or
    lies outside F"""
    E = I.warm(); pins = I.census_modules()
    from concurrent.futures import ProcessPoolExecutor
    with ProcessPoolExecutor(1, mp_context=mp.get_context('spawn'), initializer=I._worker_init) as ex:
        worker = ex.submit(E.process_modules, True).result()
    for q, h in worker.items():
        if q in pins and pins[q] != h:
            raise SystemExit('REFUSED: %s differs between the run process and a worker' % q)
        pins[q] = h
    pins.pop(os.path.realpath(__file__), None)
    pins[os.path.realpath(os.path.join(HERE, 'idea_to_grade_aw1_rel1.py'))] = I.sha16(os.path.join(HERE, 'idea_to_grade_aw1_rel1.py'))
    out = [q for q in pins if not q.startswith(I.F + os.sep)]
    if out:
        raise SystemExit('REFUSED: executed files outside the tree root %s: %s' % (I.F, sorted(out)[:5]))
    return {os.path.relpath(q, I.F): h for q, h in pins.items()}                    # rel1: relative to the tree root


def main(path):
    if os.path.exists(path):
        raise SystemExit('REFUSED: %s exists (a pins file is never overwritten)' % path)
    pins = pins_now()
    doc = {'schema': 'I2G_PINS_V1', 'written_utc': dt.datetime.now(dt.timezone.utc).strftime('%Y-%m-%dT%H:%M:%SZ'), 'by': os.path.basename(sys.argv[0]),
           'paths': 'relative to the tree root (the folder above team/)', 'files': len(pins), 'pins': dict(sorted(pins.items()))}
    with open(path, 'x') as f:
        json.dump(doc, f, indent=1, sort_keys=True); f.write('\n')
    print('PINS %d files -> %s %s' % (len(pins), path, I.sha16(path)))


if __name__ == '__main__':
    main(sys.argv[1])
