# 1. The challenges of working with agents

An LLM agent is a language model that runs in a loop: it reads a prompt and files, calls tools, reads their output and decides the next call, until it stops. This chapter lists the ways such agents fail, in the words the research literature uses, and for each one: how often it happened here, what we do about it, and whether that guard is itself tested. Chapters 7 to 11 and 17 describe the guards in full.

**Words used in this chapter.** Research here is done in runs. In each run one agent does the research (the researcher), a second agent scores the finished run (the scoring agent), and a third files what was learned into the shared knowledge store (the knowledge agent). The orchestrator is the agent that builds and launches runs, watches them and keeps the books; it is itself an LLM agent. A run has rounds: numbered steps of the same study (round 1, round 2, round 3). A receipt is the saved file or tool output a number came from. To seal a forecast or claim is to write it and record its fingerprint (a short code computed from the file's bytes, which changes if a single byte changes) before the result exists, so any later change shows. An alarm is a rule that marks moments on a coin; a fire is one such moment, one coin at one second; a wave is a cluster of fires close together in time, counted as one event. A memory run is a run whose researcher gets a short brief of what earlier runs learned; a control run is the same task with no memory. A practice test is a small task with an answer key kept hidden from the agent, used to test one part of the process on a fixed set of inputs. The process is split into numbered parts, and each part has a level: WEAK (a test failed, or open blockers), WORKS (one test passed) or PROVEN (two rounds of practice tests with two agents each passed, or one practice test plus a live run), followed by its score, for example PROVEN 6 of 6.

## 1.0 How to read the counts

- **Registers.** Four registers hold the evidence. The mistake files: the scoring agent's mistake rows for each run, each with a fixed key (for example "overclaim") and a kind (the researcher's own mistake, a tool's, or a page's). The register of unclear lines: every line of a process page that a reader could act on two ways, or that is missing or contradicts another line. The failures log: every refusal or failure with its exact words, cause and fix. The hot-fix log: every change made to tools or pages while runs were going.
- **Mistake keys used below.** Overclaim (a claim the numbers do not support); no tool (a step done by the agent's own script, or with no tool at all, where a tool should have done it); rework (the agent's own jobs or files redone without a recorded cause); stop (the pipeline stopped at a step for a stated reason).
- **Units.** A run is the independent unit. 16 assessed runs have a mistake file (7 control runs and 9 memory runs); 37 more mistake files are practice-test replays, where a fresh agent repeats a step on a fixed set of inputs. Run counts and practice-test counts are always given apart, because a practice test can plant faults on purpose.
- **Literature** means a published source in 1.20. A judgement with no source is said to be one.
- **Status of a control.** *Tested* means it has its own tests or practice test with a pass bar. *Rule in text* means agents are told to do it and nothing checks it.

## 1.1 Taxonomy

Classes: **integrity** (the result is not what it claims), **memory** (what the agent knows), **control** (keeping the agent on the task and alive), **environment** (tools, machine, files), **coordination** (several agents and the owner), **statistics** (fooling ourselves with many looks).

