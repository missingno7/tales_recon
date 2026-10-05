# Pinned Aztec m.lib vs resident FFP gate bytes

Read-only evidence comparison. No canonical reconstruction source, recovery ledger, blocker ledger, or verifier normalization was changed. A tiny unrelated C probe was compiled and naturally linked with the pinned Aztec 3.6a `c.lib` plus `m.lib` to make the linker select the private helper contributions. It used only generated C (`probe.c`) and did not consume original executable bytes. The final comparison was performed afterward against immutable `evidence/functions/ledger.json` evidence.

## Selected contribution and identity

Pinned archive: `toolchain/installed/aztec-3.6a/SYS1/lib/m.lib`, SHA-256 `545e585fe6f40422b6ba969922d15d0e0e426fa32f0ad2b2b8241b49f95309f2`.

Link identity: Aztec 3.6a, no compiler flags, normal `c.lib` plus additional `m.lib`; link recipe `harness.o +o1 candidate.o +o0 c.lib m.lib; -m -t`. Worker/cache receipt is in `build/compile-cache/3f09afe5b637d40ba2ed2c690e8d5a2a3723507126a8e55c78c0a1032a530046/receipt.json`; linked executable SHA-256 `a32bf85392742817a2ae5c026f397e05093997d47b5bdfe12f74f3988ac930e4`.

The selected resident CODE symbols in that link are `.Ffix=0x810`, `.Fsub=0x81a`, `.Fdiv=0x824`, `.Fflt=0x82e`, `.Fmul=0x838`, and `amiga_ffp=0x842`. These line up with original hunk-0 offsets `0x8d00`, `0x8d0a`, `0x8d14`, `0x8d1e`, `0x8d28`, and `0x8d32` by function order and 10-byte stub spacing.

## Exact comparison

The five 10-byte `.F*` call gates match the resident bytes exactly: generated HUNK0 `[0x810,0x842)` equals original `[0x8d00,0x8d32)`. The full 130-byte region does not match. The generated range SHA-256 is `946d70ab8df7fbe4bc3dd729bd52e1e17ad29b9b283cd122bc0031d373ab8700`; original wrapper record SHA-256 is `679cf4b52b2c52c96a840cc740fba507cbaad79f7bf35fd97728b178a7d236c2`.

First difference is at original absolute hunk offset **0x8d34** (byte 52 from `0x8d00`), compared with generated HUNK0 offset `0x844`: original byte `33`, linked m.lib byte `80`. This is the high byte of the `_MathBase` A4 displacement: original instruction `tst.l $33d4(a4)` (`4aac33d4`) versus linked `tst.l $8084(a4)` (`4aac8084`). The different A4 displacement is expected from the unrelated probe's DATA/BSS layout and A4 anchor; it prevents direct byte equality.

There are 14 changed bytes total, all seven 16-bit address operands; all instruction opcode/shape bytes otherwise match. Operand fields are:

| Original operand location | Original value | Generated link value | Meaning |
| --- | --- | --- | --- |
| `0x8d34..35` | `33d4` | `8084` | `_MathBase` in `tst.l d16(a4)` |
| `0x8d44..45` | `fc90` | `ff6e` | PC-relative `__OpenLibrary` call |
| `0x8d4a..4b` | `33d4` | `8084` | `_MathBase` in `move.l d0,d16(a4)` |
| `0x8d5a..5b` | `f994` | `feda` | PC-relative `__Output` call |
| `0x8d60..61` | `f9ba` | `006c` | PC-relative `__Write` call |
| `0x8d64..65` | `f7a6` | `003e` | PC-relative `__abort` call |
| `0x8d76..77` | `33d4` | `8084` | `_MathBase` in `movea.l d16(a4),a6` |

The linked targets are identified in `t000.sym`: `__OpenLibrary=0x7c2`, `__Output=0x744`, `__Write=0x8dc`, `__abort=0x8b2`, `_MathBase` is in BSS at `0x82`. The original disassembly targets are `__OpenLibrary`-path call `0x89d4`, `__Output` `0x86ee`, `__Write` `0x871a`, `__abort` `0x850a`, and `_MathBase` at A4 displacement `0x33d4`. The PC-relative calls therefore reflect different runtime symbol placement in the test link, not a different call sequence.

Both loaded HUNK0 comparison ranges have no HUNK relocation records: original wrapper evidence reports an empty relocation list, and parsed generated HUNK0 has none intersecting `[0x810,0x892)`. This only compares post-link loaded-image relocation records; it is not a proof that the original and archive object-file relocation entries are identical. The generated linker has already resolved these A4 and PC-relative operands.

## Classification

Evidence supports exact identity of the five 10-byte vector gates and a matching 80-byte dispatcher instruction pattern, with the dispatcher’s seven context-dependent address operands resolved differently in this natural but unrelated link. The exact original/archive **complete object bytes and object relocation set are not established**: `m.lib` was observed through its selected final linked contribution, not extracted as a standalone object with unresolved relocations. Therefore this demonstrates a strong Aztec FFP ABI/source signature, not exact runtime object provenance. Preserve `UNKNOWN` ownership; do not create a complete-object alias from this result.

A meaningful future discriminant, if exact provenance is still required, is a format-aware extraction of the relevant `m.lib` member before link and comparison of its relocation records against an independently recovered original link-object contribution or symbol-resolved build context. Re-linking this probe alone cannot establish that identity because its A4 and runtime symbol placement are different.
