# AJ/CJ FFP fixup and DOS correlation assessment

## Finding

For the private-FFP blocker, the highest-leverage unresolved mechanism is a strict parser for Aztec AJ
external-reference records, followed by an independent linked-call binding
check. Current evidence can associate the `ov11_F_5FB2` source-generated
assembly with five private FFP helper names, but it cannot associate all seven
encoded call operands with those names. Until both object-site decoding and
link binding are proved, retain the existing `DIFFER` verdicts for the FFP
functions and do not grant call identity from helper-name presence alone.

## Measured AJ evidence and limits

The existing synthetic assembler probes used a single call to `.Fflt`, two
calls to `.Fflt`, and a one-call version with a preceding `NOP`; all assembler
steps returned zero. In the one- and two-call objects, the AJ code-size field
at `0x0C` is `6` and `10`; their code contains one and two `jsr` instructions
with 16-bit PC-relative extension words. The name trailer contains `.Fflt`
once in both objects. The one-call versus two-call comparison changes three
nearby words and grows the object by four bytes, but does not identify which
field is a count, site list, or width.

In the same-public-label NOP control, the call instruction moves by two bytes;
the code-size field changes `6→8`; only byte `0x24` among the noted nearby
fields changes (`0x11→0x13`), while the trailer remains identical. This is
evidence that byte `0x24` tracks a shifted code location. Its base, encoding,
relation to `.Fflt`, and the representation of multiple references remain
unknown. It is not enough to parse or normalize a fixup.

The production specimen `ov11_F_5FB2` is a 468-byte AJ object. Its generated
assembly contains seven helper calls: `.Fflt` at comparison offsets 28, 46,
and 76; `.Fsub` at 54; `.Fmul` at 84; `.Fdiv` at 94; `.Ffix` at 98. The AJ
trailer names all five helpers, each once, but that is name presence rather
than seven site records. The HUNK parser reads linked executable relocations;
the current object readers only check AJ/CJ signatures and selected header
size fields. They do not decode external reference records.

There is an independent gate identity map for the five original resident
entries: `.Ffix`→`h00+0x8d00`, `.Fsub`→`0x8d0a`, `.Fdiv`→`0x8d14`,
`.Fflt`→`0x8d1e`, and `.Fmul`→`0x8d28`. Each linked probe gate is ten bytes and
matches the corresponding original gate uniquely; the shared dispatcher is
not byte-identical because link-context operands differ. This supports a
narrow gate-address mapping, but the candidate final A4 displacements resolve
to the probe link's helper addresses, not automatically to the original gate
identities. The current verifier's relocation proof therefore still lacks
actual per-site external identity. See
`evidence/blockers/worker-resident-object/gate-alias-design.md` and
`evidence/blockers/worker-ffp-link/aj-fixup-audit.md`.

## Recommended bounded next step

Establish the AJ external-reference grammar with controlled, same-profile
specimens before adding production parsing. A useful test matrix should keep
the public label and assembler invocation fixed while independently varying:

- one external symbol with one and then two references;
- two distinct external symbols with one reference each, then reversed source
  order;
- a two-byte code shift before a reference, then a shift before only the
  second reference;
- a non-call external reference of a different encoded width, if supported by
  the assembler.

For every artifact, preserve raw bytes and hashes, list exact code offsets from
assembler output, and compare every changed AJ field. Require the decoded
record to predict all reference sites, widths, external names and their
relationship to code coordinates across the entire matrix. Then check that
the natural linker resolves each decoded reference to the named unique symbol
in its map and that each final linked operand equals that symbol's address.
Only after this passes should a narrowly scoped AJ parser feed the comparator.
Retain raw record bytes and explicit unknown fields in parsed output; reject
unsupported record types rather than inferring them.

Main pitfalls are confusing the instruction's 16-bit PC-relative operand with
the linker's record width; treating one interned symbol-name record as one
reference; assuming the apparent site byte is an absolute code offset; and
mistaking header counts or padding for references. A parser that passes only
the single-call case would not settle the repeated `.Fflt` case that blocks
`5FB2`. Even a sound AJ decoder is only half of the proof: the linked symbol
identity and original gate mapping remain separate obligations. Keep the
gate-only identity rule scoped to those five ten-byte entries; it does not
prove dispatcher ownership, a full `m.lib` object, or compiler-release
provenance.

No parser implementation is justified from the current receipts alone. The
existing experiment is deliberately inconclusive and avoids encoding the
plausible `0x24` site-field interpretation as fact.

## DOS correlation potential

The DOS executable is a useful secondary source-shape and semantic oracle. Its
strictly parsed image has ten overlays and a candidate census of 165 function
entries (146 closed CFG candidates). Existing strong cross-version links are
`ov10_F_2B8A`/`ov10_F_2BAC` to adjacent DOS overlay 6 routines and
`ov09_F_18D0`/`ov09_F_1924` to DOS overlay 7 routines. The evidence includes
controlled Microsoft C 5.10 object comparisons with declared external fields
and DOS relocation checks. A further `ov09_F_1956` link is only likely, and
`ov10_F_2BCA` is semantically equivalent despite a different absolute-value
implementation. These distinctions are preserved in
`evidence/dos/correspondence.json` and `docs/dos-secondary-oracle.md`.

No current correspondence identifies a DOS counterpart for either FFP-heavy
Amiga candidate `ov11_F_5FB2` or `ov05_F_3836`. For `5FB2`, the existing
candidate already has a strong source-shape hypothesis: ordinary C floating
point lowers to the observed Aztec private helper sequence, including the
104.0 immediate. For `ov05_F_3836`, a candidate reproduces the 616-byte
instruction shape, but linked A4 targets still differ. A DOS code match could
help assess shared gameplay source or semantics if a plausible counterpart
were independently located; it cannot establish Aztec AJ fixup grammar, bind
an Amiga A4 call, or prove Amiga bytes. The prior bounded ov14 DOS lookup
found no correspondence for its three queried routines, illustrating that
candidate similarity alone is weak evidence (`experiments/worker-ov14-dos-lookup/README.md`).

Given the present blocker, DOS work is secondary. If a later semantic question
arises, use a concrete Amiga candidate, locate a DOS candidate independently,
and report exact object spans and relocation/fixup identities with
non-matches. Do not use DOS to select a source expression merely because
mnemonics look similar, and do not feed DOS observations into the Amiga
function verifier.

## Evidence boundary

This assessment makes no new runtime ownership, exact library provenance,
source filename, or function-match claim. It changes no parser, comparator,
canonical recovery ledger, generated census, or fixture. The AJ/CJ grammar
remains open; DOS remains secondary evidence; FFP call-site identity remains
unproved.