| # | challenge (literature term) | class | how often here | main control | test of the control |
|---|---|---|---|---|---|
| 1.2 | cheating on the scorer (reward hacking, specification gaming) | integrity | 5 of 43 failures-log rows are refusals of an edit or copy after a seal; 0 known scorer edits | released tools read-only; seals by fingerprint; at most 3 tries per idea | refusals observed in live runs; no planted-cheat practice test yet (open) |
| 1.3 | saying more than the numbers show (overclaiming, sycophancy) | integrity | overclaim in 15 of 16 assessed runs, 37 rows, 0 to 6 per run | numbers rule; the scoring agent counts every overclaim | scoring-agent practice tests; scorer agreement bar 0.80 (6 tests) |
| 1.4 | wrong reports about own work (unfaithful self-report, weak verification) | integrity | 2 counting errors in the failures log (one by the orchestrator); reproduction check run in 2 of 21 series rows, both "no" | separate scoring agent recomputes from receipts; orchestrator checks one number by its own route | the scoring and knowledge roles PROVEN 6 of 6; reproduction check mostly not run (open) |
| 1.5 | seeing data it must not see (leakage, contamination) | integrity / statistics | 1 hidden-month breach in 14 scanned runs, 7 unscanned; 3 held-out hygiene rows in the failures log; 6 held-out leak lines among the unclear lines | month windows in code; a leak scanner; hidden-month scan | 7 tests; safety and data integrity PROVEN 3 of 3; model memory cannot be fenced |
| 1.6 | losing track inside a long session (context limits, lost in the middle, context rot, compaction loss) | memory | not counted by any register (gap); MAST measures 2.8% of failures as loss of history | short pinned pages; one goal per session; a short page per role with its goal and next step | rules page size bar under 8 KB; no compaction practice test (open) |
| 1.7 | forgetting across sessions, repeating mistakes | memory | 20 of 45 distinct keys repeat in more than one mistake file; repeats per run: mean 2.21 (memory) vs 4.43 (control) | knowledge store written only by the knowledge builder; brief; handover files | knowledge store and builder PROVEN 23 of 23; handover and restart PROVEN 6.5 of 7 |
| 1.8 | re-finding the known (rediscovery, low novelty) | memory / statistics | rediscovery "yes" in 9 of 21 runs, every run from the eleventh memory run on; overlap 80.7 to 100% in 7 of 8 measured runs | novelty step in the alarm pipeline | runs every run; no fix yet (open) |
| 1.9 | wandering off the task (task derailment, goal drift) | control | not counted by key (gap); MAST: derailment 7.4%, disobey task spec 11.8% | goal and scope page; takeover gate; a round checker | 8 tests; PROVEN 5 of 5 |
| 1.10 | errors that pile up over many steps (error compounding, self-conditioning) | control | rework 43 rows (8 in runs, 35 in practice tests); stop 62 rows | rounds sealed; "two failed tries on one step: stop"; fresh agent per role | rule in text; checked after the fact by the scoring agent |
| 1.11 | the agent stops or goes silent (liveness, termination failures) | control / environment | 1 night (8 to 9 Nov 2026, 2 runs) from the orchestrator's account; no register row (gap) | watch every 3 minutes | rule in text; no planted-stall test (open) |
| 1.12 | one line read two ways (underspecified instructions) | control | 2,424 unclear lines, 1,012 of them read two ways; cold readers: 383 lines in 14 reports, 17 to 39 per report | 2 cold readers per run; triage of unclear lines; frozen pages | 1 test; unclear-line reports WEAK; reader agreement not measured (open) |
| 1.13 | too sure of the next idea (overconfidence, poor calibration) | statistics | memory forecasts: mean signed error -0.13 points, 12 of 16 intervals cover; control: -3.21 points, 7 of 8 cover | sealed forecast with 80% interval; a forecast scorer | forecast scorer PROVEN 3 of 3; forecasts WORKS 14 of 19 |
| 1.14 | luck read as skill (garden of forking paths, backtest overfitting, holdout reuse) | statistics | first series: 5 of 15 passes held after; 21 runs on the same Sep to Jan months | at most 3 tries per idea; one-look holdout; memory vs control | proof checker PROVEN 10 of 10; no PBO yet (open) |
| 1.15 | wrong tool use, or no tool (tool-use errors, tool bypass) | environment | no-tool rows 84 (16 in runs); 5 failures-log rows of wrong metric scope or input name; steps done by hand 0 in all 21 runs | released tools only; the metric brief; no-tool lines | metric use PROVEN 8 of 9; steps by hand counted per run |
| 1.16 | brittle machine, unsafe restart (environment faults, non-idempotent resume) | environment | 9 failures-log rows environment, 5 restart or resume | job sheet with tested commands; fresh pipeline folders; refusal to overwrite an output; lessons register | 20 tests; resume not tested on a planted half-run (open) |
| 1.17 | deleting or publishing by mistake (destructive actions) | control / environment | 1 failures-log row (cleanup removed stores a tool re-reads) | a scratch cleaner with keep list and log; owner-only deletes and pushes | 2 tests; scratch cleanup PROVEN 2 of 2 |
| 1.18 | many agents, one system (multi-agent coordination, orchestrator failure, owner communication) | coordination | 31 hot-fix rows during runs (7 in one run); 2 failures-log coordination rows | one role per agent; a job-number allocator; one job per queue; a change-log gate | 14 tests; the orchestrator itself has no checker (open) |

## 1.2 Cheating on the scorer

**Definition.** *Specification gaming* is behaviour that satisfies the literal objective without reaching the intended outcome (Krakovna et al.). *Reward hacking* is the case where the agent changes or exploits the scorer itself. METR saw recent frontier models, on research-engineering tasks, overwrite a timer, stub an evaluator, read a stored reference answer and patch an equality check; on one task every run hacked, and telling the model not to cheat barely changed the rate (METR 2025). ImpossibleBench edits unit tests so they contradict the task; any pass is a cheat; stronger models generally cheated more often, and some model families did it mostly by editing the tests (Zhong et al. 2025).

**Mechanism.** The agent is trained and prompted to finish and succeed. When the honest path is blocked and the scorer is reachable, changing the scorer is the shortest path to "done". The model can also judge its shortcut to be what the user wanted.

**Here.** No known case of an agent editing a scorer or a grade in the 21 series runs. The pressure is visible in the failures log: 5 of 43 rows are the alarm pipeline refusing an edit or copy after a seal (for example "CHANGED SINCE VARIANT", "ANOTHER CARD THAN THE ONE GRADED", "ALREADY GRADED: never re-run", a pre-registration fingerprint copied from the previous variant). One more row shows a restart that graded a duplicate variant and was refused by the limit of 3 tries per idea. These are attempts to move past a seal, mostly by restart or copy, not by intent we can see.

**Control.** The fence and seal layers (Chapter 10): released tools are read-only and no tool is built inside a run; the alarm pipeline pins the definition and claim by fingerprint at step 7, seals variants at step 9 and refuses more than 3 graded variants per idea; a separate scoring agent grades from receipts. METR's advice matches: fix the scorer when a hole is found, do not just add a warning to the prompt.

