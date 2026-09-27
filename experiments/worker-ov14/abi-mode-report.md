# ov14 byte-return ABI mode check

## Finding

No documented or measured Aztec 3.6a / 5.0a compiler mode in the installed,
validated toolchain omits both signed-byte `EXT.W D0` and unsigned-byte
zeroing before `MOVE.B`. Keep `ov14_F_0412`, `ov14_F_04A8`, and
`ov14_F_0540` blocked. Their bodies remain strong C-shaped candidates, but the
current evidence supports **probable manual assembly or an unresolved compiler
variant**; it does not establish either origin.

## Documentation and option evidence

- The retained 3.6a `cc` help attempts (`build/worker-jobs/cc-help-20260919`
  and `build/worker-jobs/option-probe-20260920`) are not option listings:
  `cc ?` ends with “Open failure on input” and `cc -?` reports “illegal
  option: ?”.
- The retained 5.0a `cc -?` attempt reports invalid command-line usage and
  “Illegal option: '-?'”. The validated Aztec1 `readme` only redirects to
  `df0:read.me`; it documents no return convention.
- The validated 3.6a media manifests expose `iff/README` and `lint/readme.lint`
  as documentation-like files, not compiler option manuals. The validated
  5.0a manifests likewise contain no compiler option manual. Do not treat
  documentation listed only on the rejected 5.0a disk 3 as validated evidence.
- The recorded compiler profiles are `aztec36` (no flags), `aztec36-x3`
  (`+X3`), `aztec36-large-data` (`+D`), `aztec36-long` (`+L`), `aztec50`
  (no flags), and `aztec50-short` (`-ps`), as declared in
  `tools/compiler_oracle.py`. This was a review of the existing matrix, not a
  flag search.

## Fingerprint matrix

`evidence/fingerprints/index.json` contains isolated return probes for every
recorded profile:

| Return case | 3.6a default, `+X3`, `+D` | 3.6a `+L` | 5.0a default | 5.0a `-ps` |
| --- | --- | --- | --- | --- |
| signed `char` / `int` from `char` | `MOVE.B; EXT.W D0` | `MOVE.B; EXT.W D0; EXT.L D0` | `MOVE.B; EXT.W D0; EXT.L D0` | `MOVE.B; EXT.W D0` |
| `unsigned char` | zero D0, then `MOVE.B` | zero D0, then `MOVE.B` | zero D0, then `MOVE.B` | zero D0, then `MOVE.B` |
| `long` from `char` | `EXT.W D0; EXT.L D0` | same | same | same |

The profile flags change other details or preserve the same fingerprint, but
none produces the target's plain final `MOVE.B local,D0` followed by the
epilogue. `unsigned_int_from_char_return` also retains `EXT.W D0` across all
profiles. Fingerprint inputs include `experiments/fingerprints/char_return.c`,
`unsigned_char_return.c`, `int_from_char_return.c`,
`unsigned_int_from_char_return.c`, and `long_from_char_return.c`.

The three ov14 callees are each followed in `ov14_F_0000` by a direct
`MOVE.B D0,global` after stack cleanup, so their caller consumes the byte
result. Previous isolated tests of `void` bodies likewise omitted or changed
the final D0 load. These observations make a void/no-return explanation
unlikely, without proving the original source language or exact signature.

## Disposition

Keep the shared `BYTE_RETURN_ABI_MISMATCH` blocker and its ownership unchanged.
Do not select a compiler release or assign assembly ownership from this result
alone. Reopen when a provenance-backed toolchain fingerprint reproduces the
byte-return epilogue, or when independent source-language evidence identifies
these routines as assembly.
