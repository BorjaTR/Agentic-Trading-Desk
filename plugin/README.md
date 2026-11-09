# crypto-alarm-desk plugin (V1 draft)

The Claude Code plugin of the Crypto Alarm Desk repo: the knowledge and commands an agent needs to design and test alarms with the
repo's fixed engine and to learn from every try. It ships no engine, no data and no alarm: install it beside the repo.

| part | what it does |
|---|---|
| `skills/alarm-desk` | what an alarm is, the loop from idea to an audited decision (desk.py commands), the honesty rules, mistakes already made |
| `skills/learning-loop` | the generic learning loop (loop/generic) with its alarm pack (loop/packs/alarm): brief, sealed forecasts, card, assessor, curator |
| `skills/desk-setup` | install check, trading style, data and register, fit, GO / GO WITH GAPS / STOP |
| `commands/new-alarm.md` | `/new-alarm <idea>`: one idea end to end, logged |
| `commands/desk-setup.md` | `/desk-setup [data folder]`: the setup above |
| `agents/alarm-reviewer.md` | the second reviewer: must-fix only, read-only, PASS / PASS WITH ITEMS / HOLD |

Install, from the repo root (the repo's `.claude-plugin/marketplace.json` lists this plugin):
```
/plugin marketplace add ./
/plugin install crypto-alarm-desk@crypto-alarm-desk
```
Then open Claude Code in the repo root and run `/desk-setup`, then `/new-alarm <idea>`.

Reviewer: the plugin's `alarm-reviewer` agent is the default second reviewer. A desk may use any other reviewer (an outside model, a
person) under the same rules: must-fix only, read-only, never the sealed key during a trial.

Status: V1 draft, not released. What is proven and what is not: CLAIMS.md at the repo root.
