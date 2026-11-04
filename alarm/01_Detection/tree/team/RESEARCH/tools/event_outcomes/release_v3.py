"""release_v3.py: writes RELEASE_event_outcomes_V3_CANDIDATE.json (STRATEGY/LEAD builder, 25 Oct 2026; A51-07 / M1). The candidate pins
this tool's own files whole, the UNRELEASED candidate files it runs (whole: a change refuses every run until this candidate is re-cut on
purpose, never automatically) and names the released dependencies by their own releases (labcore, exit_engine, factory -> costs and
fairness_bar, label_ewsd, alarm_profile), plus the analyst python / numpy. event_outcomes.check_closure then refuses any loaded code file
the graph does not pin. Run it only after a reviewed change: python3 release_v3.py <reason>"""
import json, os, sys
HERE = os.path.dirname(os.path.realpath(__file__)); F = os.path.realpath(os.path.join(HERE, '..', '..', '..', '..'))
sys.path.insert(0, os.path.join(F, 'team', 'RESEARCH', 'tools'))
from labcore import ids, release                                     # noqa: E402
OWN = ['event_outcomes.py', 'OUTCOMES_CORE_V3.json', 'test_event_outcomes.py', 'test_a51_on_successor.py', 'test_outcomes_v3.py',
       'acceptance_v3.py', 'release_v3.py', 'README.md', 'ARCHITECTURE.md']
CANDIDATES = {'team/RESEARCH/tools/event_profile/run_parallel.py': 'the shared launcher (outcomes branch) run executes; ctxprof_shared, unreleased'}
RELEASES = ['team/RESEARCH/tools/labcore/RELEASE_labcore_V2_7.json', 'team/RESEARCH/tools/exit_engine/RELEASE_exit_engine_V1_7.json',
            'team/RESEARCH/tools/factory/RELEASE_factory_V7.json', 'team/RESEARCH/tools/bucket_proof/RELEASE_label_ewsd_V2_6.json',
            'team/RESEARCH/tools/alarm_profile/RELEASE_profile_V1_8.json']


def main(reason):
    rel = 'team/RESEARCH/tools/event_outcomes/'
    files = {rel + f: {'role': 'event_outcomes VERSION 3 (own)', 'sha16': ids.sha16_file(os.path.join(HERE, f))} for f in OWN}
    files.update({p: {'role': why, 'sha16': ids.sha16_file(os.path.join(F, p))} for p, why in CANDIDATES.items()})
    man = dict(release='event_outcomes_V3_CANDIDATE', status='CANDIDATE: NOT APPROVED; independent re-review of A51-01..07 pending',
               by='STRATEGY/LEAD builder (outcomes), 25 Oct 2026', reason=reason, replaces='none (VERSION 2 2017ed1cc2e4c6dd had no release)',
               files=files, releases={r: ids.sha16_file(os.path.join(F, r)) for r in RELEASES}, runtime=release.runtime(),
               data_vintage='none pinned here: every run freezes its own input vintages (PRICE / EPI index sha16, funding files) in RUN_FROZEN.json',
               open_findings=['see team/RESEARCH/tools/event_outcomes/A51_ANSWERS_V3.md'])
    p = os.path.join(HERE, 'RELEASE_event_outcomes_V3_CANDIDATE.json')
    tmp = p + '.tmp'; open(tmp, 'w').write(json.dumps(man, indent=1, sort_keys=True) + '\n'); os.replace(tmp, p)
    release.check(p)
    print('WROTE %s %s' % (p, ids.sha16_file(p)))


if __name__ == '__main__':
    main(' '.join(sys.argv[1:]) or 'unspecified')