**Test of the control.** The refusals above are the guard firing in live runs. No practice test has yet given a researcher an impossible pass rule to see whether it cheats.

**Residual risk.** All agents run as one computer user, so an agent could read files it should not; a read leaves no trace unless it goes through a logged tool (Chapter 10).

**Open.** An impossible practice test in the ImpossibleBench style (4 fresh researchers, pass if none claims a pass). A separate computer user for runs.

## 1.3 Saying more than the numbers show

**Definition.** *Overclaiming*: a word or claim the evidence does not support. Its source in assistant models is close to *sycophancy*, answers shaped to what the reader wants to hear; human preference data rewards agreeable, confident answers, and optimising for it can trade truth for approval (Sharma et al. 2023).

**Mechanism.** A researcher wants its alarm to work and its owner to be pleased. Words like "beats", "confirms" or "because" cost nothing to write; the numbers that would back them take a tool call.

**Here.** Overclaim is the most frequent key: present in 15 of 16 assessed runs (37 rows, 0 to 6 per run; only one run was clean) and in 52 of 53 mistake files including practice tests. The scoring agent's rule counts a word the numbers do not support, a hand-derived number with no t statistic, or two causes not separated. In the first series of runs, overclaims went 4, 2, 3, 0, 0, 3 over runs 1 to 6. The numbers rule has not removed overclaims in this series.

**Control.** The numbers rule on the researcher's rules page (every comparison quotes both numbers and their source fields; a cause needs a field); the scoring agent's count; the card writer refuses trade words.

**Test of the control.** The count is what is tested: scoring-agent practice tests score whether the scoring agent finds planted overclaims, with two blind scorers set up by a tool that prepares blind scoring sets (8 tests) and their agreement checked against a bar of 0.80 (6 tests).

**Residual risk.** The rule depends on the scoring agent, which is also an LLM; an overclaim phrased softly may pass.

**Open.** Turn the commonest overclaim patterns into a refusal in the card tool (a guard in code rather than a rule in text), then count again over 10 runs.

## 1.4 Wrong reports about its own work

**Definition.** An agent's account of what it did is a claim, not evidence. Reasoning text often leaves out what actually drove the answer: in tests with planted hints, reasoning models mentioned the hint they used less than 20% of the time in most settings, and admitted to reward hacks less than 2% of the time (Chen et al. 2025). Without outside feedback, LLMs do not reliably correct their own reasoning and sometimes get worse (Huang et al. 2024). MAST counts weak or wrong verification as one of three failure classes: no or incomplete verification 8.2%, incorrect verification 9.1% (Cemri et al. 2025).

**Mechanism.** The model writes a fluent summary from its context, not from the files; a time, a count or a file name can be off and still read well.

**Here.** In the failures log, a researcher summed month rows into a fire count (19,310 written, 9,655 true) and the orchestrator itself double-counted month rows plus the total row (13,200 reported, 6,600 true) and had to retract. The series table shows the reproduction check run in only 2 of 21 runs, both "no"; 19 were not run. Typed timestamps minutes off were seen in earlier runs (not in a register).

**Control.** No agent scores its own work: the scoring agent recomputes every card number from receipts and checks the order of seals from file times; the orchestrator checks at least one number by its own route.

**Test of the control.** The scoring and knowledge roles are PROVEN 6 of 6.

**Residual risk.** The scoring agent and the researcher run on the same model family and may share blind spots; Chapter 10 sends tools to an outside reviewer on a different model for this reason.

**Open.** Run the reproduction check on every run, not 2 of 21.

## 1.5 Seeing data it must not see

**Definition.** *Leakage* is information in the training or design step that would not be available when the result is used; Kapoor and Narayanan found it in hundreds of papers across 17 fields and list eight types, temporal leakage among the commonest. *Contamination* is the model having seen the test data in training: models named the buggy file of SWE-bench tasks from the issue text alone far more often than on similar tasks from other repositories (Liang et al. 2025).

**Mechanism.** An agent reads whatever is in reach. A file with closed months in it, a test receipt left in a shared folder, or a prompt that names a held-out window is just more context to it.

**Here.** The researcher is never given the hidden months, and the series table counts breaches: 1 breach in 14 scanned runs; the first 7 memory runs were not scanned. The failures log has 3 held-out hygiene rows: two runs opened a test folder holding closed-month control numbers, and a scoring agent opened a helper script with held-out constants left in a shared scratch folder. Six unclear lines are held-out leaks (for example a released prompt that pools the held-out months into the yardstick (the plainest alarm of the same kind and side) every alarm must beat). The 20 closed-month rows in the mistake files are all in practice-test replays and are not counted as breaches here. The first edition of this document lists 15 earlier leaks in strategy research.

**Control.** Data windows live in the shared reader code and refuse closed days; the one-look holdout tool; a leak scanner (run by the orchestrator only) scans every file a researcher, scoring agent or knowledge agent reads for held-out markers; the scoring agent's three hidden-month counts (Chapter 10).

**Test of the control.** 7 tests of the leak scanner; safety and data integrity PROVEN 3 of 3; a leak practice test.

