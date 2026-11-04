# Addendum 1 to DECIDE_LOOP_PREREG_V1_1.md: the ledger status bar, raised for 22 tries (DECIDE seat, written 2026-10-26T07:06:24Z, before any outcome of loop_v1_1_run is read)

**Why.** The ledger status rule in summarize_decide_loop_v1.py (PASS when S1 passes in at least one of the 22 choosable cells) is best of 22. One passing cell out of 22 tries can come from how the cells happen to fall, not from the mechanism. The tries ledger counts all 22 cells as tries of one setting choice, so the bar must rise with them.

**No count against chance.** Project rule (the owner): no luck tests, and the numbers must be due to what we think. So the bar is raised through the mechanism, not through a chance count.

**The raised bar.** The skip line removes the same 750 TIGHTER fires in every cell. If it works for the reason in P2 (a tight book means real two-sided interest, so the push is information and a fade is on the wrong side), that gap must show whatever the entry and the exit are. It cannot be a property of one entry and exit pair. The same holds for VALUED (P1: the overshoot comes back).

**Ledger status of each ask (summarize_decide_loop_v1_1.py; v1 is kept unused):**
- **TAKE and SKIPRULE:**
  - PASS when S1 passes in at least 11 of the 22 choosable cells, in at least 2 of the 3 entries, and in at least one 1 h and one 4 h exit.
  - Otherwise UNSURE ("best of 22") when S1 passes in 1 to 10 cells, or when it misses one of those spreads.
  - FAIL when it passes in none.
- **VALUED:** the same bar on "taking every valued fire pays".
- **BADDATA:** UNSURE always.

**The reader's choice is unchanged.** decide_loop_read_v1.py still names the passing cell with the highest TAKE edge lower bound. That cell becomes the rulebook's entry and exit only when the status is PASS. On UNSURE, S1 stays CANDIDATE with entry and exit UNSET, and the Jan-Feb look is not spent.

The summary prints, for each group, the passing cells by entry and by exit, so the spread is visible.
