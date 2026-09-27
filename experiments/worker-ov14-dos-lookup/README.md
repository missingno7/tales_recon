# ov14 DOS secondary-oracle lookup

## Result

The existing DOS census and a bounded run of the existing cross-probe do not
identify corresponding DOS implementations for `ov14_F_0412`, `ov14_F_04A8`,
or `ov14_F_0540`. Evidence is inconclusive about shared C versus
platform-specific code. This lookup does not affect the Amiga Aztec proof gate.

## Evidence

- `evidence/dos/correspondence.json` has no link for any of the three ov14 IDs.
  Its seven existing links cover ov09/ov10, ov07 and other functions; the one
  ov14 cross-probe reference is `ov14_F_03C2`, a different routine.
- The DOS function census contains 165 heuristic candidates across overlays.
  It has multiple closed candidates in the 120–220 byte range, including
  146-, 151-, 157-, 167-, 177-, 198-, and 216-byte bodies. Their entry evidence
  is generally a BP-frame pattern, which does not establish semantic
  correspondence.
- Ran the existing `tools/dos_cross_probe.py` on the best current Amiga C
  candidates under both recorded DOS profiles (`msc500` and `msc510`, default
  `/AM /O /Gs`). The compiler produced code sizes 108 bytes for 0412, 124 for
  04A8, and 156 for 0540 in both profiles. None had an exact occurrence in the
  DOS executable.
- The top mnemonic-shape suggestions were low: 0412 ranked
  `dos_ov08_F_5732` at 0.6667 (95 bytes), 04A8 ranked `dos_ov08_F_2FB3` at
  0.5714 (61 bytes), and 0540 ranked `dos_ov08_F_2F42` at 0.5607 (113 bytes).
  These scores do not support shared-source claims.

## Interpretation

The DOS census supplies candidate code regions but no labels or semantic
ownership. The cross-probe supplies neither exact bytes nor convincing shape
agreement for this trio. This does not prove platform divergence: the Amiga
candidate declarations/layout and DOS compiler conventions could differ from
the historical DOS source. Retain the Amiga `BYTE_RETURN_ABI_MISMATCH`
blockers and make no DOS correspondence claim.

Full bounded probe output: `cross-probe.json`.
