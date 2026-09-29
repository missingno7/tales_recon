Excellent convergence. Task reopened, leased to `luna-reg-ov11-r6` (renew: `python tools/fleet.py renew reg-ov11_4790-5CEA --worker luna-reg-ov11-r6`). The supervisor grants a NEW budget of 30 compiler trials on top of the 40 used.

Freeze 4EC6, 54F8, 583A, 5962, 5C42 (keep `--object-group ov11_F_583A,ov11_F_5962`). Order:
1. 487E (+4, one unpaired instruction): identify that single instruction pair from the per-member diagnostic and target the one construct; predict length_delta -4.
2. 55B8 (-30; 10 expected-only vs 1 candidate-only): list the 10 expected-only instructions, map them to the missing statement(s), add exactly those.
3. 51C0 (-12 but similarity 0.64, 56/41 unpaired): this is structural. Before compiling, align the facts CFG block order (`python tools/grinder.py facts ov11_F_51C0 --max-instructions 2000 --max-bytes 2000000 > experiments/fleet/reg-ov11_4790-5CEA/facts-ov11_F_51C0.json`) against the per-member block pairing; identify which blocks are missing/extra/reordered (switch vs if-chain, loop form, shared exits) and rewrite toward the original block order as one recorded hypothesis per structural change.
Stop at all-EQUAL (report EQUAL_CANDIDATE with best.object_groups) or budget. One command at a time. Write result.json (json.dump), `python tools/fleet.py intake reg-ov11_4790-5CEA --dry-run`, reply with the TASK line.