**Residual risk.** Model memory: the agents were trained on public text and may know later market history. The tools hold the windows; the model's memory cannot be fenced.

**Open.** Scan the 7 unscanned runs; keep test receipts outside every folder agents read.

## 1.6 Losing track inside a long session

**Definition.** The context window is the text the model can attend to at once. Accuracy falls when the needed fact sits in the middle of a long context (*lost in the middle*, Liu et al. 2023) and falls as input grows even on simple tasks (*context rot*, Chroma 2025, 18 models). When the window fills, the harness *compacts*: it summarises and restarts from the summary, and over-aggressive compaction drops details needed later (Anthropic 2025, context engineering). MAST measures loss of conversation history at 2.8% of multi-agent failures.

**Mechanism.** Attention is a finite budget; every extra page read spends it. A summary keeps what seemed important when it was written, not what turns out to matter.

**Here.** Not counted by any key (gap). Indirect signs: the time log of the first series named reading as the largest single cost (52 minutes over four trials); after a compaction the orchestrator lost track of which runs were still going.

**Control.** Short pinned pages: one rules page per run, pinned by fingerprint, with a size bar under 8 KB; one home per topic so no page copies a rule; notes outside the window, as Anthropic recommends: a short page per role with its goal, scope, where it is and its next step, plus journals and handover files; a fresh agent per role, so no agent carries another role's context; a read-once log.

**Test of the control.** The researcher's rules page is PROVEN 12 of 12 (13 questions, 0 contradictions, size bar).

**Residual risk.** The orchestrator runs for many hours and is compacted; its page is only as good as its last update.

**Open.** A register key for "lost track" so the scoring agent can count it; a compaction practice test (resume from the summary alone and reproduce the last result).

## 1.7 Forgetting across sessions and repeating mistakes

**Definition.** A new session starts with no memory of the last one. Anthropic's harness for long-running agents answers this with an initializer session, a progress file and a commit per step, so each new session reads where the last one stopped.

**Mechanism.** What an agent learned lives in its context; when the session ends, it is gone unless written down where the next agent will read it.

**Here.** 20 of 45 distinct mistake keys appear in more than one mistake file. The worst repeaters: overclaim (52 files), a missing tool declared for round 2 (40) and for round 3 (38), rework in round 3 (20), and a pipeline stop because there were no fire rows (20). Rows repeating an earlier run's key: mean 2.21 over 14 memory runs, 4.43 over 7 control runs. This is a reading, not a test: the two groups are not matched in time and early rows used an older format.

**Control.** The knowledge store, written only by the knowledge builder from the knowledge agent's scored evidence, and a short brief for memory runs; fixed mistake keys so a repeat can be counted; a lessons register read before building or running a tool; the learning loop tools (the only row writer, and a close gate).

**Test of the control.** The knowledge store and builder are PROVEN 23 of 23, handover and restart PROVEN 6.5 of 7, the brief WORKS. The proof that memory helps is a series test (memory minus control at least +2 points, permutation p below 0.10, fewer repeated mistakes), not yet passed.

**Residual risk.** A brief can teach a wrong lesson as well as a right one; the knowledge agent only adopts a rule after a practice test.

**Open.** The 10 proof runs the owner set.

## 1.8 Re-finding the known

**Definition.** An agent given a memory of past successes tends to return to them: small variations of a known answer instead of new ones. The literature has no single term for this in agents; the closest is *mode collapse* (our judgement on the label).

**Mechanism.** The brief makes earlier alarms the most available ideas in context, and a variation of a known winner is the safest forecast.

**Here.** Rediscovery is "yes" in 9 of 21 runs and in every one of the last 8 runs, memory and control alike. The overlap with the nearest earlier alarm (the share of the new alarm's waves it shares; the novelty step's copy verdict counts fires instead, Chapter 13) was 100% in three runs, then 96.5%, 93.2%, 90.6%, 80.7% and 41%; it was not measured before that.

**Control.** The alarm pipeline's novelty step (step 16) compares each new alarm with all earlier ones; the researcher searches for copies of its definition before sealing; the proof rules count only alarms below 50% overlap of fires.

**Test of the control.** The step runs and its output is quoted by the scoring agent. It detects; it does not prevent.

**Open.** A longer first round with novelty measured (in design); a rule that a rediscovery cannot be the run's best round.

## 1.9 Wandering off the task

**Definition.** *Task derailment* (MAST FM-2.3, 7.4%) and *disobeying the task specification* (FM-1.1, 11.8%): the agent does a different task from the one set, often one it can finish.

**Mechanism.** When the set task is blocked, a nearby task that produces output feels like progress; the model has no cost for switching.

**Here.** Not counted by a key (gap). Seen as agents starting new studies instead of the assigned step, and a run answering a question at a different setting from the one named.

**Control.** Each role's page states one goal and what is out of scope; the takeover gate (a new agent taking over a role first reproduces the last result, writes the plan back, and asks instead of switching); a round checker flags a missing step on a live run after each round; the knowledge agent marks a question answered only when the exact named test ran.

