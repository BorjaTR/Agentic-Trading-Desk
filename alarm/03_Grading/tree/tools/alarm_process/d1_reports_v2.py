#!/usr/bin/env python3
"""d1_reports_v2.py (SCOUT, 31 Oct 2026; TEST, NOT REVIEWED; d1_reports_v1.py a58352d077a14e9f with the Outcomes edition and the card
as arguments of chain (GRADE: event_outcomes_rel1, alarm_card_v1_2_1; MONTH: event_outcomes_aw1_rel1, alarm_card_v1_3_1), d1_mem_v2, and its
type-check findings fixed (a module spec checked, the dynamic imports marked, warnings._filters_mutated through getattr). v1: speed stage 2, D1: team/SCOUT/D1_BUILD_PLAN_V1.md 9b9edfc8a0e2de3f; step 0
job 20265186: 338 of 338 columns equal, the reports byte for byte): ONE process from Outcomes to the reports, the values from memory.
Review fix (CONDUCTOR's must M1, team/CONDUCTOR/reviews/REVIEW_SCOUT_D1_CODE_V2.md bcf771a7a532540e): the two Outcomes runs go through
concurrent.futures.ProcessPoolExecutor (spawn), not multiprocessing Pool.map: a run whose process dies (the RSS guard, an OOM kill, a
native crash) breaks the pool, so both runs give rc 1 at once (the reason on stderr) and the chain exits 6, never a wait for the watchdog.
  chain   F W V LAB_DAYS G FIRST LAST WINDOW LEAN SCREEN BASE XS EO CARD   (EO: the Outcomes edition run(0) runs; CARD: the card)
          for each list of XS (ALARM: W/<V>_FIRES_V1_LIST.tsv, RND: W/RND_<V>_V1_LIST.tsv) event_outcomes_rel1.run(0, ...) in its own
          spawned process, both at once, into W/om_<V>[RND]_v1 (log W/om_<V>[RND]_v1.log), each day's rows kept as they are written
          (d1_mem_v1.Capture) and kept beside the root as <root>.mem.pkl; then, when every run passed, menu_v2_1 (not with SCREEN 1) and
          alarm_card_v1_2_1 in this process with event_outcomes.read answering from those rows (d1_mem_v1.install), each written as
          the chain writes `cmd > file 2>&1`. Prints nothing; writes W/d1_<V>_steps.tsv: step, rc, seconds, out (the chain's STATUS
          lines, in its order).
  perfire F PERFIRE W V      perfire_v1_1 in this process, from the two roots' .mem.pkl; its output on stdout (the job's redirect).
  handoff F LEAD_NULL <lead_null args>
          lead_null_v1_1 in this process (sys.argv as its command line); each manifest row's two roots (lead_null's names
          <W>/om_<V>_v1, <W>/om_<V>RND_v1) with a .mem.pkl answered from it; its output on stdout.
A root read from a .mem.pkl is still checked against the store: its subject, and its days and coins against the store's own index
(d1_mem_v1.mem_read, MEM_MISMATCH). Writes only W's files named above and the .mem.pkl files. Never deletes."""
import concurrent.futures as cf, contextlib, importlib.util, io, multiprocessing as mp, os, pickle, runpy, sys, time, traceback, warnings

HERE = os.path.dirname(os.path.abspath(__file__))


def load(name, path):
    if name in sys.modules:
        return sys.modules[name]
    sp = importlib.util.spec_from_file_location(name, path)
    if sp is None or sp.loader is None:
        raise ImportError('no module at %s' % path)
    m = importlib.util.module_from_spec(sp)
    sys.modules[name] = m; sp.loader.exec_module(m); return m


def tools(F):
    T = os.path.join(F, 'team', 'RESEARCH', 'tools')
    return T, os.path.join(F, 'team', 'LAB3', 'code')


def outcomes(args):
    """one Outcomes run in this spawned process -> (rc, seconds, part, days)"""
    F, IN, G, SUBJ, FIRST, LAST, WIN, OUT, LAB, EO = args
    T, CODE = tools(F); sys.path.insert(0, CODE)
    t0 = time.time(); log = open(OUT + '.log', 'x')
    try:
        from lab3 import write as LW  # pyright: ignore[reportMissingImports]  (code_dir on sys.path)
        d1 = load('d1_mem_v2', os.path.join(HERE, 'd1_mem_v2.py'))
        EOR = load(os.path.basename(EO)[:-3], EO)
        cap = d1.Capture(LW.write_part)
        EOR.run(0, LAB, CODE, IN, G, SUBJ, FIRST, LAST, OUT, run_window=EOR._window_arg({'run-window': WIN}),
                roots={'CTX': None, 'EPG': None, 'CAUSE2': None}, log=lambda s: (log.write('%s\n' % s), log.flush()), inprocess_write=cap)
        with open(OUT + '.mem.pkl', 'xb') as f:
            pickle.dump({'part': cap.part, 'days': cap.days}, f, protocol=pickle.HIGHEST_PROTOCOL)
        return 0, int(time.time() - t0)
    except BaseException:
        log.write(traceback.format_exc()); return 1, int(time.time() - t0)
    finally:
        log.close()


def mem_of(roots):
    d1 = load('d1_mem_v2', os.path.join(HERE, 'd1_mem_v2.py')); mem = {}
    for root in roots:
        with open(root + '.mem.pkl', 'rb') as f:
            x = pickle.load(f)
        cap = d1.Capture(None); cap.part = x['part']; cap.days = x['days']
        mem[os.path.realpath(root)] = (cap, x['part'][4:])
    return d1, mem


