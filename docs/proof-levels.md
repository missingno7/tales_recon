# Reconstruction proof policy

Evidence extraction is not source reconstruction. `current_proof_level: null`
means no reconstructed artifact has met a source-match level. A topology census
cannot be promoted to HUNK_CONTENT_MATCH by copying the oracle.

| Level | Required evidence |
| --- | --- |
| SEMANTIC_ONLY | Readable source with documented behavioral evidence |
| CODEGEN_SIMILAR | Pinned compiler experiment and measured similarity |
| FUNCTION_CODE_MATCH | Complete function bytes and independently resolved relocations |
| MODULE_CODE_MATCH | Complete module routines, padding and data contributions |
| DATA_LAYOUT_MATCH | Typed objects reproduce measured sizes, offsets and references |
| HUNK_CONTENT_MATCH | All initialized content independently produced |
| HUNK_RELOCATION_MATCH | Complete relocation sites, types, targets and addends verified |
| OVERLAY_NODE_MATCH | Complete node's content, allocations, ordering and references from normal linking |
| ROOT_LAYOUT_MATCH | Resident contributions and allocations arise from normal linking |
| LINKED_HUNK_LAYOUT_MATCH | Whole linked topology emerges from modules, object order and toolchain rules |
| EXECUTABLE_MATCH | Executable structure/content matches under an explicit comparison policy |
| WHOLE_FILE_MATCH | Every file byte matches; independent provenance and natural build also demonstrated |

These are separately assessed obligations, not interchangeable percentages.
Semantic meaning, generated-code equality and exact historical source text are
separate claims. No original source spelling or filename is assumed recovered.
No per-function ORG, placement scripts, original-code fallback, carrier runtime,
or post-link patching may satisfy the final reconstruction proof.

Runtime ABI ownership is not exact library object provenance. A known Manx
trampoline may be classified as runtime glue while the producing linker version
and library object remain unknown. All other ranges retain unknown ownership
until supported by independent evidence.
