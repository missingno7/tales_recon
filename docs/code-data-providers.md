# Typed CODE-resident score providers

`TYPED_CODE_DATA` accounts strictly typed audio bytecode in the original CODE
hunk. It contributes no C or ASM instruction bytes and establishes no original
filename, author, TU, object membership or natural resident layout.

The measured provider covers every command reached from the 35 independently
bound selector roots, following the freshly decoded interpreter grammar and
all pointer edges. Its 2,400 commands and 35 two-byte headers own 5,182 typed
bytes. All 90 reached RELOC32 fields bind to independently reached named
command labels. The four unused state-dependent handlers and all other unused
or unknown opcodes reject.

The grammar is rederived from driver instructions and all 44 handler bindings
before reading score operands. Measured values are then curated into strictly
ranged typed command arguments. Source production reads only those typed
facts; no copied run, raw carrier or original instruction bytes enter an output.
A global grammar digest covers every handler, including rejected ones: a
handler or binding change stales every stream.

Six source modules reproduce the complete measured AJ objects and one natural
link in the single pinned producing job `build/worker-jobs/sol-audio-score-004`.
Every ordinary byte, CODE/DATA/BSS/COMMON extent, symbol, reference count and
named RELOC32 is checked. This batch has local named command pointers only;
external stand-ins, masks, addends and unproved targets reject. No source input
size limit was hit: the largest module has 9,435 source bytes and 1,303 typed
bytes; the largest object symbol inventory has 26 symbols. The first small
control used STOP as a macro name, which collides with the 68000 mnemonic;
all command macros now use the SC_ prefix. Failed/successful trial receipts
remain under build/worker-jobs and worker limits2.json.

The assembler's complete object CODE totals 5,188 bytes. An independent typed
three-byte header+end control in the same producer proves the one-byte implicit
assembler alignment at each module end. Those six generated zeros are verified
as object structure but receive zero source/data/padding credit. They stay
RAW_ORACLE_DEBT at 16E3,1835,1CC5,21DD,257B,2815. No bytes are clipped from an
object: every source command and every implicit object byte is verified, with
separate typed and uncredited partitions. The unreachable 26-byte island
19F7..1A11 has no proved root and is omitted from source. It and its four
relocations stay RAW_ORACLE_DEBT. No guessed filler bridges that island.

The separate code_data_providers ledger map uses DATA_LAYOUT_MATCH. The full
entry lists all six canonical source files and one compact proof. The retained
72-byte pilot fact/batch and its 26 controls remain available; accepting both
pilot and full provider would overlap and rejects. Ordinary recovery writes
preserve the map. Census sums typed_bytes, not the enclosing span or object
padding; hybrid accounting admits each of seven typed partitions exactly once.
Verifier identities are provenance only and never replace complete replay.

Promotion uses the shared regression_receipt gate, complete input snapshots,
unchanged producing inputs, and repeated exact verification under the ledger
lock before atomic publication. A worker's TEST_ONLY accounting scenario is
not an accepted proof and is not part of this patch.

Supervisor commands after applying the reviewed patch (refresh zero-entry
schema outputs before running the full gate):

```powershell
python tools/promote_code_data.py --manifest evidence/code-data-providers/score-batch.json --verify-only
python tools/census.py --write
python tools/census.py --check
python tools/hybrid_image.py --write
python tools/hybrid_image.py --check
python -m unittest discover -s tests -v
python tools/promote_code_data.py --manifest evidence/code-data-providers/score-batch.json --promote
python tools/census.py --write
python tools/census.py --check
python tools/hybrid_image.py --write
python tools/hybrid_image.py --check
```

Missing retained inputs require a fresh unchanged ordinary aztec_worker batch
and reviewed SHA pins. A cached PASS cannot substitute for missing producer
artifacts. No normal game build or complete root layout is claimed.
