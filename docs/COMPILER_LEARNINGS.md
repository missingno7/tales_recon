# Compiler learnings: Manx Aztec C 3.6a (Amiga)

This is the one page to read before writing candidate C. Every line is a rule that has paid off or a trap that cost trials.
Tags:
- ✔ verified (an exact match or measured control)
- ? hypothesis
- ✗ dead end; do not retry

Evidence shorthand:
- `FP` = evidence/fingerprints/index.json and evidence/rules/fingerprints/*.c (49 programs × 6 profiles)
- `BJ` = docs/blockers.json
- `N§k` = item k of the retired handoff, read it with `git show 4534341:docs/NEXT.md`
- `LS` = the worker lessons appendix at the end of this page (formerly shipped in every fleet packet)

## Pick the profile first
- ✔ `$xxxx.l` DATA operands with RELOC32 mean `aztec36-large-data` (+D). `d16(a4)` data means `aztec36`. Jump-slot calls are not data. A unit can mix both (`--per-member-profiles`). (FP, N§7)
- ✔ A4 = H1 + 0x7FFE, so a global at H1+0x28 is `0x802A(a4)`. (FP)
- ✔ Game code uses default flags. The runtime library (format, startup `_main`, CLI parser) was built with +X3, which merges adjacent call cleanups into one `addq`. (N§8/§10)
- ✔ 5.0a is not the game compiler: its `movem.l` is always emitted and `long*3` is inlined. 3.20a is not it either: it allocates A6/D3/D2 and uses `cmpi.l #0`. (FP, BJ resident_F_411E)

## Frame and ABI
- ✔ Every compiled C function starts with `link a5,#n`, even `#0`. The measured corpus has 272 ordinary exact C entries, two complete-C entries and four behavioral C entries. The scoped FRAMELESS_ENTRY calibration and pinned option controls live in tools/audio_frame_calibration.py; an independent entry and frame-free CFG are also required.
- ✔ No `movem` at all when nothing is saved. Register variables go to D4, D5… in declaration order (and A2, A3).
- ✔ D0–D2/A0–A1 are scratch: D2 is written unsaved in 11 canonical functions, e.g. resident_F_31AA@32D0. ? D3 and A4 preservation are unmeasured. (docs/reconstructed-asm.md)
- ✔ Arguments: all on the stack, the caller pops them with `addq.w #n,sp`. char and int are pushed as words; a char parameter is read at `9(a5)`. Parameters start at 8(a5); long and pointer are 4 bytes. Results return in D0. A returned pointer is `lea x,a0; move.l a0,d0`. (FP)
- ✔ int = short = 16 bits; long = 32. int and short are interchangeable declaration views. (docs/type-evidence.md)
- ✔ Char return: a signed char gives `move.b x,d0; ext.w d0`, a long return adds `ext.l`, an unsigned char gives `moveq #0,d0` then `move.b`.
  - The asm text says `move.l #0,d0`, but `as` emits moveq, so there is no zero-extension blocker. (FP)
  - ✗ A **bare** byte return (no ext.w) occurs only in resident_F_411E and ov14_F_0412/04A8/0540. 3.6a, 3.6b, 5.0a and every source form or option tried all widen. It needs a 3.3x/3.4x compiler. (BJ, N§1)
- ✔ Storing an int-returning call into a long adds `ext.l`. Declare the callee `long F()` and pass `1005L`. (BJ RESIDENT-WB-DECLARATION-001)

## Read the code back as C
| You see | Write |
| --- | --- |
| `tst.w g` + `beq/ble` | `if (g == 0)` / `if (g <= 0)` (compare to 0 uses tst) |
| `bcc/bcs/bls` | unsigned comparison (`bls` on a counter that starts at 0 means unsigned `c > 0`) (LS) |
| branch / `moveq #1` / `bra` / `moveq #0` | a boolean expression (no Scc is ever emitted) |
| `bra` to a bottom test | `for`/`while` loop. `while(n--)` = `move.w n,d0; sub.w #1,n; tst.w d0` |
| `lsr.w` / `asr.w` | unsigned / signed `>>`. An `unsigned int` field selector gave the lsr in resident_F_01BA |
| `swap; clr.w; swap; divu.w #3; swap` | `(unsigned)long_call() % 3` (ov04_F_1AA2) |
| `jsr` to `.mulu/.mods/.divs` | long `*`, `%`, `/`, or long-index struct addressing |
| `muls.w #N`, pointer add, no `ext.l` | `((struct RecN *)&G)+i`. With `ext.l` it is `(char*)&G + N*i` (ov10_F_0000) |
| `move.b 1(a0,d0.l)` | `(char)` of an int member, i.e. its low byte (ov09_F_0000) |
| `ext.l d0; bra disp` … `dc.w` table … `jmp (pc,d0.w)` | dense `switch`: default comes before dispatch; holes in the table point at default |
| `sub.l #k,d0; beq` chain | sparse `switch` |
| `bcc` out of a switch that lands on a lone `bra` | an explicit `default: break;`. Otherwise omit an empty default (LS) |
| bare `tst` with no branch | empty `if (x) ;` (LS) |
| pointer loaded twice for `p->x` | `p->x = p->x op y`. Loaded once means `p->x op= y` (ov05_F_1EFC) |
| `move.l fn,a0; jsr (a0)` | call through a function pointer |
| `dc.b …,0` after `rts`, `lea/pea d16(pc)` | string literals: one tail per function, padded to even; `""` is a single NUL (ov03_F_0000) |
| FFP `#$86000048`-style longs | float constants (134.0); a non-commutative op evaluates its right operand into d1 first (LS) |

## Levers that move registers and evaluation order
- ✔ Locals: the first declared local gets slot -2, the next -4. Frame gaps need an address-taken struct local (ov08_F_0000) or neutral unused locals (ov10_F_0000).
- ✔ Cast the index to long before scaling. That fixed a d0/d1 role swap (ov09_F_298E, 660 B).
- ✔ Cast the pointer before adding, not after the scalar sum (ov04_F_1E36).
- ✔ A TU-local `char *` view indexed by `(long)row*21+col` beat the shared long view (ov08_F_1F4C).
- ✔ Control flow:
  - Countdowns as `if(--e->t<=0){…}else{…}`; keep post-increments and ternary arms in source order (ov08_F_1F4C).
  - Re-test the flag in each `else if` (ov10_F_0000).
  - `if(a||b){break;}` needs braces; prefer `while(cond)` over `for(;;){if…break;}` (LS).
  - Nest a switch under its outer guard (ov11_F_3B92).
- ✔ A byte local loaded via `moveq #0` is `unsigned char` (LS).
- ✗ XOR operand orientation in resident_F_463E: 15 trials across 10 families. Explicit register locals flip it but add a D4 save. (BJ)
- ✗ The "moveq mechanism" for ov08_F_1F4C does not exist: `as` emits moveq on its own. (N§6)

## Data layout
- ✔ Words and longs are even-aligned; char arrays keep odd strides (31-byte rows).
  - Example: `struct {char a,b; int n; long v;}` puts n at +2 and v at +4.
  - SDK RasInfo is 12 B and BitMap 40 B under aztec36. (docs/type-evidence.md, evidence/rules/ov04-root-abi-views)
- ✔ Placement by kind of variable:
  - Initialized data → DATA.
  - An uninitialized extern → COMMON (`global name,size`), ordered by first reference. Linking `_close` before CRT0 moves DOSBase.
  - COMMON folds into the H1 zero tail; BSS is a 4-byte sentinel. (evidence/rules/ov04-root-abi-views, runtime-vars)
- ✔ An initialized function-local `static` goes inline into dseg; an uninitialized one becomes `bss`. String literals are emitted into CODE, even under +D, and even for a TU that has only an initialized `char *` table. The intro story at H0 0018 is one. (FP, batch-0004)
- ✔ Each CODE contribution is padded to a longword with zeros. (docs/runtime-candidates.md)

## Objects, calls and linking
- ✔ `bsr.b` to a later function means **same object** (forward calls are shortened). `jsr d16(pc)` (4EBA) means separate objects in one node. Use `--object-group` only with that `bsr` evidence. (FP, N§2/§7)
- ✔ `jsr d16(a4)` (4EAC) means an A4 jump slot: an overlay→root call, or any root symbol that also has an overlay or distant (>±32 KB) caller. Every resident call to that symbol then uses the slot: `.mulu/.divs/...`, printf, wbparse, format. (N§10)
- ✔ An exported same-overlay function whose address is taken through a resident initialized pointer makes separate callers use the A4 trampoline; self-calls stay local. (evidence/rules/ov04-export-routing)
- ✔ Overlay link line: `ln -m -t -o out root.o +o1 … +o0 c.lib`. The guest shell limits arguments to 510 characters, so use `ln -f argfile`. `+ccd` puts CODE and DATA in CHIP memory. (docs/overlay-linking.md, docs/toolchain.json)
- ✔ Assembler `as`:
  - It rejects CRLF, `.b` branch suffixes and over-long `public` lines.
  - `far data` plus externs declared under `dseg` give absolute RELOC32; otherwise references are A4 shorts. (docs/reconstructed-asm.md)

## Not C or not game code: route it elsewhere
- c.lib (index/str*, segload, lmul, wbparse, printf, format, sscanf, freeseg, CRT0) and the 91 DOS/exec glue stubs are **PINNED_RUNTIME**. Call them by their exact entry; never grind them. (docs/runtime-candidates.md, N§11/§15)
- FFP 10-byte operator stubs (m.lib) link as one group; use `--with-m-lib`. (N§3)
- The audio driver is RECONSTRUCTED_ASM (register/CCR ABI, A4 reuse, no LINK). Its bytecode is TYPED_CODE_DATA. (docs/reconstructed-asm.md, docs/code-data-providers.md)

## Open unknowns
- The exact game compiler release: 3.4x would explain the four bare byte returns.
- The AJ fixup encoding.
- D3/A4 preservation.
- The XOR orientation rule.
- Original TU grouping and COMMON providers. (BJ, evidence/rules/aj-external-fixups/audit.md)

## Appendix: worker lessons (LS)

- Write plain structured C first. Canonical same-node callees, and their proven objects, are linked automatically; call them by mechanical name.
- Branches reaching a different join point usually mean another if/else-if nesting or a combined && / || condition, not a goto.
- A frame slot your locals do not explain usually means declaration order or types; an unused local is a last resort with a neutral name (never pad/filler).
- If only an A4 displacement differs, the verifier's relocation_issues name the exact global the original reads.
- Reuse canonical siblings' declaration views for shared globals. Compiler helpers (.mulu/.divs/.mods/.modu/.divu) come from C arithmetic, never declarations; in resident code the verifier routes them through A4 slots like the original.
- Aztec idioms: `lea sym(a4)` + `move.b 1(a0,d0.l)` is `(char)` of an int member (low byte); a bare `tst` with no branch is an empty `if (x) ;`; `tst/bls` on a zero-started counter is unsigned `c > 0`; a `continue` jumping back to a top test means `while (cond)`, not `for (;;) { if (...) break;`.
- More Aztec idioms: a condition re-tested in every arm (`btst` repeated) is `if ((x & 128) && (k == 1 || k == 2)) ... else if ((x & 128) && ...)`, not one outer `if (x & 128)`; `default: break;` adds a dispatch jump and an end jump, so omit an empty default; `muls.w #N` feeding a pointer add with no `ext.l` is record indexing (`(struct RecN *)&G + i` or `&arr[i]`), while `(char *)&G + N * i` adds `ext.l`.
- `beq THEN; cmp; bne SKIP; THEN: bra OUT` (a jump to a lone bra) is `if (a || b) { break; }` with braces; a bare `break;` folds into direct exits. A local stored once and never read (`clr.l -6(a5)`) is a real historical store: keep it with a neutral name.
- Float code is ordinary Aztec C on `float` (FFP) values; verify with `--with-m-lib`. Read each operator from the A4 stub the original calls: 8CD8 `.Fadd`, 8CE2 `.Fcmp`, 8CEC `.Fneg`, 8CF6 `.Ftst`, 8D00 `.Ffix` (float->int), 8D0A `.Fsub`, 8D14 `.Fdiv`, 8D1E `.Fflt` (int->float), 8D28 `.Fmul`; never guess `*` for `-`. A non-commutative op evaluates its converted right operand first into d1. FFP constants are inline longs (`#$86000048` = 134: 24-bit mantissa, exponent byte - 0x40); an int literal (`> 134`) and a float literal (`> 134.0`) load in different orders.
- `movea p,a0; movea p,a1; op (a1)` is `p->x = p->x op y;` (a single load is `p->x op= y`). A `bcc` out of a switch landing on a lone `bra` after the last case means `default: break;`.
- Byte local loaded via `moveq #0` is `unsigned char`. Word slots and gaps under one address-taken base are one struct local. "Local table full!" means fewer locals (structs/arrays). A jump table spans min..max case; entries hitting the default body are extra labels.
- A `bsr.b` to an adjacent canonical function means one original object: report it (the supervisor tests an evidence-backed `--object-group`); source changes cannot produce it.

## Graphics glue caller (4692 / 34E0)
- Verified: 4692 is a separately admitted RECONSTRUCTED_ASM stack-to-register
  bridge, not an identified exact library member. Its C callers stay C.
- Verified: link its unchanged canonical AJ object through
  reconstructed_asm_dependencies; never replace it with a C stand-in or import
  ASM as C. Map segment 2 COMMON folds into physical DATA; verify that fold.
- Verified: in 34E0, `width = p->field_4 << 3; stride = width;` reloads the frame
  slot. Chaining the assignments keeps D0 and is two bytes short. The 18-byte
  frame includes four unused word locals. The profile is aztec36-large-data.
