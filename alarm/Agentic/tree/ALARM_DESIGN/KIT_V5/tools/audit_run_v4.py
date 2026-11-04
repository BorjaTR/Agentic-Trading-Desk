#!/usr/bin/env python3
"""audit_run_v4.py (SCOUT, 2 Nov 2026, ALARM_V1_20_1; GPT's must-fix): audit_run_v3.py unchanged plus A18 TRUE, the step that makes the row part of finishing. For every DECISIONS row from TRUE_REQUIRED_FROM on: an intact TRUE row of that idea and variant under receipts/*/TRUE_<V>_*/ (TRUE_ROW.tsv and its .sha16 equal, the card's sha16 equal, a word), its def_sha16 the VARIANTS row's, its label and mirror digests named on the variant's sealed card (true_label=, true_mirror=), and its perfire_sha16 equal to this variant's own row of the GRADE job's PERFIRE_SEAL.tsv. A job whose template, twin, stages or digest list say it had a seal needs it (queue_job_v14's fl_seal_expected); a job from before the seal prints UNVERIFIED as a warning. Any word finishes; the word changes no state. Earlier decisions are not asked. Exit 3 when A18 fails: the variant is not finished. Otherwise as audit_run_v3.py.
  python3 -B audit_run_v4.py --settings <settings file> <RUN> [--write]"""
import csv, glob, hashlib, importlib.util, os, sys
_s = importlib.util.spec_from_file_location('audit_run_v3', os.path.join(os.path.dirname(os.path.realpath(__file__)), 'audit_run_v3.py')); V3 = importlib.util.module_from_spec(_s); sys.modules['audit_run_v3'] = V3; _s.loader.exec_module(V3)
TRUE_REQUIRED_FROM = '2026-11-02T23:00:00Z'   # the adoption boundary of this edition; earlier finished work is not asked
WORDS = ('TRUE', 'NOT SUPPORTED', 'UNSURE')


def s16(p):
    with open(p, 'rb') as f:
        return hashlib.sha256(f.read()).hexdigest()[:16]


_q = None


def queue():
    """queue_job_v14, loaded once beside this file, for its one rule of when a job had a seal"""
    global _q
    if _q is None:
        s = importlib.util.spec_from_file_location('queue_job_v14_a', os.path.join(os.path.dirname(os.path.realpath(__file__)), 'queue_job_v14.py')); _q = importlib.util.module_from_spec(s); s.loader.exec_module(_q)
    return _q


def seal_row(run, job, V):
    """this variant's sha16 in the job's PERFIRE_SEAL.tsv (variant, sha16, ..., job), as queue_job_v14's fl_source reads it: the seal is the one SHA16.txt recorded, exactly one eight-column row of this variant and this exact job, else raises"""
    d = os.path.join(run, 'receipts', job); sp = os.path.join(d, 'PERFIRE_SEAL.tsv')
    if queue().fl_sha_line(d, 'PERFIRE_SEAL.tsv') != s16(sp):
        raise ValueError('the seal of %s is not the one its job recorded in SHA16.txt' % job)
    with open(sp) as f:
        rows = [l.rstrip('\n').split('\t') for l in f if l.strip()]
    mine = [r for r in rows if r[0] == V]
    if len(mine) != 1 or len(mine[0]) != 8 or mine[0][7] != job:
        raise ValueError('%d seal rows of %s from job %s; one expected' % (len(mine), V, job))
    return mine[0][1]


