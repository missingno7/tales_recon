# resident_F_8B76 call-contract audit

This is a read-only interpretation of immutable disassembly evidence; it does not rename canonical symbols or alter any recovery source.

## Contract

`resident_F_8B76` is 18 bytes at resident CODE offset `0x8B76`. Its complete entry sequence is:

```asm
movea.l  $4(a7), a1
movem.l  $8(a7), d0-d3
movea.l  -$2c8a(a4), a6
jmp      -$132(a6)
```

At the call boundary, the return address occupies `[SP]`. The stub loads argument 1 from `[SP+4]` into A1, then four 32-bit stack slots from `[SP+8]` through `[SP+20]` into D0-D3. Thus the call contract is one pointer-like argument followed by four scalar arguments. The `graphics.library/RectFill` autodoc names this exact vector operation and ABI: `RectFill(rp,xmin,ymin,xmax,ymax)`, with `rp` in A1 and coordinates in D0:16, D1:16, D2:16, D3:16 ([official autodoc](https://developer.amigaos3.net/autodocs/graphics.library/RectFill.html)). The caller slots are 32-bit C call slots; the API consumes the low 16-bit `SHORT` coordinates.

The only two direct callers in `evidence/functions/ledger.json` are:

| Caller and callsite | Push sequence (right-to-left) | Recovered formal order |
|---|---|---|
| `ov08_F_1D42`, `0x1D7C` / absolute hunk offset 7548 | 199, 319, 168, 0, `G_h01_46CA` | `rp=G_h01_46CA`, `xmin=0`, `ymin=168`, `xmax=319`, `ymax=199` |
| `ov11_F_27CC`, absolute hunk offset 10316 | 199, 319, sign-extended local word, 0, `G_h01_46CA` | `rp=G_h01_46CA`, `xmin=0`, `ymin=local`, `xmax=319`, `ymax=199` |

The target callsites each clean exactly `0x14` stack bytes after the call. The ov08 instruction window starts at 7530 (`PEA 199`, `PEA 319`, `PEA 168`, `CLR.L`, `MOVE.L G_h01_46CA`) and ends at 7552 (`LEA 0x14(A7),A7`). The ov11 caller independently has `PEA 199`, `PEA 319`, sign-extends its 16-bit local into a long slot, pushes zero and `G_h01_46CA`, then makes the same call and cleanup. No recovered C source currently calls `F_h00_8B76`; both callers remain disassembly-only.

## Library-base binding

The stub’s A4 displacement resolves to root DATA offset `0x5374` (`32766 - 0x2c8a = 0x5374`), recorded as A4-relative reference hunk 1 / offset 21364. The game itself binds that global to the named library: in `ov04_F_1E36` at hunk-4 offsets 7738–7750, it pushes zero and the PC-relative string at offset 9518 (`graphics.library`), calls resident stub `resident_F_89D0`, then stores D0 to absolute DATA address `0x5374`. The referenced string and assignment are both recorded in the immutable function ledger for `ov04_F_1E36`. This proves that the base used by `resident_F_8B76` is the result of opening `graphics.library` in this game. The executable string table also records the adjacent diagnostic text “InitAV: cannot open graphics library” at hunk 4 / offset 9535.

This identifies the called API/library name, while leaving the exact installed library binary/release unproven. Adjacent wrappers corroborate the family: `resident_F_8B4C` uses the same base and vector `-$F0` (Move), `resident_F_8AA8` uses `-$F6` (Draw), and `resident_F_8B88` uses `-$156` (SetAPen).

## Why the prior A4 byte mismatch is not a separate identity failure

In the isolated ov08 report, the first raw difference was at `0x6`: the original A4 displacement was `-$2c8e`, while the candidate emitted `-$7fb2` for its reference to `G_h01_5370`. That reference is a different global from the library base (`G_h01_5374`). The compiler harness explicitly gives mechanical external names natural candidate DATA layout; names carry identity, not historical placement (`tools/compiler_oracle.py`, `harness`). `function_compare.py` maps a mechanical `G_h01_5370` name back to original hunk 1 / offset `0x5370`, and normalizes A4 operands only when the entire instruction layout matches. Since the earlier `F_h00_8B76` argument-shape error changed instruction layout, the prior comparison could not reach that A4 identity proof (`same_layout` guard in `function_compare.py`). The `-$7fb2` encoding therefore reflects candidate-local placement; it is not evidence that the historical global at `0x5370` was mislabeled.

## Recommendation

For any future source hypothesis, declare `F_h00_8B76` as an old-style five-argument call and pass the `G_h01_46CA` value first, then the four coordinate values. The likely API-level declaration is `RectFill(rp, xmin, ymin, xmax, ymax)`; retain the mechanical symbol `F_h00_8B76` in reconstructed source unless a separate provenance policy approves a semantic wrapper. The call’s five-slot contract, `graphics.library` base binding, and API-level vector name are now independently supported; do not spend another compilation merely to re-prove them.
