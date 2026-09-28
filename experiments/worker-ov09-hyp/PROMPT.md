# Task: controlled causal experiment on ov09_F_298E (historical reconstruction repo)

Read AGENTS.md, docs/proof-levels.md, docs/compiler-archaeology.md ("Measured outcome"),
docs/source-shape-search.md, docs/m68k-diagnostics.md first. Rules: assets/ is immutable;
never relock fixtures, never promote, never edit recovery/ canonical sources or generated
docs/*.json ledgers. Write ONLY under experiments/worker-ov09-hyp/.

Goal: test whether diagnostics are ACTIONABLE, i.e. whether a predicted instruction-level
change actually happens. Not to maximize similarity scores.

Baseline: experiments/direct-recovery/ov09_F_298E-v15.c (672 bytes vs original 660; diag aligns
183 insns, 6 candidate-only insns, repeated index/result register-role differences).
Get its cache key from evidence/experiments/source-shape-search-baseline.json and run
`python tools/diag.py ov09_F_298E --cache-key <key> --json`.

Steps:
1. TRACE: find the FIRST point where register choice diverges (original vs v15) and the six
   extra instructions. Explain in terms of C source constructs in v15 (which expression /
   temporary / index variable causes each). Write experiments/worker-ov09-hyp/TRACE.md
   with instruction offsets and the source line each maps to.
2. HYPOTHESES: author 6-8 variants, each a copy of v15 with EXACTLY ONE controlled change
   from these factors: temporary lifetime (introduce/remove/scope a temp), expression grouping
   (split/merge/reorder subexpressions), index width/signedness (char/short/int index,
   cast placement). Keep compiler profile aztec36 constant. Files: experiments/worker-ov09-hyp/hNN_<slug>.c
   BEFORE compiling anything, write experiments/worker-ov09-hyp/hypotheses.json: a list of
   {id, source, parent:"v15", suspected_cause, controlled_change, predicted_effect} where
   predicted_effect is concrete and checkable (e.g. "the 2 moveq/ext.w pair at cand +0x3A
   disappears; index reg becomes d4 as in original"; expected byte delta). Commit to predictions;
   do not edit them after results.
   Reject duplicates: no two variants may be identical after stripping comments/whitespace,
   and none may equal an existing experiments/direct-recovery/ov09_F_298E-v*.c or
   experiments/worker-ov09-298e/*.c after the same normalization.
3. RUN: write a schema_version 1 manifest (see docs/source-shape-search.md) including v15
   as control and run `python tools/shape_search.py <manifest> --json --output-dir experiments/worker-ov09-hyp/reports > experiments/worker-ov09-hyp/results.json`.
   Compiles go through the normal compiler oracle (may take minutes; that's fine). Budget: max 9 unique compiles.
   If the compiler path is unavailable, stop and report exactly why (do not invent results).
4. OBSERVE: for each variant run diag vs its cache key and record in
   experiments/worker-ov09-hyp/observations.json: {id, exact_verdict, length, byte_delta_vs_v15,
   predicted_effect_occurred: yes|no|partial, what actually changed (instruction-level), updated_explanation}.
   If a variant hits EQUAL, report it prominently but DO NOT promote it.
5. If at least one prediction was confirmed but not exact, you may run ONE follow-up round of
   up to 4 variants combining confirmed factors (same rules: predictions first, dedup, record).

Final answer (<=15 lines): exact matches / compiler trials, predictions confirmed/partial/refuted,
the most important updated explanation, and file list.
