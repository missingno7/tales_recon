# Current handoff - 2026-10-12

This is a validated consolidation checkpoint. The original requested pass is
not complete: AJ/FFP private-helper binding, live runtime-trace ingestion, and
the remaining legacy workflow/documentation audit still have open gates.

Canonical coverage is 226 functions / 107,196 C bytes, plus two complete mixed
objects with 500 C bytes, 48 ASM bytes and a 2-byte compiler literal. The generated
`progress.json` is the measurement authority. Whole-file accounting has 2,800
compiler-owned data bytes, 588 pinned runtime bytes, 2 classified padding bytes and 81,172 file bytes of
RAW_ORACLE_DEBT (including 6,680 structural bytes). Allocation-only zero fill
is separate. Accounting grants no new reconstruction proof.

## Current campaign (2026-10-12): resident-first fleet

The ov04 campaign below recovered all 24 known ov04 functions; its natural
link is now blocked mainly by root content (root CODE 2,744 of 36,260 bytes),
not by ov04 source. Recovering real resident game functions is therefore the
route to ov04 closure, and it is also the largest ready pool: resident code
below the first runtime candidate (0x75D8) had no prior attempts.

Work selection is now evidence-based (see `fleet.md`):

- Resident functions below the runtime floor, with a single measured data
  model and the ordinary safety limits, are normal `READY_FOR_HAIKU` tasks.
  The runtime tail, mixed data models, uncertain extents and indirect flow
  stay deferred with explicit reasons.
- `data_model`/`profile_hints` come from measured addressing: absolute DATA
  relocations mean `aztec36-large-data`, A4-relative data means `aztec36`.
  Jump-table call slots are not data.
- Leverage counts real PC-relative dependants (400) above A4-stub callers
  (100); stub callers already verify independently.
- `python tools/fleet.py wave N` leases independent tasks and writes Agent
  dispatch specs for Haiku workers; intake re-verifies, the supervisor promotes.

Measured first session (2026-10-12): canonical coverage rose from 156
functions / 42,116 C bytes to 183 / 54,134; whole-file RAW_ORACLE_DEBT fell
from 148,254 to 136,134. Haiku workers (29 tasks, 4-7 concurrent, six waves,
110 compiler trials in total) produced 26 promoted exact matches (20 resident;
overlay ov07_F_1A02 1,388, ov07_F_0F30 1,268, ov15_F_0C12 1,972+98 literal,
ov10_F_2634 1,366, ov10_F_3288, ov10_F_2CF4): 10,410 bytes, a median of 3
trials per match, about 9,500 accepted bytes per 100 trials. The other three
tasks ended as precise shared blockers. Every claim was re-verified at intake and
published through the batch regression gate; review renamed three
offset-forcing `pad` locals and rejected none. Opus re-measured Luna's retired
`ov11_F_2EEA` near-miss and made it exact (1,608 bytes: one wrong global name
and two if/else join shapes), and fixed proven-object dependency units, which
released ov10_F_2634/3288/2CF4 (2,624 bytes).

Continuation (2026-10-12, later): two static/planning rules reopened the
queue. (1) The census now proves Manx `switch` word tables whose `default`
arm precedes the dispatch: 18 functions (46,576 bytes) became CLOSED_CFG,
including all known ov09 code; the remaining UNCERTAIN pool is ~10 KB of
small resident/runtime fragments. (2) A resident game caller's PC-relative
call into the runtime tail (DOS/exec glue such as `resident_F_86F6` Read) is
no longer a pending source dependency: check_function already verifies such
callers standalone and binds the call by mechanical symbol, as for canonical
`resident_F_7B24`. Waves 7-8 (17 Haiku tasks, up to 11 concurrent) promoted
16 functions; `resident_F_411E` joined the char-return EXT.W mechanism with
`ov14_F_0412/04A8/0540` (now four functions). Blocker categories are taken
from the leading `MECHANISM:` token first.

