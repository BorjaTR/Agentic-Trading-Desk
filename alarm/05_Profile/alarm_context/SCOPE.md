Written by SCOUT for the repo on 30 Oct 2026 from tree/tools/alarm_context/README.md, alarm_context.py, context_blocks.py and the
RELEASE_context_V1*.json files; not the owner's document (owner seat: QUANT, per its README; the release files name LEAD / LAYERS).

# SCOPE: alarm_context (edition 1, release V1_7)

**Purpose and user.** What was happening around each alarm at the moment we would decide, so alarms can be grouped and compared by
their context. Users: QUANT, the alarm teams, STRATEGY; alarm_profile edition 1 joins it (CTX_INPUTS_V1.tsv).

**In scope.** Three levels chosen by a setting: EVENT (the alarm itself: burst, history, move, structure, walls), MARKET (BTC first,
basket, breadth, liquidation wave, spread and depth, hour), COIN (move, range, volatility, funding / OI / basis, cost, regime, class):
129 values in `CTX_CATALOG_V1.tsv`, every directional value signed in the alarm's push direction; one row per alarm and decision time.

**Out of scope.** Any outcome (heat, offer, money); the episode itself (alarm_profile); paths around the event (a separate tool);
listing age (no listing dates).

**Success.** Every value is known at the decision time (a planted 1e12 after it changes nothing), mirrored correctly for the other
side, proven by its own output proof (CTX_OUTPUT_PROOFS_V1.tsv), and the same inputs give the same sha16s.