def reader(F, mem):
    T, CODE = tools(F)
    for p in (os.path.join(T, 'event_outcomes'), T):
        if p not in sys.path:
            sys.path.insert(0, p)
    import event_outcomes as EO  # pyright: ignore[reportMissingImports]  (the tools folder on sys.path)
    d1 = load('d1_mem_v2', os.path.join(HERE, 'd1_mem_v2.py'))
    d1.install(EO, mem)
    return EO


def run_script(path, argv, out=None, env_W=None):
    """a tool's command line in this process: `path argv > out 2>&1` (a short output: stderr, then stdout); out None: to stdout"""
    so, se = io.StringIO(), io.StringIO(); rc = 0; old = sys.argv; oldW = os.environ.get('W')
    sys.argv = [path] + list(argv)
    if env_W is not None:
        os.environ['W'] = env_W
    t0 = time.time()
    try:
        with warnings.catch_warnings(), contextlib.redirect_stdout(so), contextlib.redirect_stderr(se):
            getattr(warnings, '_filters_mutated', lambda: None)()   # each tool sees its warnings once, as a process of its own would
            runpy.run_path(path, run_name='__main__')
    except SystemExit as e:
        if isinstance(e.code, int) or e.code is None:
            rc = e.code or 0
        else:
            se.write('%s\n' % e.code); rc = 1
    except BaseException:
        se.write(traceback.format_exc()); rc = 1
    finally:
        sys.argv = old
        if env_W is not None:
            if oldW is None:
                os.environ.pop('W', None)
            else:
                os.environ['W'] = oldW
    text = se.getvalue() + so.getvalue()
    if out is None:
        sys.stdout.write(text); sys.stdout.flush()
    else:
        with open(out, 'x') as f:
            f.write(text)
    return rc, int(time.time() - t0)


def chain(F, W, V, LAB, G, FIRST, LAST, WIN, LEAN, SCREEN, BASE, XS, EO, CARD):
    T, CODE = tools(F); steps = []; jobs = []
    for y in XS.split():
        x = '' if y == 'ALARM' else 'RND'
        IN = os.path.join(W, '%s_FIRES_V1_LIST.tsv' % V) if not x else os.path.join(W, 'RND_%s_V1_LIST.tsv' % V)
        jobs.append((x, (F, IN, G, 'IDEA2%s%sMENU' % (V, x), FIRST, LAST, WIN, os.path.join(W, 'om_%s%s_v1' % (V, x)), LAB, EO)))
    t0 = time.time(); res = []
    with cf.ProcessPoolExecutor(max_workers=len(jobs), mp_context=mp.get_context('spawn')) as ex:   # CONDUCTOR M1: a dead worker
        futs = [ex.submit(outcomes, a) for _, a in jobs]                                              # breaks the pool, never a hang
        for (x, a), fu in zip(jobs, futs):
            try:
                res.append(fu.result())
            except BaseException as e:
                sys.stderr.write('outcomes%s %s: %s: %s\n' % (x or '_alarm', a[7], type(e).__name__, e)); res.append((1, int(time.time() - t0)))
    ok = True
    for (x, a), (rc, sec) in zip(jobs, res):
        steps.append(('outcomes%s' % (x or '_alarm'), rc, sec, a[7])); ok = ok and rc == 0
    if ok:
        d1, mem = mem_of([a[7] for _, a in jobs]); reader(F, mem)
        if SCREEN != '1':
            rc, sec = run_script(os.path.join(T, 'alarm_process', 'menu_v2_1.py'), [V, 'om'], os.path.join(W, 'MENU_%s_om.txt' % V), env_W=W)
            steps.append(('menu', rc, sec, os.path.join(W, 'MENU_%s_om.txt' % V)))
        argv = [W, V] + (['--base', BASE] if BASE else []) + ['--lean', LEAN] + (['--screen'] if SCREEN == '1' else []) + ['--tsv', os.path.join(W, 'SUM_%s.tsv' % V)]
        rc, sec = run_script(CARD, argv, os.path.join(W, 'CARD_%s.txt' % V), env_W=W)
        steps.append(('card', rc, sec, os.path.join(W, 'CARD_%s.txt' % V)))
    with open(os.path.join(W, 'd1_%s_steps.tsv' % V), 'x') as f:
        f.write(''.join('%s\t%s\t%s\t%s\n' % s for s in steps))
    return 0


def main(a):
    cmd = a[0] if a else ''
    if cmd == 'chain' and len(a) == 15:
        return chain(*a[1:])
    if cmd == 'perfire' and len(a) == 5:
        F, PF, W, V = a[1:]
        d1, mem = mem_of([os.path.join(W, 'om_%s_v1' % V), os.path.join(W, 'om_%sRND_v1' % V)]); reader(F, mem)
        return run_script(PF, [W, V])[0]
    if cmd == 'handoff' and len(a) >= 4:
        F, LN, rest = a[1], a[2], a[3:]
        mf = rest[rest.index('--manifest') + 1]; roots = []
        lines = [l.rstrip('\n').split('\t') for l in open(mf) if l.strip()]
        head = lines[0]
        for f in lines[1:]:
            row = dict(zip(head, f))
            for r in ('%s/om_%s_v1' % (row['W'], row['V']), '%s/om_%sRND_v1' % (row['W'], row['V'])):   # lead_null's own root names
                if os.path.isfile(r + '.mem.pkl') and r not in roots:
                    roots.append(r)
        d1, mem = mem_of(roots); reader(F, mem)
        return run_script(LN, rest)[0]
    raise SystemExit(__doc__)


if __name__ == '__main__':
    sys.exit(main(sys.argv[1:]))
