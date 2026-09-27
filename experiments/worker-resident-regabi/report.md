# Resident FFP call gates for ov11_F_5FB2

Scope: read-only comparison of immutable executable/function evidence with the installed Aztec 3.6a source/archive. No source or recovery ledger changed. `references.json` records the wrapper extents, caller references, and nearby call-site instructions captured from `evidence/functions/ledger.json`.

## Wrapper map

The five resident entries are consecutive 10-byte stubs beginning at hunk 0 offsets `0x8D00`, `0x8D0A`, `0x8D14`, `0x8D1E`, and `0x8D28`. Each stub pushes a long negative vector offset onto the stack, then jumps to the shared dispatcher at `0x8D32`. The shared tail continues through `0x8D80` and returns. The mechanical function census records all five extents as `UNCERTAIN` with ownership `UNKNOWN`, because each entry shares the dispatcher tail.

| Mechanical entry | Pushed vector | Matching Aztec FFP helper | 5FB2 register use |
| --- | ---: | --- | --- |
| `resident_F_8D00` | -30 | `.Ffix` | D0 input / D0 result |
| `resident_F_8D1E` | -36 | `.Fflt` | D0 input / D0 result |
| `resident_F_8D0A` | -72 | `.Fsub` | D0, D1 inputs / D0 result |
| `resident_F_8D28` | -78 | `.Fmul` | D0, D1 inputs / D0 result |
| `resident_F_8D14` | -84 | `.Fdiv` | D0, D1 inputs / D0 result |

These mappings come from the immediate pushed in each executable stub and the independently present Aztec 3.6a `_LVOSP*` equates in `Library Source/ffp.arc` (`_LVOSPFix=-30`, `_LVOSPFlt=-36`, `_LVOSPSub=-72`, `_LVOSPMul=-78`, `_LVOSPDiv=-84`, lines 449–458). The FFP archive source contains the corresponding private helper stubs `.Ffix`, `.Fflt`, `.Fsub`, `.Fmul`, and `.Fdiv` (around lines 151–196 and 270–300).

## ABI and source comparison

The resident stub shape matches the Aztec helper pattern: push a library vector offset and jump to a shared FFP dispatcher. In Aztec's source, `.Ffix` and the other `.F*` entries push their `_LVOSP*` value and jump to `amiga_ffp` (`ffp.arc`, around lines 151–207). That dispatcher lazily opens `mathffp.library`, saves D0/D1/A0/A1 while opening it, restores them, loads the library base into A6, performs the vector call through `(A6,A0.L)`, restores A0/A6, and returns (`ffp.arc`, lines 207–247). The executable's shared tail has the same operation order and its code references the candidate strings `mathffp.library` and `no math library`; the base operand is an A4-relative global at `0x33D4`, rather than the source listing's `_MathBase` spelling.

The installed `SYS1/lib/m.lib` archive (SHA-256 `545e585fe6f40422b6ba969922d15d0e0e426fa32f0ad2b2b8241b49f95309f2`) contains the symbol strings `.Ffix`, `.Fflt`, `.Fsub`, `.Fmul`, `.Fdiv`, `amiga_ffp`, `_MathBase`, and their `_LVOSP*` names. The source listing is SHA-256 `9d676eac450df510f4f0283a58d78585223b28d5d7879dd973218a671c85f24e`. This is a strong historical library-source/archive signature, but I did not verify the resident bytes against one exact archived object contribution or relocation set.

Aztec 3.6a also has a different, ordinary C-call interface. In `ffp.arc`'s `sp.a68` section, public `_SPFix`/`_SPFlt`/`_SPSub`/`_SPMul`/`_SPDiv` wrappers load their parameters from `4(sp)` (and `8(sp)` for the second argument) before jumping to the library vector (around lines 697–768). The `amiga_math` gateway likewise moves stack arguments to D0/D1. Those public wrappers do not match 5FB2's call sites. The `.F*` names are compiler-runtime helpers with register arguments; they are the plausible natural C origin here when ordinary C floating-point expressions are lowered by Aztec. No explicit `#pragma regcall` is needed for those compiler-generated helper calls.

In `ov11_F_5FB2`, the observed sequence is consistent with this lowering: `.Fflt` at `0x5FCE` and `0x5FE0`; `.Fsub` at `0x5FE8` with the two FFP values staged into D0/D1; `.Fflt` at `0x5FFE`; `.Fmul` at `0x6006`; `.Fdiv` at `0x6010`; and `.Ffix` at `0x6014`. The earlier integer candidate and explicit ordinary calls to mechanical `F_h00_8Dxx` names do not model this ABI. A C candidate using the right floating-point types/operations could naturally produce the register sequence through Aztec's private helpers, subject to exact compiler verification.

## Callers and classification

The current census records 119 calls to these five entries across eight distinct overlay functions: `ov05_F_0000`, `ov05_F_131C`, `ov05_F_1860`, `ov05_F_1EFC`, `ov05_F_2CD4`, `ov05_F_318E`, `ov05_F_3836`, and `ov11_F_5FB2`. Per-entry site counts are 56, 11, 4, 36, and 12 in table order. In the target function, these are A4-relocated resident call stubs, not same-overlay PC-relative calls.

Classification: likely historical Aztec/Manx FFP helper assembly, or a game-linked/copy-derived version of that helper assembly. The exact vector set, stub pattern, dispatcher sequence, and strings make the FFP identity strong. The source and archive comparison do not prove that the bytes came from a specific `m.lib` object, so executable ownership should remain `UNKNOWN` until the exact linked contribution is established. This is not evidence for a compiler-generated C function body in the shared dispatcher; the dispatcher and vector stubs are assembly-shaped runtime glue. The *call sites*, however, are compatible with ordinary C floating-point source lowered into Aztec's register-based `.F*` runtime helpers.
