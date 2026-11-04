#!/usr/bin/env python3
"""clean_scratch_v2.py (SCOUT for ALARM_DESIGN KIT_V5, 30 Oct 2026; TEST, NOT REVIEWED). Runs inside a CLEAN job only (JOB_CLEAN_V6).
clean_scratch_v1.py (90e6dab92f49dee1) with its one machine path from the settings (CLEAN_RELEASE_V1 section 6): the scratch folder is the
settings key SCRATCH, which the queue (queue_job_v5.py) fills into the CLEAN job at queue time (--scratch @@SCRATCH@@); v1 took the drive
(--wdb <drive>, written into the V5 template) and added judge_scratch itself. Nothing else changed.
the owner 29 Oct 2026 14:52 Berlin: the agents "shouldn't fill up the SCRATCH_DISK disk and clean up after themselves logging the proof of what
they run and how it was run". This removes a run's OWN job scratch after the proof is on dev, and logs what it removed.

  python3 -B clean_scratch_v2.py <RUN_DIR> <SEAT> <OUT_DIR> <JOB[,JOB...]> --scratch <SCRATCH> (--dry | --apply)

For each job J (a receipts folder name <id>_<KIND>_<IDEA> of this run):
  - the proof must be on dev: RUN_DIR/receipts/J/STAGES.tsv with its end line and RUN_DIR/receipts/J/SHA16.txt; J not cleaned before
    (no CLEANED_BY.txt);
  - kept first (copied to RUN_DIR/receipts/J/, never overwritten): for GRADE, each variant's fire list (its sha16 must equal FIRES.tsv)
    and per-fire file; for MONTH, each variant's per-fire file;
  - removed: <scratch>/work_<RUN>/J/ only (it must resolve inside <scratch> and not be a symlink);
  - left for DSK, never removed: for ENTRY, the store places named in receipts/J/<V>/STORE_PLACES.tsv
    (<scratch>/work_TOOLTRIAL/chain/ALM_<SEAT>_<V>_SD_* and <scratch>/work_ALARMLIB/i2g_v3_2/full_ALM_<SEAT>_<V>_SD_*):
    work_TOOLTRIAL is a symlink into research/ and work_ALARMLIB is protected (team/DISK_RULES_V1.md rules 3 and 8; DSK HANDOVER V15
    items 7 and 9). They are logged with their size as LEFT FOR DSK.
  Refused: a store place not named for this seat and variant, a W folder that is a symlink or resolves outside <scratch>. --dry
  lists what it would remove and leave (bytes, files); --apply removes, checks it is gone, writes OUT_DIR/CLEANED.tsv (one row a path)
  and RUN_DIR/receipts/J/CLEANED_BY.txt.
"""
import sys, os, re, shutil, hashlib, datetime

KINDS = ('COUNT', 'GRADE', 'ENTRY', 'MONTH')


class Refused(Exception):
    pass


def sha16(p):
    h = hashlib.sha256()
    with open(p, 'rb') as f:
        for b in iter(lambda: f.read(1 << 20), b''):
            h.update(b)
    return h.hexdigest()[:16]


def size(p):
    n = b = 0
    for r, ds, fs in os.walk(p):
        for f in fs:
            try:
                b += os.lstat(os.path.join(r, f)).st_size; n += 1
            except OSError:
                pass
    return b, n


def stages(d):
    p = os.path.join(d, 'STAGES.tsv')
    if not os.path.isfile(p):
        return None
    rows = [l.rstrip('\n').split('\t') for l in open(p) if l.strip()][1:]
    return rows


def copy_keep(src, dst):
    if os.path.exists(dst):
        return 'kept before'
    with open(src, 'rb') as f, open(dst, 'xb') as g:
        shutil.copyfileobj(f, g)
    return 'kept'


