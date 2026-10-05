# Reconstruction proof policy

Evidence extraction is not source reconstruction. `current_proof_level: null`
means no aggregate reconstructed executable proof has been established.
Individual contribution proofs are recorded separately in `recovery/ledger.json`
and summarized by `highest_individual_contribution_proof`; they do not establish
complete overlay or executable reconstruction. A topology census cannot be
promoted to HUNK_CONTENT_MATCH by copying the oracle.

| Level | Required evidence |
| --- | --- |
| SEMANTIC_ONLY | Readable source with documented behavioral evidence |
| CODEGEN_SIMILAR | Pinned compiler experiment and measured similarity |
| FUNCTION_CODE_MATCH | Complete function bytes and independently resolved relocations |
| FUNCTION_WITH_DATA_MATCH | Complete function bytes plus an independently proved, contiguous compiler-owned CODE-data contribution |
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

The function grinder grants FUNCTION_CODE_MATCH only for a complete closed
contribution. Proven external address fields may be normalized through independent
symbol/relocation identities in the comparison buffer. This does not prove the
data objects' contents, allocation order, or whole-overlay layout. Its canonical
ledger is `recovery/ledger.json`; generated topology metrics validate those proofs
before counting reconstructed bytes. See `docs/grinder-pipeline.md` for the API,
unsupported cases, and reserved stronger states.

A complete unit may introduce several new members at once (`check_unit.py
--member`), for example a same-node call cycle in which no member can be proved
first. Acceptance is the whole unit. The object is bounded by its own ordered
linked symbols. Every member must pass the exact comparison, and every
intra-unit call must resolve to the right member. Every linked byte must belong
to a member, and original gaps stay unclaimed. Promotion writes proofs for all
new members or for none of them. Each proof names the shared unit
receipt, which records each member's source hash. Census validation rejects the
receipt unless every listed member is canonical with that source.

The opt-in `--natural-interval START..END` mode links every function of an
original interval in address order. Canonical functions keep their canonical
sources and must stay EQUAL. Unknown gaps are not linked, so the object is
compacted only at those spans. A PC-relative reference crossing a span is
accepted by target identity only when its displacement class (8-bit or 16-bit)
is the same in the original and compact links. Otherwise the unit is BLOCKED
(`GAP_DEPENDENT_ENCODING`). See docs/NEXT.md.

With `--separate-objects`, `--object-group` compiles consecutive members, with
no original byte between them, as one ordinary object. This is a
translation-unit hypothesis with the same exact acceptance. It is never
source-file provenance. The promotion evidence check re-derives each object
source from the retained unit parts.

FUNCTION_WITH_DATA_MATCH additionally requires every PC-relative literal to be
separately evidenced, an exact source-produced CODE tail, and a boundary at the
next discovered function entry. It claims that literal contribution only; it does
not establish a complete module or overlay layout.

Runtime ABI ownership is not exact library object provenance. A known Manx
trampoline may be classified as runtime glue while the producing linker version
and library object remain unknown. All other ranges retain unknown ownership
until supported by independent evidence.
