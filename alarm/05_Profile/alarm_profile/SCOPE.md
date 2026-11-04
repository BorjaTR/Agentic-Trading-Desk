Written by SCOUT for the repo on 30 Oct 2026 from tree/tools/alarm_profile/README.md, alarm_profile.py, episode_blocks.py and the
RELEASE_profile_V1*.json files; not the owner's document (owner seat: QUANT).

# SCOPE: alarm_profile (edition 1, release V1_8)

**Purpose and user.** For each liquidation alarm (subjects A02, A02_1, A02N), describe the episode at the alarm so one liquidation can
be compared with others, with every value proven to mean what it says (the owner, 22 Oct 2026, 13:03, 13:08, 13:13 Berlin). Users:
QUANT and the alarm teams; the first look reads the move spent (part 06); the outcome tool and the grade chain pin this release.

**In scope.**
- Where the move really started, how far and how fast it went before and during the liquidations, the liquidations' size against
  the coin's own normal, their shape over time, the other side's liquidations, open interest and Hyperliquid in the same burst.
- 36 values in 8 blocks (`EPI_CATALOG_V1.tsv`), named profiles over them (`PROFILES_V1.tsv`), proof cards for every value.
- Everything cut at the alarm (`known_at` = the alarm); the days the lab law seals are never read.

**Out of scope.**
- Anything after the alarm and any outcome (heat, offer, money): those stay in their own tools and are joined when reading.
- The context around the alarm (market, coin, book): `alarm_context` (its own folder here).
- Alarms other than the three liquidation subjects: the generic editions 2+ (in development, not here).

**Success.** Every value of every alarm is either a number that its proof card shows means what it says, or NOT_KNOWN with a reason;
the same inputs and settings give the same sha16s; a planted value after the alarm changes nothing (tested).
