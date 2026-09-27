# `ov09_F_298E` table-mask code-generation probe

Scope was limited to two source hypotheses around the repeated table-byte/mask expression. No canonical source, ledger, promoted evidence, or fixtures were edited. The compiler was the installed Aztec 3.6a profile; comparisons used the existing pure `compare_function` comparator and the complete closed 660-byte function (physical hunk 9, candidate node 7).

## Evidence and baseline

The expected function is `CLOSED_CFG`, starts at `0x298e`, and is 660 bytes. Retained source `ov09_F_298E-v15.c` has an existing Aztec 3.6a receipt: 672 bytes, `DIFFER`, mnemonic similarity 0.9839. The source/fingerprint history already includes signed/unsigned byte declarations, explicit casts, unsigned index forms, and a non-register integer mask temporary (`v12`), so those were not repeated.

The expected first table-mask sequence, at function offsets `+108..+122`, is:

```text
mulu.w #6,d0
lea table(a4),a0
moveq #0,d1
move.b (a0,d0.l),d1
```

The retained v15 candidate instead emits:

```text
mulu.w #6,d0
moveq #0,d1
move.w d0,d1
lea table(a4),a0
moveq #0,d0
move.b (a0,d1.l),d0
```

So it copies the index from D0 into D1, then reuses/clears D0 for the loaded table byte and accumulates the mask in D0. Compared with the expected allocation (D0 index, D1 table/result, D2 mask), the extra copy and second zero-extension cost 4 bytes in each of the three repeated checks: `+12` overall, matching the 672-versus-660 length delta. The relocation-normalized full-function comparison remains `DIFFER`; no candidate is an exact function proof.

## Hypotheses tested

| Candidate | Source hypothesis | Aztec 3.6a size | Exact verdict | First structural mismatch |
|---|---|---:|---|---|
| `register_row_value.c` | Mark the already evidenced unsigned row and integer value locals `register`, in case the historical register pressure selected the expected data-register assignment. | 620 | `DIFFER` | At `+4`, expected `move.l a2,-(sp)` becomes `movem.l d4-d5/a2,-(sp)`; normalized first byte difference `+2`. Register hints changed the whole allocation/frame enough to undershoot by 40 bytes. |
| `explicit_register_byte_temp.c` | Materialize each table read as a `register unsigned char tableByte` before applying the existing mask, to test whether an explicit byte result has the expected lifetime/register. | 682 | `DIFFER` | At `+4`, expected `move.l a2,-(sp)` becomes `movem.l d4/a2,-(sp)`; normalized first byte difference `+4`. It overshoots by 22 bytes and changes allocation before the target expression. |

Both compilations completed. Full comparator results, including cache keys and relocation issues, are in `results.json`; tested C files are alongside this report. The first structural mismatch is in the prologue for both new candidates, while the retained v15 mismatch is specifically the repeated mask/index register allocation described above.

## Verdict

Neither new hypothesis improved the retained near-match. The 672-byte v15 candidate is still the closest demonstrated source form, and its exact residual size has a consistent local explanation: three copies of a four-byte allocation penalty. The broad `register` and explicit-byte-temporary forms perturb prologue/register allocation and are worse. This supports a compiler/register-allocation mechanism for the blocker, not a missing semantic body or an established source type fact.

Next useful experiment: use existing fingerprint source forms to isolate a minimal table-byte-index plus mask expression under the same Aztec 3.6a profile, testing whether a source-level lvalue/array representation can naturally keep the index in D0 and byte result in D1. Keep it as an independent fingerprint/diagnostic; do not promote it absent a full 660-byte exact comparison.
