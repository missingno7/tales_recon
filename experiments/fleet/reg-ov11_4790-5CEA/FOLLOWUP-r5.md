Task reopened, leased to `luna-reg-ov11-r5` (renew: `python tools/fleet.py renew reg-ov11_4790-5CEA --worker luna-reg-ov11-r5`). 16 of 40 trials used; 24 remain. Do not stop early: continue until all members are EQUAL or the 40-trial budget is exhausted.

Priorities:
1. 487E (+38, similarity 0.37) is structurally wrong, not a tweak. Before compiling, re-derive its control flow from `python tools/grinder.py facts ov11_F_487E` (full CFG, calls, data refs) and write a fresh reconstruction that follows the original block order and call sequence; compare its per-member unit_diag block pairing against the CFG before and after. Record the rewrite as one hypothesis (member=487E) with a concrete prediction.
2. 4EC6 (+4, 0.99): look at the exact expected-only / candidate-only instructions and target that single construct.
3. 51C0 (-12) and 55B8 (-26): use expected-only instruction lists to find missing statements.
Keep 54F8/583A/5962/5C42 frozen and `--object-group ov11_F_583A,ov11_F_5962`. One member changed per variant, predictions first. Host is loaded: one command at a time. Write result.json (json.dump), `python tools/fleet.py intake reg-ov11_4790-5CEA --dry-run`, reply with the TASK line.
