# Reconstructed assembly admission

`tools/reconstructed_asm.py` supports two individually bounded resident spans:
559E..55D6 (56 bytes, cross-instruction CCR-X register/memory rotation loop) and
59A4..5A50 (172 bytes, saved A4 small-data world replaced by a typed record cursor
and restored). Every census/admission/accounting read decodes the current oracle
and rederives its predicate; adjoining code receives no inherited eligibility.
The recursive function ledger keeps its UNCERTAIN status. Complete span proofs
separately check direct-call entry evidence, no undecoded gaps, full register
save/restore/RTS boundaries, and the specifically resolved A4 dataflow stops.

Curated facts and the one-job batch pin inventory are in
`evidence/reconstructed-asm/`. Hash-bound mnemonic candidates live in
`evidence/rules/asm-reconstructed/`. A successful promotion writes only
`src/recovered/asm-reconstructed/`, `recovery/proofs/asm-reconstructed/` and the
separate `reconstructed_asm` ledger map. The full shared regression gate and
unchanged-input checks precede the atomic publication. Every canonical read
replays the exact source recipe, complete producer graph, complete AJ object,
CODE and all named relocation bindings. Verifier hashes are provenance only.

```powershell
python tools/promote_asm.py --manifest evidence/reconstructed-asm/batch.json --verify-only
python tools/promote_asm.py --manifest evidence/reconstructed-asm/batch.json --promote
python tools/census.py --write
python tools/census.py --check
python tools/hybrid_image.py --write
python tools/hybrid_image.py --check
```

The final pinned batch job is `build/worker-jobs/sol-audio-asm-011`. It assembles
both modules separately and links each against a separate diagnostic scalar
binding harness. No original executable is mounted. Batch evidence pins the
request, result and every artifact by SHA-256; it never embeds a job receipt.
If retained inputs are missing, prepare a fresh ordinary aztec_worker job with
the unchanged sources and exact commands, collect it and review updated batch
pins before verification. No cached PASS can replace missing producing inputs.

DATA declarations in the assembly and natural alignment in the test harness
have zero DATA/provider credit. No table or record initializers are included.
Historical owner, author, filename, object/TU membership and root layout stay
UNKNOWN. Source accounting uses RECONSTRUCTED_ASM, separate from C and from
provenance-backed RECOVERED_ASM. Ordinary C acceptance is unchanged. The hardware
store wrappers558A/5594 reject these two predicates. Batch 0004 below supplies a
separate calibrated entry witness for5594;558A remains unrooted.

The handler table has44 relocated slots80..AB. The interpreter's CMP#2C/BLE also
permits index44 to address adjoining period DATA; this is not a45th handler.
Envelope pointers/records and other spans retain their open evidence obligations.


## Separate driver batch 0002

This manifest is independent of the accepted first batch. Proposal2 was rejected:
D2 is scratch in pinned Aztec 3.6a C, and absence of a D7 save in the then-observed
C corpus did not establish D7 preservation. Neither premise is retained.

Every admission and canonical replay now rederives register calibration from
hash-bound ordinary C proofs, the canonical complete-C objects, and pinned
compiled controls. Each oracle instruction is decoded again; inline jump-table
DATA is excluded. Mixed C/ASM modules do not define the ordinary C ABI.
D2 has eleven unsaved-write counterexamples, including resident_F_31AA at 32D0
and ov08_F_1F4C at 2C60. A pop of a discarded argument into D2 counts as a write,
not an entry restore without a prologue save.

The four-register control saves/restores D4-D7; the six-register control
saves/restores D4-D7/A2-A3. Both use ordinary stack parameters and call an external
C function. Full AJ objects, named PC16 calls, diagnostic binder and complete
links rederive. The combined measured saved set is D4-D7/A2-A3; D0-D2/A0-A1 are
scratch; D3 and A4 preservation remain unmeasured. No unmeasured register earns a
preservation witness. A new unsaved D7 C counterexample or changed control makes
the D7 premise fail closed.