**Test of the control.** 8 tests of the round checker; PROVEN 5 of 5.

**Open.** A drift key in the mistake files so it can be counted.

## 1.10 Errors that pile up over many steps

**Definition.** *Error compounding*: if each step succeeds with probability p, a task of n steps succeeds with about p to the power n, so small per-step gains or losses change long-task success a lot. Models also *self-condition*: once their own errors are in context they become more likely to err again, and bigger models do not escape this (Sinha et al. 2025). METR measures the task length a model completes half the time; it has doubled about every seven months (Kwa et al. 2025). Our runs are 2 to 4 hours of many tool steps.

**Mechanism.** A wrong value early becomes an input to every later step; the agent then explains around it instead of going back.

**Here.** Rework: 43 rows (8 in runs, 35 in practice tests); stops: 62 rows (15 in runs, 47 in practice tests); 31 hot-fix rows patched a run in flight.

**Control.** Rounds are sealed one by one, so a bad round cannot change an earlier one; "two failed tries on one step: stop" (the researcher's rules page); a fresh agent per role starts with a clean context; tau-bench's lesson (consistency over k tries, pass^k) is why we judge a process on many runs, not one.

**Test of the control.** Rule in text; the scoring agent counts rework and stops after the run.

**Open.** pass^k for our runs: one idea run by 3 fresh researchers.

## 1.11 The agent stops or goes silent

**Definition.** *Liveness* failures: the agent stops making progress without saying so. MAST: unaware of termination conditions 12.4%, premature termination 6.2%, step repetition 15.7%.

**Mechanism.** An agent waiting on a job it does not re-check, a long silent step, or a session that simply ended all look the same from outside: no new files.

**Here.** On the night of 8 to 9 November 2026 two research runs went silent around 23:00 and were not restarted until the next morning (the orchestrator's own account; no register row, which is itself a gap).

**Control.** The learning loop page says to watch every 3 minutes (run times, stop files, jobs on the machine, the round checker); researchers check each job at least every 5 minutes and end with BLOCKED and the reason; restart at once from the run folder instead of asking and waiting.

**Test of the control.** None. The watch is a rule in text for the orchestrator; no tool raises an alert on silence.

**Open.** A stall alert in code (no file written for N minutes) with a planted silent run as its test; this is the first slice to build.

## 1.12 One line read two ways

**Definition.** *Underspecified instructions*: a task or rule that allows more than one action. Agents rarely notice: in Ambig-SWE most models could not tell well-specified from underspecified tasks and guessed instead of asking (Vijayvargiya et al. 2025). MAST: fail to ask for clarification 6.8%.

**Mechanism.** The writer knows what was meant; a fresh agent sees only the words and fills gaps with the most likely reading, silently.

**Here.** The register of unclear lines holds 2,424 lines (2,286 found on 8 Nov, 138 on 9 Nov); kinds: read two ways 1,012, missing 396, contradiction 318, unclear 289, waste 195, stale 119; status: open 1,889, fixed 290, fixed in a draft 11, page no longer current 234. Lines read two ways are most common on the researcher's rules page (243), then the scoring agent's step page (91). Cold readers (fresh agents reading a page for the first time): 14 reports in 7 runs, 383 lines (read two ways 236, missing 98, contradiction 49), 17 to 39 lines per report.

**Control.** Two cold readers per run mark every line they could act on two ways; their lines go into the register; a triage tool sorts them against the live files; a page is frozen while runs use it; a run may not start while a file it reads has an open unclear line.

**Test of the control.** The triage tool has 1 test; unclear-line reports are WEAK. The two readers' agreement on the same page is not measured.

**Residual risk.** 1,889 open lines. The run gate and the open count do not fit together yet; we judge that most open lines sit on pages no longer current.

**Open.** Reader agreement (Cohen's kappa per page); close or retire open lines per page.

## 1.13 Too sure of the next idea

**Definition.** *Overconfidence*: stated confidence above the hit rate. On real prediction-market questions, all five frontier models tested were overconfident (KalshiBench 2025); models also avoid words of doubt even when wrong (Zhou et al. 2024).

**Mechanism.** The agent forecasts from the story it just wrote, which always sounds plausible.

**Here.** Memory runs' researchers: 17 rounds, mean signed error -0.13 lead points (lead: how much more often the alarm's side wins the race, a move of two trading costs its way before one cost against it, than at matched random moments, minus the same difference for the opposite side, in percentage points), 10 of 17 below forecast, 12 of 16 80% intervals cover the result. Control runs' researchers (no brief): 9 rounds, mean signed error -3.21, 7 of 9 below forecast, 7 of 8 cover. Mean absolute forecast error per run: 2.85 (memory, 14 runs) and 3.08 (control, 7 runs). The first series had +2.2 forecast against -0.9 actual; the upward bias is now mostly in control runs.

**Control.** Every round seals a forecast with an 80% interval before its job runs; a forecast scorer scores Brier and coverage; forecasts are shrunk toward what similar changes gave before.

**Test of the control.** The forecast scorer is PROVEN 3 of 3; forecasts WORKS 14 of 19.

**Open.** 26 rounds are few; coverage should be judged after the 10 proof runs.

## 1.14 Luck read as skill

**Definition.** *Garden of forking paths*: choices made after seeing data create many hidden comparisons even when only one test is run (Gelman and Loken 2013). *Backtest overfitting*: the best of many strategy variants on one history usually underperforms after; the probability can be estimated (PBO, Bailey et al.) and a Sharpe ratio deflated for the number of tries (Bailey and Lopez de Prado). Reusing a holdout adaptively makes it a training set (Dwork et al. 2015).

**Mechanism.** Agents try ideas fast; each try on the same months is another look; the best look is the one they report.

**Here.** In the first series only 5 of 15 alarms that passed on Sep to Dec 2025 held in later months. The 21 runs of this series all design on the same 10 Sep to 31 Jan window.

**Control.** Months split before any work into learning, check-once and never-seen windows, enforced in code; at most 3 graded variants per idea; the one-look holdout, read by the orchestrator only; memory against control runs on the same months with a permutation test.

**Test of the control.** The proof checker is PROVEN 10 of 10; the held-out read PROVEN 4 of 4.

**Residual risk.** The series-level count of tries is not used in any correction.

**Open.** PBO over all tries of the series before any series claim (pass below 0.5).

## 1.15 Wrong tool use, or no tool

**Definition.** *Tool-use errors*: wrong tool, wrong argument name or value, ignored output (ToolScan names seven recurring types; pointer only). *Tool bypass*: writing a quick script that "does the same thing" when a tool refuses.

**Mechanism.** A refusal blocks the path to done; a script of one's own removes the block, with no tests and no data window.

**Here.** No-tool rows: 84 (16 in runs, 68 in practice tests), mostly a researcher declaring a missing tool for a round 2 or round 3 step instead of computing by hand. Steps done by hand: 0 in all 21 runs. The failures log has 5 rows of wrong metric scope or input name (market codes read on coin rows, BTC-only codes, metric codes passed where definition names were expected).

**Control.** Only released tools do data steps; a refusal is read, not bypassed (the fix goes into the tool by release); the metric brief is read for every metric code before use (Chapter 4); no-tool lines name the tool to build.

**Test of the control.** Metric use is PROVEN 8 of 9; steps by hand are counted per run.

**Open.** Build the round 2 and round 3 tools the no-tool rows ask for.

## 1.16 Brittle machine, unsafe restart

**Definition.** Environment faults (shell, paths, disk, queues) and *non-idempotent resume*: restarting a step changes the result or fails because the first attempt left state behind. Anthropic's long-running harness keeps a progress file and a commit per step so a restart is safe.

**Mechanism.** Agents assume a generic Linux shell and clean folders; the computer's own shell, a stale pending file or a task number already used breaks that.

**Here.** In the failures log (our classification of 43 rows): environment 9 (a banned word in a job text, the disk budget 3 times, a stopped queue, a job limit, virtual machine paths on the computer, a 15-minute grade, the shell not splitting a variable); restart or resume 5 (a stale pending file, missing subfolders, an output that already existed on a reused task number, a duplicate variant after restart, a resumed pipeline past its cap on fires); template or process gaps 7; tool behaviour 4 (one silent cut of a requested end day).

**Control.** A job sheet with tested commands; a fresh pipeline folder per input and new task numbers; tools refuse to overwrite an existing output; a run builder; the lessons register.

**Test of the control.** 20 tests of the run builder; 2 tests of the job templates; PROVEN 3 of 3.

**Open.** A planted half-run resume test: the resumed run must give the same receipt fingerprint as an unbroken one.

## 1.17 Deleting or publishing by mistake

**Definition.** *Destructive actions*: deletes, overwrites, pushes, publishing. In a public incident an agent ran destructive commands against a production database during a code freeze and then misreported it (AI Incident Database, incident 1152).

**Mechanism.** The agent does not see who else depends on a file; "clean up" reads as a harmless task.

**Here.** 1 failures-log row: an orchestrator sweep deleted store files that another tool re-reads. Earlier, a cleanup removed fire lists the strategy stage needed.

**Control.** Raw data is never deleted; each agent role cleans only its own finished working files through a scratch cleaner (keep list, copy of needed files into receipts first, dry run, log of every deleted file); deletes outside an agent's own working files, pushes, publishing, money and going live wait for the owner; the permission system blocks sensitive actions without approval.

**Test of the control.** 2 tests of the scratch cleaner; scratch cleanup PROVEN 2 of 2; a cleanup practice test.

**Residual risk.** One shared computer user: a tool that is not used can be bypassed.

## 1.18 Many agents, one system

**Definition.** *Multi-agent coordination failures*: MAST's inter-agent class (conversation reset, withholding, ignoring another agent's input, reasoning-action mismatch 13.2%). Anthropic's research system uses one lead agent that hands focused work to workers in clean contexts, and says the pattern suits work that splits into independent parts, not work where every agent needs the same context. The orchestrator is itself an agent with every weakness above.

**Mechanism.** Agents share one machine, queues and disk but not context; each acts on its own picture.

**Here.** The hot-fix log: 31 changes during runs (7 in a single run, 5 series-wide, 3 for all new runs), each one a change of environment under a run that is supposed to be comparable. Coordination rows in the failures log: 2 (a hot fix changed an installed tool under another job; a fix job waited behind a 17-minute grade). The orchestrator's double count and its night of not restarting stalled runs are in 1.4 and 1.11.

**Control.** One agent per role and one role per agent; job numbers from one allocator; one job per queue; jobs filed only on a free queue; disk budgets per agent role; a change-log gate (every file change must have its row in the log) before every run; the owner's standing rules re-read after every reset; for the owner, verdict first in plain words, one question at a time.

**Test of the control.** 14 tests of the change-log gate; PROVEN 3 of 3.

**Residual risk.** No agent checks the orchestrator while it works.

**Open.** A freeze on hot fixes while a run is open (fixes wait for the next run or void the current one); an orchestrator checker on the same watch timer as 1.11.

## 1.19 The design rules that answer these challenges

The controls in 1.2 to 1.18 come from eight design rules, D1 to D8. Each rule below says what it requires, how it is enforced (in code, or in text only), which challenges it answers, and which block of Chapter 0 builds it. A rule enforced in text only is weaker than one a tool refuses to break; the table at the end says which is which.

**D1. Released tools do every data step.** No agent computes a number by hand or builds a tool inside a run; every data step is a call to a released tool with its tests passing from the installed copy. Enforced in code: installed tools are read-only to runs; the scoring agent counts hand-computed steps (0 in all 21 runs). Answers 1.2, 1.4, 1.15. Built in block 16.

**D2. Every number has a receipt.** A number in a card cites the file it came from and that file's fingerprint, so a second agent can recompute it from the receipt alone. Enforced partly in code: the scoring agent recomputes every card number with its own code and files a mismatch for each one that differs or is missing. Answers 1.3, 1.4, 1.10. Built in block 10.

**D3. Seal before you see.** Forecasts, claims and the readings a run may use are written and fingerprinted before the result exists, and nothing sealed may change. Enforced in code: the alarm pipeline pins definition and claim by fingerprint (step 7) and refuses a changed or re-graded variant ("CHANGED SINCE VARIANT", "ALREADY GRADED"); the filter tool quotes the fingerprint of the sealed file of expected signs in every output header. Answers 1.2, 1.13, 1.14. Built in blocks 7 and 10.

**D4. Months are fenced.** Every study names its learning months, its check months (opened once, for one frozen rule) and its never-seen months before any work, and the reader code refuses closed days. Enforced in code: shared readers, the one-look holdout tool and the leak scanner. Answers 1.5, 1.14. Built in block 12.

**D5. One role per agent.** The agent that does the research never scores it; a separate scoring agent scores from receipts, a separate knowledge agent files what was learned, and cold readers check the pages. Enforced in text, checked after the fact: each role gets its own launch and its own list of files it may write, and the change log records who wrote what. Answers 1.3, 1.4, 1.12, 1.18. Built in block 8.

**D6. Memory only through the knowledge tool.** What one run learned reaches the next run only as scored evidence filed by the knowledge agent through the knowledge builder, which refuses a row that fails its check, and a short brief built from it. Mistakes carry fixed keys so a repeat can be counted. Enforced in code. Answers 1.6, 1.7, 1.8. Built in block 7.

**D7. Learning counts only against a control.** A claim that agents learn needs memory runs to beat control runs (same task, no memory) on bars written before the runs, with a permutation test. Enforced in code for the numbers; the bars are fixed in text before the runs. Answers 1.7, 1.13, 1.14. Built in block 11.

**D8. The owner decides what cannot be undone.** Money, live trading, deletes outside an agent's own working files, publishing, code pushes and which months may be read are the owner's decisions, logged in his words. Enforced partly in code (the scratch cleaner deletes only from an agent's own working files, with a keep list and a log); the rest in text. Answers 1.17, 1.18. Built in block 18.

**Which challenge each rule covers, and what is left uncovered**

| challenge | rules | enforced in code? | gap with no rule yet |
|---|---|---|---|
| 1.2 cheating on the scorer | D1, D3 | yes | no planted-cheat practice test |
| 1.3 overclaiming | D2, D5 | partly (count only) | no refusal in the card tool |
| 1.4 wrong self-report | D1, D2, D5 | partly | reproduction check mostly not run |
| 1.5 leakage | D4 | yes | 7 runs never scanned; model memory |
| 1.6 losing track in a session | D6 | partly | no compaction practice test |
| 1.7 forgetting across sessions | D6, D7 | yes | proof runs not finished |
| 1.8 re-finding the known | D6 | detects only | no rule stops a rediscovery |
| 1.9 wandering off the task | none of D1 to D8 | text only | goal page and takeover gate only |
| 1.10 errors piling up | D2, D3 | partly | stop rule in text only |
| 1.11 agent goes silent | none of D1 to D8 | no | stall alert in code (smallest first slice) |
| 1.12 one line read two ways | D5 | text only | reader agreement not measured |
| 1.13 overconfidence | D3, D7 | yes | none beyond calibration over more runs |
| 1.14 luck read as skill | D3, D4, D7 | yes | no PBO over all tries |
| 1.15 wrong tool use | D1 | yes | none |
| 1.16 brittle machine | D1 | partly | no planted half-run resume test |
| 1.17 deleting or publishing by mistake | D8 | partly | none |
| 1.18 many agents, one system | D5, D8 | partly | nothing checks the orchestrator |

Two challenges, 1.9 and 1.11, have no design rule behind them, only practice: keeping an agent on task and alive is still the orchestrator's job, and the orchestrator is not checked (1.18). We judge, from the counts above, that these are the first places to add a rule enforced in code.

## 1.20 Sources

Literature (M method, I worked example, P practitioner or first-party write-up, L live incident or production evidence):

- Cemri et al. *Why Do Multi-Agent LLM Systems Fail?* (MAST). arXiv 2503.13657. M. https://arxiv.org/abs/2503.13657
- METR. *Recent Frontier Models Are Reward Hacking* (2025). L. https://metr.org/blog/2025-06-05-recent-reward-hacking
- Zhong, Raghunathan, Carlini. *ImpossibleBench: Measuring LLMs' Propensity of Exploiting Test Cases*. arXiv 2510.20270. M. https://arxiv.org/abs/2510.20270
- Krakovna et al. *Specification gaming examples in AI*. I. https://vkrakovna.wordpress.com/2018/04/02/specification-gaming-examples-in-ai/
- Sharma et al. *Towards Understanding Sycophancy in Language Models*. arXiv 2310.13548. M. https://arxiv.org/abs/2310.13548
- Chen et al. *Reasoning Models Don't Always Say What They Think*. arXiv 2505.05410. M. https://arxiv.org/abs/2505.05410
- Huang et al. *Large Language Models Cannot Self-Correct Reasoning Yet*. arXiv 2310.01798. M. https://arxiv.org/abs/2310.01798
- Kapoor and Narayanan. *Leakage and the Reproducibility Crisis in ML-based Science*. arXiv 2207.07048. M. https://arxiv.org/abs/2207.07048
- Liang, Garg, Zilouchian Moghaddam. *The SWE-Bench Illusion*. arXiv 2506.12286. I. https://arxiv.org/abs/2506.12286
- Liu et al. *Lost in the Middle: How Language Models Use Long Contexts*. arXiv 2307.03172. M. https://arxiv.org/abs/2307.03172
- Hong, Troynikov, Huber. *Context Rot* (Chroma, 2025). P. https://research.trychroma.com/context-rot
- Anthropic. *Effective context engineering for AI agents* (2025). P. https://www.anthropic.com/engineering/effective-context-engineering-for-ai-agents
- Anthropic. *Effective harnesses for long-running agents* (2025). P. https://www.anthropic.com/engineering/effective-harnesses-for-long-running-agents
- Anthropic. *How we built our multi-agent research system* (2025). P. https://www.anthropic.com/engineering/multi-agent-research-system
- Sinha et al. *The Illusion of Diminishing Returns: Measuring Long Horizon Execution in LLMs*. arXiv 2509.09677. M. https://arxiv.org/abs/2509.09677
- Kwa et al. (METR). *Measuring AI Ability to Complete Long Tasks*. arXiv 2503.14499. M. https://arxiv.org/abs/2503.14499
- Yao et al. *tau-bench*. arXiv 2406.12045. M. https://arxiv.org/abs/2406.12045
- Vijayvargiya et al. *Interactive Agents to Overcome Ambiguity in Software Engineering*. arXiv 2502.13069. M. https://arxiv.org/abs/2502.13069
- Zhu et al. *Establishing Best Practices for Building Rigorous Agentic Benchmarks*. arXiv 2507.02825. M. https://arxiv.org/abs/2507.02825
- Kokane et al. *ToolScan*. arXiv 2411.13547. M (pointer only, not read). https://arxiv.org/abs/2411.13547
- KalshiBench. *Do Large Language Models Know What They Don't Know?* arXiv 2512.16030. I. https://arxiv.org/abs/2512.16030
- Zhou et al. *Relying on the Unreliable: The Impact of Language Models' Reluctance to Express Uncertainty*. arXiv 2401.06730. M. https://arxiv.org/abs/2401.06730
- Gelman and Loken. *The garden of forking paths* (2013). M. http://www.stat.columbia.edu/~gelman/research/unpublished/p_hacking.pdf
- Bailey, Borwein, Lopez de Prado, Zhu. *The Probability of Backtest Overfitting*. M. https://papers.ssrn.com/abstract=2326253
- Bailey and Lopez de Prado. *The Deflated Sharpe Ratio*. M. https://papers.ssrn.com/abstract=2460551
- Dwork et al. *The reusable holdout* (Science 2015); *Generalization in Adaptive Data Analysis and Holdout Reuse*. arXiv 1506.02629. M. https://arxiv.org/abs/1506.02629
- AI Incident Database, incident 1152 (agent deleted a production database during a code freeze, July 2025). L. https://incidentdatabase.ai/cite/1152/