Wave 10 and two Opus fixes (2026-10-13): the owned-literal tail proof now
decodes around switch tables (closed ov06_F_063A, 2,690 bytes), and an
original `bsr` between a new and a standalone-proved canonical function
admits an evidence-backed object group (closed ov07_F_1F6E, ov05_F_467E
5,438 bytes, ov08_F_1AB8 with unchanged worker sources). Also promoted:
ov12_F_0000 (2,998, all known ov12 code), ov15_F_0000 (2,190), resident_F_3008.
ov09_F_0000 (6,334 + 18 literal bytes, all known ov09 code now canonical) closed in four one-factor Opus steps from the worker's NEAR: empty `if (x) ;`, unsigned `c > 0`, `(char)` of an int member (low-byte displacement), and `while (!changed)`; these idioms are now in the packet lessons.
Wave 11 promoted ov07_F_1424, ov06_F_0000 (ov06 known code complete) and ov05_F_3B6C. ov08_F_1F4C stays 12 bytes short after two rounds (SOURCE_SHAPE_RESIDUAL); its claimed MOVEQ mechanism is refuted (the assembler turns move.l #small into moveq). ov10_F_0000 (7,990) remains approximate.
ov03_F_001C (4,494 + 854 literal bytes) closed after two tool fixes: the Manx
symbol map prints hunk numbers in decimal (the parser read them as hex, so
every proxy symbol in hunk 10+ was unbindable, e.g. calls into ov14/ov15),
and same-object evidence now also counts a PC-relative JSR to an
overlay-exported callee (separately compiled callers route exports through
the A4 trampoline), admitting members between an evidenced pair. Its 38
worker gotos were then removed by a restructuring worker (EQUAL, zero gotos;
the decisive form was one `if (rv == 0 && f1f == 0) ... else if (f1f != 0 &&
rv == 0)` chain). ov03_F_0000 followed once the census evidenced a
PC-relative empty literal `""` (a NUL right after `rts`), so all known ov03
code is canonical (ov03 RAW_ORACLE_DEBT 0).
Canonical replacement is now transactional (`tools/canonical_replacement.py`,
via `check_function`/`check_unit --replace-canonical`): a complete-unit
receipt pins its canonical dependencies' source hashes, so replacing one
re-proves every pinning dependent in the same transaction (dependents are
withdrawn while re-proved, one regression gate on the pre-state, full
rollback on any failure); grouped or chained dependents refuse, and
promote_batch refuses replacements that would stale a receipt.
Runtime below the tail: resident 0x6FD8..0x704E is c.lib's `kputchar`
debug-output member (kputchar/kputs/kgetchar/KMayGetChar/KPutFmt/kprintf/
KDoFmt), matched exactly, uniquely and relocation-free when linked alone
(`tools/runtime_members.py`, `evidence/experiments/runtime-members.json`).
The planner now treats calls into pinned member entries as runtime calls
and never tasks the member's bytes; the runtime floor is unchanged because
real game code follows the member. This released resident 3930, 3A06 and
3674 (which call `kprintf` at 0x701A), and through them 3870, 3A6E, 3AE4
and 0FDE. resident_F_08FC (squared distance, `.mulu` via A4) closed first
try under the new helper route.
CHAR_RETURN_EXTENSION is now a measured TOOLCHAIN blocker: every char
return widens under Aztec 3.6a (11 source forms, +X1..+X5, 17 accepted
single-letter options) and 5.0a; the game has no widened byte return and
exactly four bare signed ones (411E, ov14 0412/04A8/0540). It needs another
historical compiler release (3.4/3.6 pre-a) or non-C provenance; it gates
404A/4184, the 287C region and ov14_F_0000.
ov10_F_0000 (7,990 + 90 literal bytes; all known ov10 code) closed in an
Opus pass from the round-2 NEAR in six one-factor steps: an `else if` chain
that re-tests `(action & 128) &&` in every arm (the original's repeated
`btst #7`), two removed redundant calls, a missing three-iteration draw
loop and its `(64L, 40L, ..., 176L, 160L)` box arguments, no `default:
break;` (it adds a dispatch jump and an end jump), and 54-byte record
indexing as pointer arithmetic (`(struct Rec54 *)&G + i`; `char * + 54 * i`
adds `ext.l`). The last residuals were relocation identities only (two
swapped/shifted globals and a 4EC6/435E callee name). Three unused locals
remain under neutral names because the 134-byte frame requires them.
OWNED_TAIL_UNBOUNDED resolved (CFG/BOUNDARY): the census now seeds a weak
`POST_LITERAL_PROLOGUE` entry where a function's referenced literal bundle
(NUL-terminated printable runs it references, plus one alignment byte) is
followed directly by an uncovered `link a5`. Such entries stay UNCERTAIN
(no caller) but bound the preceding tail. Four entries appeared (ov11 20AE,
resident 1306/39C0/39F8; no existing extent changed); ov11_F_15C8 (2,778)
and resident_F_3930 then promoted unchanged apart from neutral struct names.
`tools/boundary_refresh.py` now writes the census before type evidence (a
census change regenerates the instruction index) and checks type evidence.
ov07_F_0612 (1,684 + tail) closed unchanged once ov07_F_1424 filled its
gap (NONCONTIGUOUS_LOCAL_UNIT_LAYOUT resolved by recovery, not tooling).
Open: ov11_F_15C8 is EQUAL but its tail is followed by unreferenced code at
0x20AE (OWNED_TAIL_UNBOUNDED); ov09_F_0000 is two residuals from exact;
ov03_F_001C matches shape and its 853-byte tail but needs ov03_F_154E/1500;
ov05_F_1EFC joins the FFP family. `tools/boundary_refresh.py` replaces the
manual post-promotion steps (two refused gates came from skipping them).

Wave 9 (10 tasks) promoted ov09_F_1B1C (2,986), ov08_F_354E (2,214),
ov11_F_0D8E (1,508) and resident 3C4C/2FE2/2816. Four ended as shared
mechanisms: SAME_OBJECT_SHORT_CALL (a `bsr.b` to a canonical callee proved
standalone: resident_F_033E, ov07_F_1F6E), NONCONTIGUOUS_LOCAL_UNIT_LAYOUT
(ov07_F_0612 calls 18F8 across an unowned gap), TAIL_PROOF_TABLE_SPANS
(ov06_F_063A: the owned-tail proof decodes without jump-table spans, a
verifier fix), and STALE_PROVEN_OBJECT_GROUP (ov11_F_2272: all 60 members of
its grouped natural unit are now EQUAL after ov11_F_40AE, but the recorded
407C+40E0 object predates 40AE). Lesson: keeping runtime-tail/A4-stub
callees external inside `prepare_unit` was tried and reverted; it broke the
proven standalone stand-in fallback (resident_F_2FE2 EXTRACTION_BLOCKED).
Rank-level exclusion (runtime_tail_call) is the working rule.

Earlier handoff state: the READY_FOR_HAIKU queue was drained (`fleet.py wave N
--dry-run` returns nothing claimable). Further gains need, in leverage order:
(a) runtime-tail identification below; (b) the IMPLICIT_HELPER_A4_ROUTE
harness export control; (c) the G_h01_A15E natural-unit view decision;
(d) the AJ/FFP binding that also gates `ov11_F_0B4C`; (e) static extent
recovery for UNCERTAIN functions (384 resident, all of ov09). Re-plan after
each; newly canonical callees release waiting callers automatically.

Next resident frontier: of 38 eligible resident functions, 15 wait on
PC-relative calls into unidentified runtime-tail code (`resident_F_86F6`,
`8708`, `8820`, `894A`, ...). Identifying those library contributions
(RUNTIME/LIBRARY) is the next Opus campaign; 15 more wait only on game
callees and open as waves land.

Opus-owned shared blockers now in `blockers.json` `function_blockers`:

1. RESOLVED `IMPLICIT_HELPER_A4_ROUTE` (CALL_BINDING): resident callers
   reach `.mulu/.divs/.mods/.modu/.divu` through A4 jump-table slots because
   overlays call those helpers. Measured: an overlay object that calls the
   helpers, referenced from the root harness, turns a resident candidate's
   `jsr .mods` into `jsr d16(a4)` and changes nothing else.
   `tools/helper_exports.py` adds that control (harness only, never claimed)
   for exactly the sources whose original functions call pinned
   runtime-arithmetic entries through A4 stubs; verifier, unit trials and
   proof re-derivation register the same route. `compiler_oracle.py` stays
   byte-identical (a comment-only edit stales 15 resident DATA-interface
   proofs), so the module wraps its harness/proxy builders for registered
   sources only. `resident_F_09C0`'s unchanged worker source is now
   canonical; 08FC, 3AE4 and 7430 re-enter the queue.
2. RESOLVED `PROVEN_OBJECT_GROUP_DEPENDENCY` (OBJECT/TU_LAYOUT; `ov10_F_2634`,
   which gates `ov10_F_3288` and `ov10_F_2CF4`, ~2.6 KB): automatic dependency
   units compiled canonical `ov10_F_22E6` outside its proven
   `1FDE+2160+22E6` object (undefined externs it inherits from `2160`).
   `check_unit.prepare_unit` now closes over hash-checked proven object
   membership (`proven_object_members`), so the unit compiles; the Luna-era
   draft is 30 bytes short of the 2,842-byte unit and is back with Haiku.
3. `XOR_RESULT_REGISTER_ORIENTATION` (SOURCE_SHAPE; `resident_F_463E`, 56
   bytes): no tested form or release puts the `eor.w` result in the
   first-evaluated register.
4. `NATURAL_UNIT_DECLARATION_VIEW` (DECLARATION_VIEW; `ov11_F_2272`, 386
   bytes): with `--object-group 2272,23F4,2430,247C` in natural interval
   0x2272..0x5FB2 the entry and its group are EQUAL (positive TU evidence), but
   canonical `ov11_F_407C` differs: `G_h01_A15E` has two canonical views
   (`struct Record`/`struct Event`) and the harness keeps one per symbol.
5. Existing: ov14 char-return `EXT.W`, AJ/FFP (`ov11_F_5FB2`, `ov05_F_3836`),
   `ov05_F_2CD4` (real source-shape residual, 0.94 similarity), uncertain CFG
   extents.

Time-boxed: `RESIDENT-VARS-LAYOUT-001` (two indistinguishable vars providers).
Return to it when recovered resident readers/writers bind the actual storage
and first-reference COMMON order. Opus-owned shared blockers, in order:
resident DATA/COMMON ownership, ov14 char-return `EXT.W` (TOOLCHAIN),
AJ/FFP private helper binding (`ov11_F_5FB2`), uncertain CFG boundaries.

## First closure campaign: ov04

All 24 known closed-CFG functions are canonical: 9,758 C bytes,
1,008 compiler-owned data bytes, 2 proved terminal padding bytes and zero initialized debt bytes.
`../evidence/closure/ov04.json` lists canonical and remaining function identities;
`../evidence/hybrid/accounting.json` contains the complete ownership partition.

The strict curated claim in `../evidence/contributions/padding.json` explains
2A0E..2A10 using the actual full-link output. Its loader re-derives all source,
proof, object-group, profile, compiler and retained unit inputs, replays all
24 members including actual literal bytes, and rejects incoming references,
changed allocation or stale dependencies. Zero accounting debt grants no
natural node or whole-file proof.
No ov04 pinned runtime contribution is proved.
Resolve relocations against independently established target identities, and
review separately compiled source/object ordering. Existing accepted grouping
receipts constrain historical hypotheses without establishing original TUs.

The first bounded wave accepted F0536's 622-byte body and 38-byte literal tail,
plus F1302's 410-byte body through seven separately compiled dependency objects.
F1E36 is now accepted at FUNCTION_WITH_DATA_MATCH: 1,784 body bytes and its
complete 450-byte literal bundle. The three separately compiled objects match
all 3,032 contribution bytes, including canonical F26F0 and F27FE and their
previously proved tails. Independent linker controls explain
F27FE's A4 overlay trampoline: a resident initialized function-pointer reference
exports it and changes separate callers' route, while an unreferenced helper
remains PC-relative. `../evidence/rules/ov04-export-routing/proof.json` retains
the authored sources and positive/negative controls; it grants no source or TU
acceptance. The evidence-rooted recipe now propagates through ordinary, queued
and mixed-profile compiler/cache/unit identities, with strict inventory/member/
harness re-derivation and complete-unit trampoline mapping. Legacy recipes stay
valid. Owned automatic units now use existing per-member tail verification.
The accepted compile has five F27FE A4 trampoline calls and five F26F0
PC-relative calls. Its distinct resident call targets and G2EE8/G2EF0 references
are independently bound. Canonical batch verification and the regression gate
accepted the unchanged source; census and hybrid replay validate the new proof.

Independent natural interval checks match 07CA..1302 and 26F0..2A10; the latter
includes the linker's two-byte terminal zero pad. This is evidence for the
layout hypothesis, not accepted padding ownership or full overlay closure.
`../evidence/rules/ov04-natural-intervals.json` retains the compact inputs.
Pinned Aztec 3.6a linker controls establish `+ccd` as a natural CHIP allocation
selector for CODE and initialized DATA. The retained rule does not establish
the original release or a complete ov04 link.

Exit gate: every initialized byte independently explained; all game-owned
C/ASM reconstructed; compiler literals/data proved; runtime contributions
identified or independently separated; all relocations/layout reproduced by
the ordinary historical overlay link; zero ov04 RAW_ORACLE_DEBT. An accounting
image assembled with oracle debt cannot satisfy this gate.

## Top five blockers by leverage

1. Resident DATA/COMMON: recover real initialized contributions and intervening
   allocations. SDK-compatible RasInfo/BitMap views now pass exact source
   verification, but establish no original ownership or TU order. Their first
   92-byte COMMON cluster covers only 16 of ov04's 185 root relocation sites.
   Categories DATA_OWNERSHIP / OBJECT/TU_LAYOUT.
2. ov04 natural node link: the refreshed 15-object link matches all 24 functions,
   literals, 185 relocation layouts and 10 ordered exports. Its 1,496 raw byte
   differences are confined to independently proved address fields. Root CODE
   is 2,744 versus 36,260 bytes; root DATA initializes 556 versus 11,956 and
   allocates 4,960 versus 46,044. Preserve these open obligations and the full
   14-slot topology requirement. Category OBJECT/TU_LAYOUT.
3. AJ/FFP external identities: controlled AJ specimens now establish a bounded
   external-word grammar and natural PC binding. The real FFP object still uses
   unsupported records. Extend only with positive/negative specimens, consume
   the proved identities in the strict verifier, and leave ov11_F_5FB2 blocked
   until private helpers resolve independently. Category CALL_BINDING.
4. Indirect control flow: the small WinUAE pipe history collector and bounded
   event validator exist, but no live-game trace/overlay-load adapter has been
   validated. Establish a load epoch and a genuine single-step edge, then
   return to static table/extent proof. History adjacency is only a candidate
   edge, and an observed target never proves completeness. Category CFG/BOUNDARY.
5. Declaration/object isolation: verify actual dependency units with distinct
   compatible partial views and explicit same-object conflict controls.
   Compiler-identity changes leave several old cache controls skipped until
   rerun. Categories DECLARATION_VIEW / OBJECT/TU_LAYOUT.

## Normal worker commands

```powershell
python tools/grinder.py rank --node ov04 --limit 5
python tools/grinder.py facts ov04_F_1E36 --max-instructions 1000 --max-bytes 150000
# Write candidate to build/workers/NAME/candidate.c, then diagnose locally.
python tools/check_function.py TARGET build/workers/NAME/candidate.c --profile aztec36 --isolated --no-promote
# After an exact result, promote the unchanged candidate.
python tools/check_function.py TARGET build/workers/NAME/candidate.c --profile aztec36
# Existing batch alternative for independent promotions:
python tools/promote_batch.py build/workers/wave.json --verify-only
python tools/promote_batch.py build/workers/wave.json
```

Dependencies compile as separate objects by default. `--object-group` is an
evidence-backed hypothesis; arbitrary canonical concatenation is not a default.
Only expose declarations needed by the candidate TU. No universal struct
merger or inferred shared header is an authority. Ranking favors closure and
caller unlocks; report a blocker category and smallest changed experiment on
failure rather than repeatedly spawning the same hypothesis.

## Validation and assumptions

```powershell
python tools/type_evidence.py --write
python tools/census.py --write
python tools/census.py --check
python tools/hybrid_image.py --check
python -m unittest discover -s tests -v
# Re-derive produced specimens only with the validated historical caches/tools:
python tools/hybrid_image.py --refresh --write
```

The normal resident CLI promotion passed the full regression gate.
Census validates all 156 canonical proofs.
Hybrid accounting has zero overlap and zero unaccounted file bytes, and refresh
replays all 156 retained exact artifacts.
Queue/batch regression tests remain active; fresh compilation of the skipped
controls is still due. The automatic-unit producer now retains raw conflicting
TU declarations and derives only the harness's filtered view. The strict
consumer caught the earlier invalid F1302 receipt; it was withdrawn and replaced
through normal verification and promotion, with negative provenance controls.

Pinned Aztec 3.6a is the primary profile; compatible 5.0a/short-int and existing
member-specific profiles remain available where receipts justify them. Exact
historical release attribution is unproved. Do not relock original fixtures,
force addresses, patch linked outputs or normalize unproved helper identities.

Proof levels are defined in `proof-levels.md`: semantic/similarity is advisory;
FUNCTION_CODE_MATCH requires complete bytes and independently resolved fixups;
FUNCTION_WITH_DATA_MATCH adds a proved compiler-owned tail; overlay/executable
levels additionally require independent content, relocation and natural layout.
RAW_ORACLE_DEBT is validation/accounting only, never reconstructed source.

Scratch and new attempts go under ignored `build/`; retirements go under
`to_delete/`. The user manually deleted the historical quarantine before this
push. No deleted archive is reintroduced in the active project or pushed.

Recommended next wave: bind the original resident runtime DATA consumers.
Independent SDK compilation reproduces the tested 3.6a/5.0a vars layouts,
but none of their complete ten-byte initialized contributions occurs in the
original. Do not reuse them as original providers or clip a two-byte match.
See `../evidence/experiments/runtime-vars.json`. The terminal word has three
original consumers; resident766C is a closed 310-byte startup CFG, while the
pinned complete object emits312 bytes including the same nonzero trailing
two bytes. Verify that whole unit's callee/global bindings before identifying
the original runtime DATA variant and its COMMON ownership. Natural COMMON
merging controls are measured; they do not select original object order or
compiler release. (Superseded 2026-10-12: this kept ov04 closure ahead of
unrelated targets while ov04 functions remained; all are canonical now and the
resident-first campaign above is the route to its natural root link.)

Startup routing controls now match all ordinary bytes of the complete312-byte
object. Eight global and eleven PC target bindings remain pending; callback
main uses logical node1, and exit requires a validated DATA jump entry.
The allocator/task public-private units add34 strictly accepted runtime bytes.
See `../evidence/experiments/startup-bindings.json`. No startup DATA or complete
root layout is accepted.

Alert, WaitPort and GetMsg now have independent complete-object/source/two-DATA-
order matches, adding48 experimental target bytes. Strict accepted-caller
entry checks remain intact and no bytes are counted. The CurrentDir target
at869C must not be confused with Forbid at8974. Next, bind DOSBase and the
remaining parser/global relationships; see startup-targets.json.

DOSBase is independently bound at H1+A98E by the CRT0 initializer. Five complete
DOS library/source leaves match54 candidate bytes in two DATA orders; CurrentDir,
Input, Output and Open resolve four startup correspondences (42 bytes). These
remain unpromoted. See `../evidence/experiments/dosbase-bindings.json`. Next verify
complete CRT0 identities, parser/global relationships and original storage
providers; preserve strict accepted-caller entry checks.

The bounded complete CRT0 review matches108 ordinary bytes and its one DATA
relocation. All differences occupy seven SDK fields; H1 end/BSS start and clear
count derive from original allocations. Saved-stack and startup-entry identities
remain pending. Source/library links equal while object files differ. See
`../evidence/experiments/crt0-bindings.json`; no runtime acceptance is added.

The first resident source contribution is now canonical: resident_F_77A4,
432 C bytes plus its2-byte compiler-owned literal, at FUNCTION_WITH_DATA_MATCH.
The unmodified456-byte pinned/SDK object differs; this is a reconstructed runtime
variant, without original filename, TU, provider or exact release attribution.
Fresh normal root verification proves all CODE and bindings under aztec36-x3.
Root-unit comparisons preserve actual root coordinates; strict named DATA
interfaces rederive source, original call facts, payloads, CODE relocations and
body mapping. Tampered/stale inputs reject. See
`../evidence/experiments/resident-cli-source.json`.

CLI global access views are now function-proved, but original DATA/COMMON
ownership and natural root placement remain UNKNOWN. The tested vars object
still contradicts whole original initialized DATA. Next verify the Workbench
parser and remaining startup/provider identities; use the normal isolated
verification boundary. All24 ov04 members and actual0000 padding replay under
the refreshed tool provenance; natural overlay/root/executable closure is open.

Workbench parser resident_F_7B24 is now canonical at FUNCTION_WITH_DATA_MATCH:
158 C bytes plus22 compiler-owned literal bytes. The bounded failed declaration
wave is retained; changing only two result declarations and long mode arguments
closed exactness. Normal promotion regression passed after refreshing stale type
evidence and making the queue fairness test independent of timestamp ties.
Original filenames, TU membership, runtime release and DATA/COMMON ownership
remain unknown. Next bind remaining startup consumers and the original provider.
See `../evidence/experiments/resident-workbench-source.json`.

Startup-called exit wrapper resident_F_8534 is now canonical:30 C bytes at
FUNCTION_CODE_MATCH, with its callback access and deeper exit callee bound.
The deeper resident_F_8552 CFG ends six bytes before the next entry; that
epilogue remains unclaimed. A complete unmodified SDK exit compile/assemble/link
produced284 CODE bytes against the original238-byte complete-object hypothesis.
Retained toolchain failures and full inputs are in resident-exit-object.json;
next compare cleanup branches before changing source. No original DATA/COMMON
provider or root layout is accepted. See
`../evidence/experiments/resident-exit-wrapper.json`,
`../evidence/experiments/resident-exit-boundary.json` and
`../evidence/experiments/resident-exit-object.json`.

The complete SDK-derived exit variant removes exactly three cleanup branches
absent from the original CFG and naturally produces238 CODE bytes. All180
ordinary bytes match, including the FPU thunk and six-byte terminal epilogue.
The58 address-field bytes have diagnostic source/symbol correspondences only;
no acceptance, runtime accounting, canonical boundary or provider claim changes.
Replay: `python evidence/rules/resident-exit-variant/replay.py`. Next independently
bind complete callees8640/8980/8788/8974/8A12 and cross-routine globals; a strict
whole-object consumer is still required. Retained newline and symbol-file
failures are in `../evidence/experiments/resident-exit-variant.json`.

Complete resident_F_8640 close source is canonical:76 C bytes. Its SDK-compatible
6-byte device-record accesses and all mechanical bindings pass normal exact and
regression checks. Strict FreeMem20 and CloseLibrary16 public/private units add
36 runtime bytes, using accepted ov04 public entries and both DATA orders. The
private-entry substitution negative control preserves the existing guard.
Three of five deeper exit callee identities are now independent; Forbid and
ReplyMsg, mixed-source whole-object acceptance and global/provider roles remain
open. See `../evidence/experiments/resident-close-source.json` and
`../evidence/experiments/resident-exit-bindings.json`.

All five exit callee identities now have independent source/library or canonical
source evidence. Forbid8 and ReplyMsg12 match uniquely at the proved SysBase
identity in both DATA orders; they remain outside runtime accounting. A complete
mechanical mixed-source control produces238 bytes with180 ordinary bytes and all
29 address fields matching. The two SDK assembly blocks are unchanged except
for saved-stack symbol spelling. Normal C promotion still rejects assembly.
Next add curated complete-source facts and a strict mixed-runtime recipe with
C/ASM partitions, inbound canonical anchor and rehashed negative controls;
retain all existing C and accepted-public-entry guards. See
`../evidence/experiments/resident-exit-message-leaves.json` and
`../evidence/experiments/resident-exit-mechanical.json`. No coverage/debt changes.

A label-only source control preserves complete CODE and all mechanical binding
coordinates and measures196 C-compiler bytes plus42 SDK ASM bytes. The terminal
six-byte epilogue belongs to C compiler output. This is source-language evidence
only; no canonical source extent, historical TU or accounting acceptance. Replay
`python evidence/rules/resident-exit-mechanical/replay.py`; partition inputs are
in `../evidence/experiments/resident-exit-partition.json`.

Strict staged verification now lives in `tools/resident_mixed.py`; curated
source-object facts are separate in `evidence/source-facts/resident-exit.json`.
It rederives the candidate from pinned SDK source, checks the exact harness and
producing commands, verifies whole-object bounds and all independent callees,
and decodes all238 bytes with coprocessor support confined to this SDK recipe.
The16 focused negative/positive controls preserve normal C rejection of inline
assembly and the runtime public-entry guard. Run `python tools/resident_mixed.py`.
Its VERIFIED_STAGED_MIXED_OBJECT result explicitly grants no acceptance. Next
integrate the curated extent and196 C/42 ASM partitions into canonical proofs
and accounting, with unchanged-source revalidation at that promotion boundary.
No generated function extent or coverage metric is hand-edited.

The normal census now revalidates curated mixed source-object facts into
`evidence/functions/source-objects.json`. It retains both the232-byte uncertain
CFG and independently proved238-byte complete object, with196 C/42 ASM bytes;
this staged view grants no canonical acceptance or coverage. Nested entries,
conflicting descent extents, accepted-source overlaps and attempted substitution
for a canonical proof are rejected. Scoped census reuse hashes the curated fact,
SDK source, retained artifact graph and independently checked library inputs;
edits or removed facts invalidate reuse. A fresh isolated historical-toolchain run
reproduces the unchanged sources, assembly, objects, linked executable and symbol
map byte for byte, and passes the strict verifier. See
`../evidence/experiments/resident-exit-refresh.json`. Next implement canonical
mixed-source proof/promotion and language-aware accounting using this separate
extent basis; keep ordinary C and runtime public-entry guards intact.

The complete SDK-derived resident_F_8552 mixed object is now canonical at
FUNCTION_CODE_MATCH in the separate recovery `mixed_source_objects` map.
Its source, complete238-byte extent,29 independent fields and196 C/42 ASM
partitions rederive on census and accounting reads. Normal C remains CLOSED_CFG
only and rejects assembly. A fresh unchanged historical compile and unchanged
validation input graph precede admission; ordinary recovery writes preserve the
mixed map. Whole-file debt falls by238 to148566, with no aggregate layout proof.
Forbid/ReplyMsg complete identity controls remain outside runtime accounting.
Next resolve the original DATA/COMMON provider and natural resident linking
needed for ov04 closure; original filename/TU/release and provider remain unknown.
See `../evidence/experiments/resident-exit-admission.json`.

Two bounded SDK vars hypotheses now naturally compile and link in two DATA
orders: remove the DETACH globals, or retain them without explicit initializers.
Both own zero CODE/two DATA bytes; their complete COMMON allocations differ64
versus72 bytes. The rounded00140000 DATA pattern appears at original H1 offsets
1002,1074 and11952. Canonical exit independently references11952, but neither
provider membership nor original COMMON allocation follows from the equal word.
No DATA, padding or COMMON bytes are promoted. Retained whole objects, header
pins, commands, maps and replay are in `evidence/rules/runtime-vars-variant/`;
see `../evidence/experiments/runtime-vars-variant.json`. Next bind complete
startup/CRT0 consumers and natural first-reference COMMON order before choosing
a provider hypothesis. Do not prune unreferenced globals merely because an exit
cleanup branch is absent.

The complete startup mechanical source now matches with LONG/D0 views for
the three pointer-returning assembly helpers and aztec36-x3. Pointer-return
views/default and LONG views/default both emit316 bytes; the one-factor+X3
control emits312. Decoded operands account for all38 address/literal fields,
including immediate-to-A4 and two-A4 instructions. Original and candidate
main/exit routes are checked through the overlay tree and DATA JMP relocation.
A label-only+X3 control preserves every byte and binding and measures304 C,
6 SDK ASM and2 compiler literal bytes (`*\0`). The whole object owns no DATA/BSS.
Retained recipes/replay in `evidence/rules/startup-mechanical/` use canonical
evidence paths, not ignored build inputs. Separate staged source facts are in
`evidence/source-facts/resident-startup.json`; no canonical acceptance or coverage
is granted. Next implement strict complete callee/producer verification and
mixed code/literal admission, then use startup/CRT0 objects for COMMON ordering.
See `../evidence/experiments/startup-mechanical.json`.

The retained startup producer now has a bounded audit in
`tools/startup_producer.py`. It rederives both sources and harnesses from the
pinned SDK recipe, requires the complete tool/header and artifact inventories,
checks exact producing commands and whole-object bounds, and preserves the
304 C / 6 ASM / 2 literal partition under the label-only control. Thirteen
retained-input tests cover omitted inventories, consistently rehashed source,
header and object edits, failed commands, partition claims and quarantine paths.
Its `VERIFIED_STARTUP_PRODUCER_ONLY` result grants no source acceptance or
coverage and is not wired into canonical promotion. Next independently verify
the complete callee bodies and original field identities, then require a fresh
unchanged compilation at the mixed code/literal admission boundary. DATA/COMMON
provider and natural resident layout remain unknown.

Validation for this producer-audit boundary: census write/check, hybrid check,
the unchanged startup field replay and all 468 regression tests passed (9
skipped). Canonical source acceptance and accounting totals did not change.

The complete resident_F_766C startup is now canonical in `mixed_source_objects`
at FUNCTION_WITH_DATA_MATCH: 304 C bytes, 6 SDK assembly bytes and the 2-byte
compiler literal. The 310-byte closed CFG and complete 312-byte source object
remain separate extents. All 38 fields rederive, including the actual node1
main route and relocated DATA exit entry. CLI, Workbench and exit anchors are
canonical; allocator/task helpers retain independent public/private bindings.
Fresh complete library/SDK-source links bind the seven remaining leaves (90
bytes) in two DATA orders, without adding runtime accounting. The DOSBase
initializer is checked independently. Open's 14-byte object remains distinct
from its control link's two-byte alignment.

Fresh startup and label-only compilations reproduce all retained source,
assembly, objects, executables and symbol maps unchanged. Canonical admission
rechecks the recorded validation inputs after the full 481-test regression
(9 skipped). Census and accounting consumers rederive the mixed proof and
count its literal separately. Normal C and public-entry library guards remain
intact. See `../evidence/experiments/startup-admission.json`.

Fresh complete CRT0 controls now establish natural COMMON ordering under the
pinned candidate linker. The unchanged library and SDK-source objects produce
identical whole executables in three contexts (16 successful guest steps).
Adding a separate four-byte DATA/eight-byte COMMON provider changes the seven
expected fields; all 108 other bytes and the DATA relocation remain unchanged.
Placing the unchanged library `_close` object before CRT0 moves DOSBase before
saved SP and SysBase without a filler object or fixed address. This explains a
possible mechanism for the original ordering, not its original provider.
`../tools/crt0_controls.py` replays pinned inputs, complete object boundaries,
source recipes, all fields, relocation and both whole outputs; the measured
report is `../evidence/experiments/crt0-controls.json`. It grants no acceptance.

Next complete CRT0 saved-stack/startup bindings using the canonical consumers
and review full runtime admission separately. Then identify the original
earlier DOS consumers and real DATA providers. Neither vars hypothesis is
selected: original DATA/COMMON provider, TU, filename, release and natural
resident/ov04 closure remain unknown. Coverage/accounting is unchanged.

CRT0 control validation: all 493 regression tests passed (9 skipped), including
12 new producer/order rejection tests. Census write/check, hybrid accounting
check and exact retained-report replay passed. The full regression log is
`../build/recovery/crt0-controls-regression.log` (ignored attempt output).