All eight proposed spans retain independent witnesses after the correction:

| H0 span, half-open | CODE bytes | Valid non-C witness |
| --- | ---: | --- |
|544C..558A|318|A0 channel input read at entry; caller 5936 supplies it without a stack argument|
|5796..57C0|42|A4 world setter/capture and register-argument bridge|
|57E4..5868|132|D0 register argument; explicit preservation of measured caller scratch registers|
|58BC..59A4|232|D7 loop overwrites the entry value without the calibrated required preservation|
|5A50..5CC2|626|A0/A1 register-stream entry, JMP-entered handlers, saved A4 record consumer|
|5CC6..5D74|174|Relocated JMP-entered register-ABI handlers and shared tails|
|5D78..5D80|8|Relocated JMP-entered register-ABI handler tail|
|5D92..5E6C|218|Relocated handlers, stream prefetch/rewind and shared tails|

The dispatcher witness does not use D2 preservation. Its caller passes an A0
channel without a stack argument; the entry reads A0 and loads A1; command
dispatch zeroes D0.w, prefetches a byte, and jumps through A2 without a new return
frame. Every one of the 44 H1+292E slots 80..AB names an exported instruction
entry. CMP #2C/BLE also admits index 44, which reads adjoining period DATA at
H1+29DE; it remains an explicit unproved computed edge, never a 45th handler.

A SYS1-compiled C function-pointer dispatcher, the register-heavy C controls,
and C-compatible 5428/558A/5594 reject the non-C predicates. The four IRQ routines
55D6/5646/56B6/5726 use ordinary scratch D0/A0 and remain UNKNOWN on the C route.
The three orphan fragments lack independent entries. Eligibility never follows
from adjacency or lack of a frame alone.

One final producer job, sol-audio-asm-017, supplies all 21 source inputs and
35 successful guest steps. Curated evidence pins paths/hashes, with no embedded
job receipts. Complete source objects own 1,750 CODE bytes and zero DATA/BSS/
COMMON. Strict AJ decoding checks every token, symbol, long-reference count,
PC16/long field, section transition and trailer. Whole links check every symbol,
hunk, ordinary byte and named field. No opcode or ordinary operand is masked.
Contributions use AJ-produced bytes and only proved named address rebinding.

The synthetic RTS/scalar binders, linker alignment and dseg declarations earn no
credit. Envelope/handler pointer tables, records and the base at H0+5E6C still
need independently typed and bounded DATA providers with named proved targets.

Fresh calibration always guards the predicate. Its corpus digest and observed
counts are retained provenance, not a cached acceptance decision; additional
agreeing C proofs do not stale an ASM body, while a counterexample to an active
premise rejects it. The shared input closure includes canonical C sources/proofs
and the controls. Verifier identity remains provenance only. Owner, original
filename, original object/TU membership and natural root layout stay UNKNOWN.

~~~powershell
python tools/promote_asm.py --manifest evidence/reconstructed-asm/batch-0002.json --verify-only
python tools/promote_asm.py --manifest evidence/reconstructed-asm/batch-0002.json --promote
python tools/census.py --write
python tools/census.py --check
python tools/hybrid_image.py --write
python tools/hybrid_image.py --check
~~~

The promotion tool runs the actual shared regression receipt, checks unchanged
inputs, replays the complete batch again, and publishes source/proofs/ledger
atomically. The supervisor is the only publisher.


## Frameless audio entries: batch 0004

`audio_frame_calibration.py` rederives FRAMELESS_ENTRY from hash-bound canonical
C sources/proofs and fresh pinned 3.6a controls. The measured corpus has 272
ordinary exact C entries, two complete-C entries and four behavioral C entries.
Behavioral C contributes only its bound entry instruction to this measurement;
it remains BEHAVIORAL_C, never an exact C match.

