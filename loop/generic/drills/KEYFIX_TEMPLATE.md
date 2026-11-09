Key fix (paper research). You repair one drill kit before any agent takes it. S = {SEAT_ROOT}. Kit: S/{KIT}/ (DESIGN.md, TASK.md, its material, key/KEY.md, GOLD/good.md, GOLD/bad.md, GOLD/KNOWN.md). A fresh key checker wrote S/{KIT}/KEYCHECK.md: read it first, then the kit and the live documents the task names.
Fix every item the checker flagged (must and should), and every task line it flagged:
- one meaning per key line: an answer that is right by the named documents earns the point; write the accepted forms in the line;
- no leak: a task or material line that gives an answer away is reworded, keeping the trap it carries;
- a key item no named document teaches: either point it at a document that does teach it, or mark it "not counted in the pass rule" and say why;
- the pass rule in DESIGN.md is changed only when the item count changes (same percentage).
Rules:
- Never edit key/KEY.md: write key/KEY_V2.md (the full key) and put its sha16 (first 16 hex of sha256) in DESIGN.md under a "KEY_V2" line listing what changed.
- Change GOLD/good.md and GOLD/bad.md only if needed so good still earns the full total and bad keeps a clear low total; rewrite GOLD/KNOWN.md item by item for KEY_V2.
- Never read any file whose name contains HELDOUT, T8_ or FEBMAR; never write a Feb-Jul 2026 number; run no job; change nothing outside the kit folder; no em dashes.
- End DESIGN.md with your REPORT block per {GENERIC}/REPORT_TEMPLATE_V1.md.
Max 25 tool calls. Reply with: KEY_V2 sha16, the new good and bad totals, the item count, and every file you changed.
