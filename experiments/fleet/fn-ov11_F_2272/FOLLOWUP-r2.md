Task reopened, leased to `luna-fn-ov11_F_2272-r2` (renew: `python tools/fleet.py renew fn-ov11_F_2272 --worker luna-fn-ov11_F_2272-r2`). New budget: 10 compiler trials.

Your remaining difference (JSR vs original BSR.B to F_h11_2430) indicates a same-object (same translation unit) call. ov11_F_2272 (0x2272..0x23F4), canonical ov11_F_23F4 (..0x2430), canonical ov11_F_2430 (..0x247C) and canonical ov11_F_247C (..0x2562) are contiguous. The unit verifier now supports `--object-group ID,ID,...` (see docs/fleet.md, docs/proof-levels.md): members compiled as one object, canonical members allowed if their proven grouping lies inside the group. Hypotheses (one per trial, predictions first):
 A: `python tools/fleet.py verify-unit ov11_F_2272 <your best source> --profile aztec36 --separate-objects --object-group ov11_F_2272,ov11_F_23F4,ov11_F_2430` — predict the late call becomes BSR.B and the unit length matches.
 B (if A refused or differs): include 247C in the group.
 Also consider `--per-member-profiles` if any canonical member was proven under aztec36-large-data (check recovery/proofs/<ID>.json compiler profile).
Do not edit canonical sources. If EQUAL, set best.verifier="check_unit" with options including object groups (best.object_groups). Write result.json (json.dump), run `python tools/fleet.py intake fn-ov11_F_2272 --dry-run`, reply with the TASK line.