The four control functions cover an empty void leaf, constant-return leaf,
void store with no locals and six register variables live across a named C call.
Each is compiled under default, +D, +X3, +x3, +x3,5 and +L: 24 LINK A5 entries,
with UNLK A5 before every RTS. All accepted 3.6a profile option sets must occur
in this matrix; an added profile without a control rejects. A frameless entry
in any canonical C entry or available control rejects the calibration. Pinned
5.0a default/-ps, 3.20a and 3.6b ROM observations agree (the ROM uses A6).
The older supplemental jobs are observations, not required premises; unavailable
retained artifacts are reported as unavailable, while changed available pins
reject. No general claim about every C compiler or original source is made.

A span needs independent entry evidence and its own fully decoded CFG. Its entry
must not be LINK, all instructions must be reachable, at least one path must
reach RTS/RTE, and no reachable path may execute LINK/UNLK or leave an unproved
boundary. Edges are regenerated from instructions; supplied edges cannot conceal
a frame. A compiled LINK-framed C function is an explicit rejection control.
The prior register, CCR-X and A4 predicates remain unchanged.

| H0 half-open span | Candidate CODE bytes | Independent entry |
| --- | ---: | --- |
| 5594..559E | 10 | Direct JSR from 53E6 at 53EA |
| 55D6..5646 | 112 | SDK SetIntVector registration in 50E8 |
| 5646..56B6 | 112 | SDK SetIntVector registration in 50E8 |
| 56B6..5726 | 112 | SDK SetIntVector registration in 50E8 |
| 5726..5796 | 112 | SDK SetIntVector registration in 50E8 |
| 5868..58BC | 84 | Direct JSR from 50E8 and 53E6 |
| 615E..617C | 30 | SDK AddIntServer registration in 50E8 |

All seven complete mnemonic source objects and named fields verify exactly,
totaling 572 RECONSTRUCTED_ASM candidate bytes and zero DATA/BSS/COMMON credit.
The fresh producer is `build/worker-jobs/sol-audio-score-frameless0004-001`:
50 successful guest commands, with complete request/result/artifact pins in
`evidence/reconstructed-asm/batch-0004.json`. Sources are under
`evidence/rules/asm-reconstructed/batch-0004/`. Promotion remains the supervisor's
step; these curated candidates do not themselves grant ownership.

The cbwrap one-past label at 617C names the independently proved callback entry
for its short BSR. It owns zero bytes and does not export a second definition
of that callback. Its export has `original: null`, so the canonical pointer
registry cannot credit a one-past CODE entry. Owner, filename, original object/TU and natural layout remain
UNKNOWN. Diagnostic binders, scalar allocations and linker alignment own no
original game DATA or CODE.

558A, 57C0..57E4 and 5CC2/5D74/5D80 remain unresolved: no independently proved
entry/consumer was established. Adjacency and a relocated pointer alone do not
supply one. Canonical ASM ownership also does not yet make 53E6's C unit usable:
`check_unit` lacks a reconstructed-ASM dependency recipe and still reports
`unrecovered same-node dependency: resident_F_5594`. The next experiment is a
provider recipe that links the complete proved ASM objects under the C unit's
mechanical names and checks every physical named binding. No C stub substitutes.

```powershell
python tools/promote_asm.py --manifest evidence/reconstructed-asm/batch-0004.json --verify-only
python tools/promote_asm.py --manifest evidence/reconstructed-asm/batch-0004.json --promote
```

The publisher runs the unchanged shared regression gate and rechecks all input
pins before atomic publication. Only after publication should the supervisor
refresh census/boundaries and hybrid accounting.

## Canonical reconstructed-ASM dependencies in C units

