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
before returning that slice. A promotion changes those inputs. Worker-facing
reads (`--function`, fleet packets, `allow_stale=True`) then still return the
last generated slice, with `stale: true`, `stale_reasons` and a note, and never
rewrite the report. `--function ... --strict` and `--check` refuse stale evidence. It includes program-wide observed widths for globals
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

## Canonical declaration views

`tools/declaration_views.py` answers a narrower question for workers: which
declarations do canonical recovered sources already use for the symbols a
target references? Only sources named by `recovery/ledger.json` are read.
Every `extern` statement is parsed, including several declarations on one
line, multidimensional arrays and `extern T F();` function views. Comments
are ignored. The target's symbols are its A4 data identities, excluding the
A4 jump-stub slot at each direct-call site, plus its direct callees. For each
symbol the report gives:

- the count per distinct view, one per source file;
- the majority view, with ties broken by source path and marked `majority_tie`;
- the alternatives, with sources;
- the observed original access widths from `evidence/types.json`, program-wide
  and for the target.

It includes only the struct definitions named by the chosen views. When sources
using those views define a tag differently, the majority body is emitted and
the others are listed. A data identity without an exact canonical name is
reported with any canonical view whose declared extent covers it. That extent
is estimated under the Manx 16-bit `int` model with even-aligned words, so
containment is a candidate, not an object boundary.

```powershell
python tools/declaration_views.py --function ov11_F_51C0          # JSON views
python tools/declaration_views.py --function ov11_F_51C0 --block  # paste-ready extern block
python tools/declaration_views.py --clusters                      # conflict breakdown (top 10)
```

These are candidate source views that already compiled exactly in other
routines. They are not historical type provenance. Access widths do not
determine a C type uniquely. Fleet packets use the block to keep worker
declarations consistent (docs/fleet.md). A worker that needs another view
records that view as a controlled change.

`--clusters` groups the pairwise conflicts of the single-line scanner above
by 256-byte DATA page. It also counts symbols with several views under the
full statement parser, and lists struct tags with more than one body. On
2026-09-28 there were 138 pairs in 14 clusters:

| Cluster | Pairs | Symbols | Relations |
| --- | --- | --- | --- |
| `G_h01_94xx` | 54 | 10 | 53 int/short ABI-compatible, 1 review |
| `G_h01_A1xx` | 21 | 2 (A15A, A15E) | 12 struct view, 7 review, 2 int/short |
| `G_h01_9Fxx` | 19 | 6 | 10 struct view, 5 pointer/scalar, 2 array/scalar, 1 extent, 1 review |
| `G_h01_A4xx` | 14 | 1 (A464) | struct view |
| `G_h01_A5xx` | 10 | 1 (A554) | struct view |
| `G_h01_8Axx` | 5 | 1 (8A3C) | int/short |
| `G_h01_79xx` | 3 | 1 (799E) | int/short |
| `G_h01_A6xx` | 3 | 1 (A6A8) | struct view |
| `G_h01_34xx` | 2 | 1 (34EC) | struct view |
| `G_h01_45xx` | 2 | 2 (4524, 452E) | struct view |

The full parser finds 43 symbols with more than one view. Nine struct tags
have several bodies: `Record` has 23, `MotionRecord` 5, `Event`, `Object` and
`Target` 4 each, `Item` and `State` 3 each, and `Flags` and `Row` 2 each.
Most pairs (63 of 138) are int/short views of one 16-bit word, which are
ABI-compatible in observed Manx use. The pairs that could change a harness
trial are the struct-view, pointer/scalar and array groups at `A15E`, the
`9Fxx` block, `A464` and `A554`. The report is diagnostic only. No canonical
source was rewritten, and any consolidation remains a supervisor decision.
