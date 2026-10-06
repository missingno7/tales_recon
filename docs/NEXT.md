# Current handoff - 2026-10-06

This is a validated consolidation checkpoint. The original requested pass is
not complete: AJ/FFP private-helper binding, live runtime-trace ingestion, and
the remaining legacy workflow/documentation audit still have open gates.

Canonical coverage is 156 functions / 42,116 C bytes. The generated
`progress.json` is the measurement authority. Whole-file accounting has 1,494
compiler-owned data bytes, 588 pinned runtime bytes, 2 classified padding bytes and 148,804 file bytes of
RAW_ORACLE_DEBT (including 6,680 structural bytes). Allocation-only zero fill
is separate. Accounting grants no new reconstruction proof.

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
compiler release. Keep ov04 closure ahead of unrelated targets.

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
