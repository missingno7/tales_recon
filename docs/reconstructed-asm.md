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
store wrappers558A/5594 reject both non-C predicates and remain on C.

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
