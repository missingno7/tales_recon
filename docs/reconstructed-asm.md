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