def plan_job(run, seat, j, scratch):
    m = re.match(r'^[0-9]+_(%s)_[A-Z][A-Z0-9]*$' % '|'.join(KINDS), j)
    if not m:
        raise Refused('NOT A KIT_V5 JOB NAME %r' % j)
    kind = m.group(1)
    rd = os.path.join(run, 'receipts', j)
    st = stages(rd)
    if st is None or not any(r and r[0] == 'end' for r in st):
        raise Refused('%s: NO PROOF ON DEV (STAGES.tsv with an end line)' % j)
    if not os.path.isfile(os.path.join(rd, 'SHA16.txt')):
        raise Refused('%s: NO SHA16.txt IN ITS RECEIPTS' % j)
    if os.path.exists(os.path.join(rd, 'CLEANED_BY.txt')):
        raise Refused('%s: ALREADY CLEANED' % j)
    w = os.path.join(scratch, 'work_' + os.path.basename(run.rstrip('/')), j)
    keep, targets, left = [], [], []
    variants = sorted({r[0].split('_', 1)[1] for r in st if r and re.match(r'^grade_[A-Z][A-Z0-9]*$', r[0])})
    if kind == 'GRADE':
        fp = os.path.join(rd, 'FIRES.tsv')
        if os.path.isfile(fp):
            for l in open(fp):
                x = l.rstrip('\n').split('\t')
                if len(x) == 4:
                    v, n, s, path = x
                    src = os.path.join(w, '%s_FIRES_V1_LIST.tsv' % v)
                    keep.append((src, os.path.join(rd, '%s_FIRES_V1_LIST.tsv' % v), s))
        for v in variants:
            keep.append((os.path.join(w, 'PERFIRE_%s.tsv' % v), os.path.join(rd, 'PERFIRE_%s.tsv' % v), None))
    if kind == 'MONTH':
        for v in variants:
            keep.append((os.path.join(w, 'PERFIRE_%s.tsv' % v), os.path.join(rd, 'PERFIRE_%s.tsv' % v), None))
    if os.path.isdir(w):
        if os.path.islink(w) or not os.path.realpath(w).startswith(os.path.realpath(scratch) + os.sep):
            raise Refused('%s: ITS SCRATCH IS A SYMLINK OR RESOLVES OUTSIDE THE SCRATCH FOLDER %s: %s' % (j, scratch, w))
        targets.append(w)
    if kind == 'ENTRY':
        for v in sorted(os.listdir(rd)):
            sp = os.path.join(rd, v, 'STORE_PLACES.tsv')
            if not os.path.isfile(sp):
                continue
            pre = ('ALM_%s_%s_SD_' % (seat, v))
            for l in open(sp):
                x = l.rstrip('\n').split('\t')
                path = x[-1] if x and x[0] in (v, 'run') else None
                if not path:
                    continue
                if os.path.basename(path) == 'run':
                    path = os.path.dirname(path)          # the grader's run sits in the store's own full_<AID>_<dates>_<stamp>/ folder
                ok_chain = os.path.dirname(path) == os.path.join(scratch, 'work_TOOLTRIAL', 'chain') and os.path.basename(path).startswith(pre)
                ok_run = os.path.dirname(path) == os.path.join(scratch, 'work_ALARMLIB', 'i2g_v3_2') and os.path.basename(path).startswith('full_' + pre)
                if not (ok_chain or ok_run):
                    raise Refused('%s: STORE PLACE NOT OURS %s' % (j, path))
                if os.path.isdir(path) and path not in left:
                    left.append(path)
    return kind, rd, keep, targets, left