The ordinary `check_unit` separate-object route can retain complete canonical
reconstructed-ASM objects beside its C contribution. `reconstructed_asm_dependencies`
is a distinct recipe in the compiler identity and unit receipt; ASM is never a
C member, never a C stub, and earns no new ownership from the caller proof.
Accepted source, fact, proof, pinned producer graph and complete assembled object
are bound separately. The existing reconstructed-ASM comparison is replayed at
acceptance and canonical reads; the new link checks every export, ordinary byte,
named PC/long field and relocation. Short transfers to one-past labels require
the independently accepted next object at the actual linked boundary.

Only compatible resident 3.6a separate-object trials are supported. C members
retain the ordinary exact comparator and mechanical external-runtime harness
bindings. The complete typed 6200 selector provider and its complete score support
objects can be retained too, with no new typed-data or instruction credit. Its
physical symbol must remain in CODE. Historical object/TU membership and natural
root layout remain unknown. Use `check_unit` explicitly; a unit missing the ASM
recipe rejects rather than accepting a synthetic C dependency.

## Graphics register bridge: glue 4692

`glue_library_asm.py` admits only H0 4692..46CE (60 bytes). Every read
rederives the pinned C frame calibration, the independent PC-relative call at
35A4, the fully decoded contiguous save/load/vector-call/restore/RTS sequence,
and the next LINK-framed entry. The predicate requires all ten individual
32-bit stack loads (SP+36..72), D4-D6/A2-A6 preservation, A6 graphics base,
and the independently pinned SDK vector -636/register map. An ordinary framed
C call, missing entry, changed load, clipped span or different vector rejects.
No adjoining entry inherits eligibility. The recursive UNCERTAIN ledger and
its conservative A4 stops stay unchanged; the separate span proof restores A4.

`evidence/reconstructed-asm/batch-glue-4692.json` pins a fresh mnemonic-only
SYS1 assembler producer. Complete AJ CODE, zero DATA/BSS/COMMON, all symbols,
the one named HUNK_RELOC32 field and complete diagnostic link rederive.
G_h01_5374 is independently named by the exact ov04_F_1E36 graphics.library
OpenLibrary assignment. Its storage is unowned. Diagnostic scalar storage,
RTS and link alignment earn no credit. Library member, author, historical
filename, source provenance, object membership and natural layout are UNKNOWN.
The route is RECONSTRUCTED_ASM, never PINNED_RUNTIME or RECOVERED_ASM.

The existing `reconstructed_asm_dependencies.py` recipe links the unchanged
complete canonical object at its exported mechanical entry. The fact supplies
its prefix, entry export and independently named external DATA identity. All
source/proof/producer pins, complete linked bytes and exhaustive named base
relocations use the general route above. An export already spelled with the
mechanical name reuses the checked physical symbol without a duplicate alias.
No additional compiler, queue or C acceptance mechanism is introduced.
`promote_asm.py` dispatches this manifest to the glue predicate and retains its
existing stage, overlap check, shared gate and atomic publisher.

The sprite caller 34E0 stays ordinary C. The retained candidate is
`evidence/rules/glue-caller/resident_F_34E0.c`. Use aztec36-large-data (+D),
separate objects, and the unchanged canonical 33E6 member. Its ordinary C unit
owns 502 bytes (250 prior +252 new); the separate glue span owns 60 ASM bytes.

```powershell
python tools/promote_asm.py --manifest evidence/reconstructed-asm/batch-glue-4692.json --verify-only
python tools/promote_asm.py --manifest evidence/reconstructed-asm/batch-glue-4692.json --promote
python tools/check_unit.py resident_F_34E0 evidence/rules/glue-caller/resident_F_34E0.c --profile aztec36-large-data --separate-objects --per-member-profiles --isolated --no-promote
python tools/check_unit.py resident_F_34E0 evidence/rules/glue-caller/resident_F_34E0.c --profile aztec36-large-data --separate-objects --per-member-profiles
```

The supervisor publishes only after tools/tests writers are idle and the
fresh shared gate passes. This batch grants no original library-source
provenance; the caller proof grants only ordinary exact C credit.
