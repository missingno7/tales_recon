# Amiga ranked-frontier audit

This is a read-only snapshot audit of `evidence/functions/ranking.json` (528 ranked entries), `evidence/functions/ledger.json`, and the grinder admission rules in `tools/grinder.py` / `tools/recovery_state.py`. It applies the normal 256-byte, HIGH-confidence, no-indirect-flow, at-most-one-unknown-call, zero-PC-relative-data, at-most-40-data-reference, no-unrecovered-local-dependency, and ready-local-unit gates. No canonical source or ledgers were edited.

Of 528 ranked functions, **18** are overlay entries with `CLOSED_CFG` extent and size at most 256 bytes. Four pass the structural admission fields; the current ranking snapshot labels those four `BLOCKED`, so none is presently a usable compile-loop entry. Since recovery-ledger repair is in progress, that status observation is informational; the structural counts below come from the ranked candidate fields.

| Admission gate hit within the 18-function cohort | Count | Overlap |
| --- | ---: | --- |
| Noncontiguous same-node unit | 14 | Dominant gate |
| Pending local dependency | 13 | 10 also fail unit closure; 3 more overlap with excess unknown calls, one of those also has PC-relative data |
| More than one unresolved call identity | 3 | All three also fail local dependency/unit closure, except one also fails PC-relative data |
| PC-relative data ownership | 2 | `ov03_F_0000` and `ov07_F_03CC`; both also fail unit closure |
| Indirect control flow, low confidence, or >40 data references | 0 | No hits in this cohort |

The exact overlap patterns are: 10 candidates fail only the local-dependency and unit-closure gates; two fail those plus the unknown-call limit; one fails those plus the unknown-call and PC-relative-data gates; one fails unit closure plus PC-relative-data ownership; and four pass all structural gates. The three over-limit unknown-call candidates are `ov03_F_0000`, `ov11_F_0B4C`, and `ov11_F_247C`. This makes local-call closure the narrowest practical focus: relaxing the unknown-call cap alone would not admit any of those three.

Across the 18 candidates, the most repeated unrecovered direct-callee IDs are `ov11_F_5962` (eight call sites), `ov11_F_5C42` (three), `ov11_F_4B0C` (three), and `ov11_F_583A` (three). The 8 sites to `F_5962` reduce to three short candidate callers because some functions call it more than once.

PC-relative data is a small, separable pocket: `ov03_F_0000` has one such reference and `ov07_F_03CC` has four. Their likely work is tail/data-boundary attribution, independent of the larger local-call clusters.

## A4 findings

All 18 short closed functions have A4-relative data references (117 total). Six use 21 A4-relocated call-stub sites. These are not queue blockers: the linker/verifier has an independent symbol-identity path for them, and the queue excludes those resolved stubs from `unknown_calls`. An instruction scan found no direct A4-register writes among the 18, so A4 restoration is not the mechanism suppressing this cohort.

## Highest-payoff local dependencies

1. **`ov11_F_5962` and `ov11_F_5C42` form a reciprocal call dependency.** Each is a pending local dependency for three short candidates, and they call each other. Together they sit in a seven-function short-candidate call component that also includes `ov11_F_2E26`, `ov11_F_54F8`, `ov11_F_5EC0`, `ov11_F_2430`, and `ov11_F_247C`. Every member has `same_node_unit_ready=false`; this is a natural-unit/interval-closure task, not a case where promoting either cycle member alone is guaranteed to release callers.

2. **`ov11_F_4B0C` is a fan-in dependency for `ov11_F_415A`, `ov11_F_6486`, and `ov11_F_0B4C`.** The first two have only this one pending local dependency; `ov11_F_0B4C` has two additional pending dependencies and exceeds the unknown-call cap. Recovering `F_4B0C` with its naturally required local unit is therefore the cleanest multi-caller unlock to investigate after the reciprocal cycle.

3. **`ov11_F_583A` is a lower-priority single-caller route into `ov11_F_13DC`.** It does not meet the multi-unlock payoff of the first two groups; its interval is noncontiguous, so it still needs natural-unit evidence.

These are payoff candidates, not guaranteed unlocks: the `same_node_unit_ready` flag is false for every dependency-bearing short candidate in the snapshot. A dependency promotion alone may leave the compile gate closed until intervening function ownership and natural unit layout are resolved. The four structurally gate-passing IDs are `ov11_F_5FB2`, `ov14_F_0412`, `ov14_F_04A8`, and `ov14_F_0540`; all currently carry `BLOCKED` state in the snapshot and should be rechecked after the supervisor finishes ledger repair.
