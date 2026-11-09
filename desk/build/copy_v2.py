#!/usr/bin/env python3
"""copy_v2.py: copy the released editions into a new staging folder (alarm/, alarm/alarm_design/, alarm/alarm_pipeline/, loop/; the repo holds
the two Alarm sub-editions at its top, see below), leaving out what EXCLUDES.tsv names. copy_v1.py did the same for one edition (the Alarm package into alarm/); since 9 Nov 2026 the
repo ships three Alarm editions and the learning loop, so one call copies every source and writes one record.

  python3 -B desk/build/copy_v2.py <new staging folder> <release folder>=<repo subfolder> [<release folder>=<repo subfolder> ...]

Example (the 9 Nov 2026 build; RELEASE is the folder that holds the installed editions):
  python3 -B desk/build/copy_v2.py STAGE RELEASE/Alarm/alarm/ALARM_V1_22_1=alarm RELEASE/Alarm/alarm_design/ALARM_BUILD_V26=alarm/alarm_design \\
      RELEASE/Alarm/alarm_pipeline/ALARM_PIPELINE_V1_4_1=alarm/alarm_pipeline RELEASE/Learning_Loop/learning_loop/LEARNING_LOOP_V1_1=loop

The staging folder must not exist (nothing is overwritten). Every file of each release is either copied byte for byte (cp -p semantics,
made writable by its owner: the install is read-only) to <repo subfolder>/<path in the release>, or listed in EXCLUDED.tsv beside this
script (path in the repo, pattern, category). An EXCLUDES.tsv pattern is an fnmatch on the path in the repo ('*' crosses '/'). A file whose
name or folder matches the never-open words (NEVER_OPEN below) is left out unread, whatever EXCLUDES.tsv says. A symbolic link is refused.
Then run scrub_v1.py on <staging>/alarm and <staging>/loop, the pin fixers and known_tests_v1.py on <staging>/alarm. The design pack and the
pipeline are staged inside alarm/ only so that one scrub and one pin chain cover them with the package (their tables pin package files);
at install they move to the repo top, alarm_design/ and alarm_pipeline/, because the package's own tests read every file of alarm/ as the
package (test_pins_current_v1 found the design pack's change history there as stale pins)."""
import fnmatch, os, re, shutil, sys

HERE = os.path.dirname(os.path.abspath(__file__))
NEVER_OPEN = re.compile(r'(?i:heldout|held_out|febmar)|(?<![A-Z])LOOK(?![A-Z])|(?:^|/)T8_|team/SCOUT/receipts')   # the owner's held-out rule: such files are never read, so never shipped (FIRSTLOOK, the first-look step, is not a LOOK path)


def rules():
    out = []
    for line in open(os.path.join(HERE, 'EXCLUDES.tsv'), encoding='utf-8'):
        if line.startswith('#') or line.startswith('pattern\t') or not line.strip():
            continue
        pat, cat, why = line.rstrip('\n').split('\t')
        out.append((pat, cat, why))
    return out


def main(argv):
    if len(argv) < 2 or any('=' not in a for a in argv[1:]):
        print(__doc__); return 2
    dst = os.path.abspath(argv[0])
    if os.path.exists(dst):
        print('REFUSED: %s exists' % dst); return 2
    pairs = [(os.path.abspath(a.split('=', 1)[0]), a.split('=', 1)[1].strip('/')) for a in argv[1:]]
    for rel, sub in pairs:
        if not os.path.isdir(rel):
            print('REFUSED: no release folder %s' % rel); return 2
    rs = rules(); kept = 0; gone = []
    used = {r[0]: 0 for r in rs}
    for rel, sub in pairs:
        for d, ds, fs in os.walk(rel):
            ds.sort()
            for f in sorted(fs) + [x for x in ds if os.path.islink(os.path.join(d, x))]:
                src = os.path.join(d, f)
                if os.path.islink(src):
                    print('REFUSED: a symbolic link in a release: %s' % src); return 2
                rp = os.path.join(sub, os.path.relpath(src, rel)) if sub else os.path.relpath(src, rel)
                if NEVER_OPEN.search(rp):
                    gone.append((rp, 'NEVER_OPEN', 'never_open')); continue
                hit = next((r for r in rs if fnmatch.fnmatch(rp, r[0])), None)
                if hit:
                    gone.append((rp, hit[0], hit[1])); used[hit[0]] += 1; continue
                os.makedirs(os.path.join(dst, os.path.dirname(rp)), exist_ok=True)
                shutil.copy2(src, os.path.join(dst, rp)); kept += 1
                os.chmod(os.path.join(dst, rp), os.stat(src).st_mode | 0o200)   # the install is read-only; the copy is ours to scrub
    with open(os.path.join(HERE, 'EXCLUDED.tsv'), 'w', encoding='utf-8') as fo:
        fo.write('# EXCLUDED.tsv (copy_v2.py): every file of %s left out of the repo\npath\tpattern\tcategory\n'
                 % ', '.join('%s (%s/)' % (os.path.basename(r), s) for r, s in pairs))
        for g in sorted(gone):
            fo.write('\t'.join(g) + '\n')
    unused = [p for p, n in used.items() if n == 0]
    print('COPIED %d files, EXCLUDED %d (never-open %d), rules unused: %s' % (kept, len(gone), sum(1 for g in gone if g[1] == 'NEVER_OPEN'),
                                                                           unused or 'none'))
    return 0


if __name__ == '__main__':
    sys.exit(main(sys.argv[1:]))
