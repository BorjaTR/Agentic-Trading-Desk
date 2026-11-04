Written by SCOUT for the repo on 30 Oct 2026 from tree/tools/alarm_context/README.md, alarm_context.py and context_blocks.py; not
the owner's document.

# ARCHITECTURE: alarm_context (edition 1, release V1_7)

## Inputs
| input | format |
|---|---|
| the alarm list (EVENTS) | TSV: coin, t, side (+1 pushed up, shorts forced; -1 pushed down), S |
| lab days | the lab's one format, read only through `lab3.days` (purpose research): EVENT the day before up to the last decision day; MARKET and COIN the 31 days before |
| `../../QUANT/receipts/COSTS_PER_COIN_V4.tsv` | cost per coin (COIN level; as a decision feature NOT_KNOWN without a source vintage, rule A09-02; the retro values beside) |
| `COIN_TYPES_V1.tsv` | major / alt / meme, a hand list |
| setting `decisions` | minutes after the alarm (default 0) |

## Steps
1. For each alarm and decision time, read lab values at the last minute end at or before the decision time (channels and bands from
   the minute before; alarm history strictly before the alarm).
2. Each block (`@block(level, name)` in `context_blocks.py`, docstring lines `column: meaning [unit]`) computes its values.
3. Write each level as its own part with `lab3.write.write_part`: `CTX.A02.EVENT`, `CTX.A02.MARKET`, `CTX.A02.COIN` (ROWS; as_of =
   the alarm, known_at = the decision time); codes `CTX.A02.<column>` listed in `CTX_CATALOG_V1.tsv`.

## Outputs
The research store (settings key `RESEARCH_STORE`; built into `alarm_context.py:8,29` today).

## Files (tree/tools/alarm_context/)
`alarm_context.py` (build, show, read, catalog), `context_blocks.py` (the blocks), `CTX_CATALOG_V1.tsv`, `COIN_TYPES_V1.tsv`,
`CTX_OUTPUT_PROOFS_V1.tsv` (the proof cards), tests `test_alarm_context.py` (34), `test_ctx_output_proofs.py` (12),
`test_p09_v1.py` (2), and the releases `RELEASE_context_V1*.json`.

## Settings keys a real run needs
`LAB_DAYS`, `RESEARCH_STORE`, `PYTHON`. The store path is still built in (`MACHINE_PATHS.tsv` of the part).

## Tests
Planted values after the decision time change nothing; mirror tests for every directional column; one output proof per reading;
the part's RUN_PROOF.md shows them run from the repo and from a copy (lab3 from `Alarm/_vendor/LAB3_code` through `LAB3_CODE`).