def true_faults(run, idea, V, def_sha16, grade_job='', card='', run_row=None, warns=None):
    """why this idea and variant has no intact TRUE row: [] when one exists. card: the text of the variant's sealed card."""
    why = []
    if not grade_job or grade_job == '-':
        return ['the decision names no GRADE job']
    if not os.path.isdir(os.path.join(run, 'receipts', grade_job)):
        return ['GRADE job %s has no receipts' % grade_job]
    seal = os.path.join(run, 'receipts', grade_job, 'PERFIRE_SEAL.tsv')
    if not os.path.isfile(seal):
        try:
            need = queue().fl_seal_expected(run, grade_job, V, run_row or {})
        except OSError:
            need = ['its stages cannot be read']
        if need:
            return ['GRADE job %s had a seal and it is gone: %s' % (grade_job, need[0])]
        if warns is not None:
            warns.append('%s %s: PERFIRE UNVERIFIED, job %s is from before the seal' % (idea, V, grade_job))
    for rp in sorted(glob.glob(os.path.join(run, 'receipts', '*', 'TRUE_%s_*' % V, 'TRUE_ROW.tsv'))):
        d = os.path.dirname(rp); n = os.path.basename(d)
        try:
            sc = os.path.join(d, 'TRUE_ROW.sha16')
            if not os.path.isfile(sc) or open(sc).read().strip() != s16(rp):
                why.append('%s: row damaged' % n); continue
            rows = list(csv.DictReader(open(rp), delimiter='\t'))
            if len(rows) != 1:
                why.append('%s: not one row' % n); continue
            r = rows[0]
            if r.get('idea') != idea or r.get('V') != V:
                why.append('%s: belongs to %s %s' % (n, r.get('idea'), r.get('V'))); continue
            if r.get('def_sha16') != def_sha16:
                why.append('%s: definition %s, sealed %s' % (n, r.get('def_sha16'), def_sha16)); continue
            if r.get('verdict') not in WORDS:
                why.append('%s: word %r' % (n, r.get('verdict'))); continue
            cp = os.path.join(d, 'TRUE_CARD.txt')
            if not os.path.isfile(cp) or s16(cp) != r.get('card_sha16'):
                why.append('%s: card damaged' % n); continue
            if os.path.isfile(seal) and r.get('perfire_sha16') != seal_row(run, grade_job, V):
                why.append('%s: PERFIRE %s is not %s\'s sealed one' % (n, r.get('perfire_sha16'), V)); continue
            if 'true_label=%s' % r.get('label_sha16') not in card or 'true_mirror=%s' % r.get('mirror_sha16') not in card:
                why.append('%s: label or mirror not the ones sealed on the card' % n); continue
            return []
        except (OSError, ValueError) as e:
            why.append('%s: %s' % (n, e))
    return why or ['no TRUE row']


class Audit(V3.Audit):
    def a18(self):
        fails = []; warns = []; var = {(r['idea'], r['V']): r for r in self.rows('VARIANTS')}; runs = {r['job']: r for r in self.rows('RUNS')}
        for r in self.rows('DECISIONS'):
            if r['utc'] < TRUE_REQUIRED_FROM:
                continue
            v = var.get((r['idea'], r['V']))
            if v is None:
                fails.append('%s %s: no VARIANTS row' % (r['idea'], r['V'])); continue
            cp = os.path.join(self.run, v.get('prereg_rel', ''))
            card = open(cp).read() if os.path.isfile(cp) else ''
            job = r.get('grade_job', ''); rr = runs.get(job, {})
            for w in true_faults(self.run, r['idea'], r['V'], v['def_sha16'], job, card, rr, warns):
                fails.append('%s %s: %s' % (r['idea'], r['V'], w))
        self.a18_fails = fails
        self.add('A18', 'TRUE', fails, warns)

    def runall(self):
        lines, nfail = V3.Audit.runall(self)
        self.a18()
        c = self.res[-1]; lines.insert(-2, '%-4s %-11s %s%s' % (c[0], c[1], c[2], '' if c[2] == 'PASS' else ' (%d)' % (c[5] or c[6])))
        i = len(lines) - 2
        lines[i:i] = ['       - %s' % x for x in (c[3] or c[4])]
        lines[0] = lines[0].replace('audit_run_v3.py', 'audit_run_v4.py')
        lines.append('FINISHED NO: A18' if self.a18_fails else 'FINISHED: every decision since %s has its TRUE row' % TRUE_REQUIRED_FROM)
        return lines, nfail + (1 if self.a18_fails else 0)


def main(argv):
    a = list(argv); write = '--write' in a; a = [x for x in a if x != '--write']; settings = None
    if '--settings' in a:
        i = a.index('--settings'); settings = a[i + 1] if i + 1 < len(a) else None; del a[i:i + 2]
    if len(a) != 1 or not V3.RUNTAG.match(a[0]) or not settings:
        raise SystemExit('USAGE audit_run_v4.py --settings <settings file> RUN [--write]')
    try:
        V3.configure(settings)
    except V3.Refused as e:
        raise SystemExit('REFUSED: %s' % e)
    au = Audit(a[0])
    if not os.path.isdir(au.run):
        raise SystemExit('NO RUN FOLDER %s' % au.run)
    lines, _ = au.runall()
    print('\n'.join(lines))
    if write:
        d = os.path.join(au.run, 'audit'); os.makedirs(d, exist_ok=True)
        p = os.path.join(d, 'AUDIT_%s.txt' % au.now.strftime('%Y%m%dT%H%M%SZ'))
        with open(p, 'x') as f:
            f.write('\n'.join(lines) + '\n')
        print('WRITTEN', p, V3.sha16(p))
    return 3 if au.a18_fails else 0


if __name__ == '__main__':
    sys.exit(main(sys.argv[1:]))
