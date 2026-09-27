# Original-machine type evidence

`tools/type_evidence.py` produces a bounded diagnostic view in
`evidence/types.json`. It reads the locked executable through the existing
read-only census path, validates the fixture lock and current function-ledger
identity, then re-decodes instructions at the recorded offsets. A4 data
identities use the independently recorded A4 bias and the decoded displacement.

The report records byte widths at A4 references, direction when Capstone's
operand position makes it explicit, `lea` and `pea` address-taking candidates, an
immediately adjacent, same-register `ext` instruction as local context, and A5
frame-relative accesses at offsets of eight or more. A5 loads also retain
same-register `ext` context and `lea`/`pea` address-taking sites. A5 offsets
remain frame-access candidates: the tool does not assign them parameter numbers
or declare a prototype. Widths, extensions, and address-taking do not independently establish C integer
signedness, pointer type, ownership, semantic name, or object boundaries.

The declaration checker scans simple one-line `extern` declarations in C files
under `src/`. It compares repeated names and classifies the relationship rather
than rewriting source. In observed Manx use, `int` and `short` are both
16-bit-compatible declaration views when signedness also agrees; signed versus
unsigned views are reported separately. These pairs are distinguished from
`char`/word, `long`/word, pointer/scalar, and array-shape differences. Different
struct tags are review items because recovered routines may intentionally have
partial record views and the checker does not prove member layout. The compiler
harness keeps the first declaration of a repeated external symbol, so reported
shape conflicts can make a trial depend on source order. This is a diagnostic
about the harness and candidate declarations, not proof the original source
contained a conflict.

Run `python tools/type_evidence.py --write` to regenerate the measured report,
`python tools/type_evidence.py --check` to verify it, or
`python tools/type_evidence.py --function ov07_F_03CC` for a compact per-function
slice. The Python API `function_evidence(fid, root=ROOT)` applies the same
ledger, instruction-index, miner, and declaration-source freshness checks
before returning that slice. It includes program-wide observed widths for globals
the function touches, plus compact declaration-conflict totals; declaration
examples are filtered only when their mechanical `G_h01_HEX` suffix identifies
the same DATA-hunk offset. Each slice caps globals at 12, frame slots at 8,
examples at 8, and machine sites at 2 per item; the full evidence remains in the
JSON database.

The current report's counts summarize machine observations and declaration
relationships. They are not inferred-type totals and do not update generated
baseline ledgers or reconstruction ownership.

The measured report scans 652 function candidates and records 1,783 A4 data
offset identities, 7,885 A4 access sites, 1,430 address-taking sites, 178
same-register extension contexts, and 981 A5 frame-access sites across 354
frame offsets. A5 evidence includes 2 address-taking sites and 76 local
extension contexts. These totals describe decoded instruction evidence, not
separate source variables or parameters.

The declaration scan found 55 differing declaration pairs across 18 mechanical
symbol names. It classifies 43 pairs as struct-view review, 5 as pointer/scalar
shape differences, 4 as array-shape differences, and 3 as other declaration
view review. Examples include `G_h01_9F66` declared as both `long` and
`struct Sprite *`, and `G_h01_9F0C` viewed as `struct LongSlot[4]`,
`char[1]`, and scalar `char`. Struct tags may be partial views; the scan does
not prove size, offsets, or actual historical declarations. The 55 count is
pairwise and includes repeated cross-file combinations.

The report deliberately defers hard signedness and pointer conclusions,
parameter-number/prototype recovery, struct member and extent validation,
ownership, and semantic naming. Extension context is strictly local to an
adjacent same-register load; it is not whole-function signedness proof.
