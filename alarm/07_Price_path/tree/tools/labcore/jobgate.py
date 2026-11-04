"""labcore.jobgate (BUILD2, 23 Oct 2026; ASK BUILD1-132312; LAB1 13:20:39Z: 'every batch job waits on the gate at start and between
chunks (labcore gate_wait)'). MOVED verbatim from team/FEED/code/gate_wait_v1.py 3dc746099a47153e (BUILD1 for LIVE4); gate_wait fixed to BUILD1 e2fe77ffd73b53f9 (ASK BUILD1-135033: waited = sum of polls, no clock); BUILD1 retires
its copy once a job imports this one. Owner LAB1.
  gate_wait(gate=GATE, poll_s=30, log=print, max_wait_s=None, sleep=None, job_id=None, jitter_max_s=300) -> seconds waited (the sum of
  the sleeps; sleep None = time.sleep). job_id (LIVE4 14:30:31Z): after a PAUSE, wait jitter_s(job_id) more (0-300 s, fixed by the id) and
  read the gate again, so jobs resume one at a time; a job that never saw PAUSE starts at once.
  jitter_s(job_id, max_s=300) -> int seconds from sha256 of the id text (never builtin hash())
  Blocks while the first line of team/FEED/stops/BACKFILL_GATE.txt is not RUN (a missing or unreadable gate is PAUSE: a job never runs
  blind). Prints one line when it starts waiting and one when it goes on. max_wait_s: raise TimeoutError after it (None = wait).
Use in a job: gate_wait() before the first chunk and between chunks; a chunk already running is never killed by the gate.
  from labcore.jobgate import gate_wait"""
import hashlib, os, time

GATE = '<LAB_REPO>/forensics/team/FEED/stops/BACKFILL_GATE.txt'


def state(gate=GATE):
    try:
        with open(gate) as f:
            s = f.readline().strip().upper()
        return s if s in ('RUN', 'PAUSE') else 'PAUSE'
    except OSError:
        return 'PAUSE'


def jitter_s(job_id, max_s=300):
    """0..max_s seconds, fixed by the job id: sha256 of its text (a seed from an explicit key, never builtin hash())"""
    return int(hashlib.sha256(str(job_id).encode()).hexdigest()[:8], 16) % (int(max_s) + 1)


def gate_wait(gate=GATE, poll_s=30, log=print, max_wait_s=None, sleep=None, job_id=None, jitter_max_s=300):
    """-> seconds waited = the sum of the sleeps (deterministic; a planted sleep counts the same as a real one, TEST2 13:42:41Z)"""
    sleep = time.sleep if sleep is None else sleep
    waited = 0; said = False; jittered = False
    while True:
        while state(gate) != 'RUN':
            if not said:
                log('gate_wait: %s reads PAUSE: waiting (polling every %d s)' % (gate, poll_s)); said = True
            if max_wait_s is not None and waited >= max_wait_s:
                raise TimeoutError('gate_wait: still PAUSE after %d s' % waited)
            sleep(poll_s); waited += poll_s
        if said and job_id is not None and not jittered:               # resume one at a time, then read the gate again
            j = jitter_s(job_id, jitter_max_s); jittered = True
            log('gate_wait: RUN: job %s waits its %d s turn' % (job_id, j)); sleep(j); waited += j
            continue
        break
    if said:
        log('gate_wait: RUN after %d s: going on' % waited)
    return waited
