# ov11_F_5FB2: floating-point reconstruction experiment

Scope: isolated compiler-shape experiment only. No canonical source, blocker ledger, recovery ledger, or promotion was changed. All verifier calls used `check_function.py --batch ... --isolated --output-dir experiments/worker-ov11-5fb2-ffp/checks --json`.

## Best plausible C

Candidate: [cast_each_104.c](cast_each_104.c). Its key expression is:

```c
x = ((float)G_h01_94BE - (float)p->value)
    * (float)p->child->value / 104.0;
```

This is the strongest match to the original operation order. The original loads `G_h01_94BE` (word, sign-extends, `.Fflt`), loads `p->value` at +0x2c (word, sign-extends, `.Fflt`), calls `.Fsub`, then loads `p->child->value` at +8, calls `.Fflt` and `.Fmul`, divides by immediate FFP value `0xd0000047` (104.0), and calls `.Ffix` before storing the result as a 16-bit local. This C expression compiles to the same helper-call order and exact 104.0 immediate. The casts must be on each subtraction operand: `(float)(G_h01_94BE-p->value)` instead emits an integer `sub.w` before `.Fflt`, which is observably different.

Other original evidence retained in the candidate: `p=G_h01_8BEC+a` with a 0x34-byte record stride; `p->value` offset 0x2c; child pointer offset 0x22 and child value offset 8; locals `x` and `y` are words at A5-6 and A5-8. The remainder models the observed integer condition and global updates.

## Isolated verifier result

Best candidate receipt: `BLOCKED / COMPILE_ERROR` (not an equality or mismatch result).

- Expected function length: 206 bytes; actual linked function: unavailable (`actual_length: null`).
- Compiler and assembler succeeded. Link failed because the harness links `c.lib` only and the candidate references the five Aztec private floating helpers: `.Fflt`, `.Fsub`, `.Fmul`, `.Fdiv`, `.Ffix`.
- Receipt/cache key: `2b6507a5859635804ea83d7b3b23a95ea85a680c9a6bf28611b73d2008440a35`.
- Source SHA-256: `95dc8eb042af0ee0b8ddd0d6632686be84dce595fee6e92b80dd01364f45fbe6`.
- Linker reports `Undefined symbol: .Fflt`, `.Fsub`, `.Fmul`, `.Fdiv`, `.Ffix`.
- No generated-byte comparison or relocation comparison was possible; consequently there is no first-byte mismatch to report. This must not be interpreted as `EQUAL`.

The compiler-generated assembly is in `build/compile-cache/2b6507a5859635804ea83d7b3b23a95ea85a680c9a6bf28611b73d2008440a35/t000.asm`. Its central sequence is `.Fflt, .Fflt, .Fsub, .Fflt, .Fmul, immediate #$d0000047, .Fdiv, .Ffix`, with operand loads and D0/D1 staging corresponding to the original. Symbols remain absolute in this pre-link assembly, so it does not establish final A4-relative relocations.

The installed `toolchain/installed/aztec-3.6a/SYS1/lib/m.lib` contains these private helper symbols; `compiler_oracle.py` currently links only `c.lib`, and `check_function.py --isolated` has no per-candidate library override. Thus the precise blocker is unavailable helper-library resolution in the verifier, before code bytes and HUNK relocations can be compared—not evidence that the source shape is wrong. The required future discriminating run is an isolated compile/link using the same pinned Aztec objects plus `m.lib`, followed by exact code and relocation comparison. Do not promote unless that comparison succeeds.

## Focused hypotheses tried

- `cast_each_104`: compiler and assembler succeed; helper sequence and 104.0 immediate align; link blocked by missing `.F*` symbols.
- `cast_after_integer_sub`: compiles integer subtraction before conversion and omits `.Fsub`; link blocked by the remaining `.F*` helpers. Rejected as a shape match.
- `named_float_temporaries_104`: compiler materializes three float temporaries, then emits `.Fsub/.Fmul/.Fdiv/.Ffix`; link blocked by missing helpers. Less economical and uses extra local storage, so weaker than the direct expression.
- Earlier 45.0 literal candidate was discarded: it emitted FFP `#$b4000046`, while the original literal is `#$d0000047` (104.0).
- Earlier `45.0f` spelling was rejected by Aztec 3.6a parser (error 69, missing semicolon); use unsuffixed `104.0`.

No semantic similarity was counted as a match and no original bytes were supplied to generated output.