def main(argv):
    a = list(argv)
    mode = None
    for k in ('--dry', '--apply'):
        if k in a:
            mode = k; a.remove(k)
    if '--scratch' not in a or a.index('--scratch') + 1 >= len(a):
        raise Refused('USAGE ... --scratch <SCRATCH, the settings key> (--dry | --apply)')
    i = a.index('--scratch'); scratch = a[i + 1]; del a[i:i + 2]
    if mode is None or len(a) != 4:
        raise Refused('USAGE clean_scratch_v2.py RUN_DIR SEAT OUT_DIR JOB[,JOB] --scratch SCRATCH (--dry | --apply)')
    run, seat, out, jobs = a
    if not re.match(r'^[A-Z][A-Z0-9]{0,11}$', seat) or not os.path.basename(run.rstrip('/')).startswith(seat + '_'):
        raise Refused('SEAT %r DOES NOT MATCH THE RUN %s' % (seat, run))
    plans = [(j,) + plan_job(run, seat, j, scratch) for j in jobs.split(',') if j]
    now = lambda: datetime.datetime.now(datetime.timezone.utc).strftime('%Y-%m-%dT%H:%M:%SZ')
    total = 0
    log = []
    # 'total' counts only what is removed
    for j, kind, rd, keep, targets, left in plans:
        for src, dst, want in keep:
            if not os.path.isfile(src):
                print('%s KEEP MISSING %s' % (j, src)); continue
            if want and sha16(src) != want:
                raise Refused('%s: FIRE LIST CHANGED %s (FIRES.tsv says %s)' % (j, src, want))
            if mode == '--dry':
                print('%s WOULD KEEP %s -> %s' % (j, src, dst))
            else:
                r = copy_keep(src, dst)
                if want and sha16(dst) != want:
                    raise Refused('%s: KEPT COPY DIFFERS %s' % (j, dst))
                print('%s %s %s %s' % (j, r.upper(), dst, sha16(dst)))
        for t in targets:
            b, n = size(t); total += b
            if mode == '--dry':
                print('%s WOULD REMOVE %s %d bytes %d files' % (j, t, b, n)); continue
            shutil.rmtree(t)
            gone = not os.path.exists(t)
            log.append((now(), j, t, b, n, 'REMOVED' if gone else 'STILL THERE'))
            print('%s %s %s %d bytes %d files' % (j, 'REMOVED' if gone else 'STILL THERE', t, b, n))
            if not gone:
                raise Refused('%s: COULD NOT REMOVE %s' % (j, t))
        for t in left:
            b, n = size(t)
            if mode == '--dry':
                print('%s WOULD LEAVE FOR DSK %s %d bytes %d files (protected place)' % (j, t, b, n)); continue
            log.append((now(), j, t, b, n, 'LEFT FOR DSK (protected place)'))
            print('%s LEFT FOR DSK %s %d bytes %d files' % (j, t, b, n))
    if mode == '--apply':
        os.makedirs(out, exist_ok=True)
        p = os.path.join(out, 'CLEANED.tsv')
        new = not os.path.exists(p)
        with open(p, 'a') as f:
            if new:
                f.write('utc\tjob\tpath\tbytes\tfiles\tresult\n')
            for r in log:
                f.write('%s\t%s\t%s\t%d\t%d\t%s\n' % r)
        for j, kind, rd, keep, targets, left in plans:
            b = sum(r[3] for r in log if r[1] == j and r[5] == 'REMOVED')
            with open(os.path.join(rd, 'CLEANED_BY.txt'), 'x') as f:
                f.write('%s cleaned by %s: %d bytes removed in %d places, %d places left for DSK (CLEANED.tsv); the proof stays here\n' % (
                    now(), os.path.basename(out.rstrip('/')), b, sum(1 for r in log if r[1] == j and r[5] == 'REMOVED'), sum(1 for r in log if r[1] == j and r[5] != 'REMOVED')))
    print('%s TOTAL %d bytes over %d jobs' % ('WOULD REMOVE' if mode == '--dry' else 'REMOVED', total, len(plans)))
    return 0


if __name__ == '__main__':
    try:
        sys.exit(main(sys.argv[1:]))
    except Refused as e:
        print('REFUSED: %s' % e, file=sys.stderr)
        sys.exit(2)
