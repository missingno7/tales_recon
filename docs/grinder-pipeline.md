# Mechanical source recovery

The host now discovers function candidates, supplies bounded evidence, batches
historical compilation, compares complete object contributions, promotes exact
matches after regressions, and parks repeated failures. The proposer only writes
C. No complete game or overlay has been reconstructed.

## Measured bootstrap

The recursive census finds 652 candidates and 246 closed contiguous CFGs. It
decodes 127,462 distinct CODE bytes, starting with ov14/ov12/ov13 and ov07 before
the other CODE hunks. Unreached ranges and uncertain boundaries remain explicit.
These counts are analysis coverage, not reconstructed-source coverage.

The preferred ov12 has one 2,998-byte closed CFG with 132 call sites. Ov14 has
smaller leaves and is therefore the mechanical bootstrap; ov07 remains the
semantic whole-overlay pilot.

| Promoted function | Complete code contribution | Profile |
| --- | ---: | --- |
| ov14_F_03AE | 20 bytes | aztec36 |
| ov14_F_03C2 | 80 bytes | aztec36 |
| ov04_F_00C4 | 34 bytes | aztec36 |
| ov04_F_00E6 | 30 bytes | aztec36 |

All four initial bootstrap functions passed the exact verifier. Their 164 bytes are FUNCTION_CODE_MATCH,
with external data identities resolved independently; no global-data layout is
claimed. Other tested profiles differ on these game functions. This is useful
release/ABI discrimination, not proof of a uniquely selected historical release.
The 470 matching runtime bytes and cross-release segload ambiguity remain intact.

The next ranked batches recovered 12 additional leaves (640 bytes), with failures
retained and revised from exact feedback. The ordinary verifier then automatically
included a recovered callee and verified the entire naturally compiled 88-byte
unit `ov11_F_25D6` + `ov11_F_25F8`. Both short BSR targets resolve to the verified
callee symbol. Promoting its 54-byte caller brings the total to **17 functions,
858 bytes**. A subsequent four-leaf batch added 204 bytes, reaching 21 functions /
1,062 bytes before live-model trials. The first successful hosted run then promoted
`ov11_F_4A92` (18 bytes) on round one and `ov11_F_5A62` (78 bytes) on round four,
reaching **23 functions / 1,158 bytes**. The latter converged through 74, 74, and
82-byte mismatches before EQUAL. The third candidate was parked after a repeated
mismatch. This remains function-level proof, not an ov11 module match. The full
run receipt is `recovery/runs/a7a55000b4954d8995468d316a1dbd8c.json`.

The end-to-end test uses `experiments/grinder-bootstrap/fixture_proposer.py`, a
deterministic replay of independently authored C, **not an LLM**. It promotes the
four leaves and deliberately emits a wrong ov11 candidate. The repeat is cached,
becomes a blocker, and acquires no canonical source ownership. The live OpenAI adapter now also drives bounded trials through this contract.
Its attempts and outcomes are retained separately from this fixture replay.

## Commands

Run from the repository root with the existing pinned toolchains installed:

```powershell
python tools/function_census.py
python tools/grinder.py rank --limit 12
python tools/grinder.py facts ov14_F_03AE
python tools/check_function.py ov14_F_03AE experiments/grinder-bootstrap/ov14_F_03AE.c --json
python tools/check_function.py --batch experiments/grinder-bootstrap/batch.json
python tools/fingerprint.py --build
python tools/fingerprint.py --function ov14_F_03C2
python tools/fingerprint.py --search movem
```

`check_function` uses 3.6a and 5.0a-short by default. Repeat `--profile` to select
profiles. `--no-promote` retains comparisons without assigning canonical source.
Its batch input is an array of `{id, source, profiles}` objects. Exit status 0
means at least one trial matched, 1 means no match, and 2 means an input/service
blocker; consumers of a multi-function batch must inspect each verdict.

The host uses the existing native Capstone installation. Only historical
compile/assemble/link operations run under the unattended WinUAE worker.
`compiler_oracle.py` never reads the original game. It mounts independent source
and pinned dependencies and links `harness.o +o1 candidate.o +o0 c.lib` naturally.
Candidate code is not executed. No fixed placement or executable patching occurs.

## Proposer contract and long runs

```powershell
python tools/grinder.py run --batch-size 16 --max-rounds 1000 --max-attempts 5 --profile aztec36 --proposer python tools/local_model_proposer.py
```

Put `--proposer` last: its remaining arguments are the adapter command. Each
invocation receives one JSON fact package on stdin, and must emit exactly:

```json
{"source":"recovered(a) int a; { return a; }\n"}
```

The adapter may call the user's chosen model service. No model provider, account,
or API key is embedded in this repository. The optional `tools/model_proposer.py`
adapter uses the installed CLI and existing login with an explicitly selected
model (default `gpt-5.6-luna`, low reasoning). It requests read-only, ephemeral,
structured output, disables project tool features, caches model proposals, and
rejects tool events or incomplete responses. Live OpenAI calls are now running after explicit user approval to transmit bounded
function evidence and candidate C. Proposals and comparisons retain independent
receipts. Do not count fixture replay or a completed model request as convergence.
A persistent offline Qwen3-Coder 30B Q4_K_M backend now drives this contract,
with measured prompt budgets, VRAM, throughput, caching and per-run reports.
Its frontier trial found no new matches; live calibration reproduced an already
recovered 20-byte function without adding coverage. See [local inference and
measured limits](local-model.md).
The interface follows the [official non-interactive documentation](https://learn.chatgpt.com/docs/non-interactive-mode).

Packages are limited to 160 decoded
instructions and 64 KiB, and contain extent, disassembly/CFG, ABI, nearest measured
compiler examples, calls, data/string references, relocations, recovered
dependencies, retained prior candidate C, and up to five compact mismatches. Mechanical `G_hNN_OFFSET`
and `F_hNN_OFFSET` extern names identify evidence targets; the harness allocates
their definitions normally. They are not address-placement directives.

The default queue allows high-confidence closed overlay functions up to 256 bytes,
excludes indirect flow and unrecovered same-node dependencies, and bounds unknown
calls and data references. It retains the existing ranking and defaults to aztec36
alone; alternate profiles require an explicit request. Recovered entries
are skipped on restart. Proposer errors and bounded non-convergence produce
`recovery/blockers/*.json`; `python tools/grinder.py retry ID` explicitly requeues
one. The loop processes other eligible candidates. Infrastructure failures pause
the run without marking the selected functions blocked. A first cache hit still
provides a revision opportunity; only a repeated failure for that function ends
its attempt. Each completed round saves a checkpoint and a permanent `recovery/runs` receipt.
Source validation failures are returned as candidate feedback. Repeated identical
validation failures end that candidate, as do repeated cached compiler mismatches. Use one grinder writer per
checkout. The worker has an exclusive compilation lock; a stale lock requires
checking that its worker has stopped before removing that one file.

## Exact comparison and proof boundaries

The verifier validates fixture identity, current census implementation, evidence
bytes, and closed extent. It extracts the entire AJ/CJ object's code contribution
from its natural overlay HUNK and cross-checks object length, symbol start, and
HUNK padding. It cannot select a convenient matching instruction subset.

HUNK relocation sites, types, widths, target identities, and addends must agree.
A4-relative fields are resolved from the naturally linked startup's relocated
LEA, the linker symbol map, and explicit external identities. The Manx logical H2
COMMON-to-H1 convention is checked against actual allocation. Only proven address
fields are normalized in comparison memory; instruction bytes, widths, branches,
and constants must otherwise match exactly. Ambiguous displacement locations and
unproven target identities fail. Normalization never alters a linked artifact.

Feedback includes lengths, relocation profiles/proofs, raw and normalized first
differences, first differing instruction, mnemonic similarity, prologue/epilogue,
owned data/BSS sizes, compiler/flags, cache key, and compiler-error logs.

For a caller with adjacent recovered same-node dependencies, `check_function.py`
automatically creates one source unit in natural function order. Existing C is
renamed to mechanical dependency symbols; no original bytes enter compilation.
Every function symbol must occur at its expected contribution boundary, all
object bytes must be accounted for, and every member must match before the caller
can promote. Wrong callee identities, calls into a function's interior, changed
dependency code, extra trailing code, padding gaps, and owned data reject the unit.
Unit sources, dependency hashes, whole-object hashes and receipts are retained in
`recovery/units`; generated coverage validates the linked receipt. `check_unit.py`
exposes the same complete-unit comparison for diagnostics. No MODULE_MATCH is
granted for a partial historical module.

Unsupported source/harness declarations are recorded per trial. They no longer
cancel other valid candidates in the same compilation batch.

Current conservative blockers include candidate-owned data/BSS, PC-relative data
ownership, and call bindings outside completely verified units. These require additional
proof support before promotion. Unknown indexed jumps stop descent; no jump table
is guessed. Explicit A4 writes/restores prevent a closed ABI-based proof.
Indirect calls can be recorded and compiled, but are deprioritized. The harness
currently supports self-contained C with simple extern scalars, pointers, arrays,
structs, and old-style function declarations; unsupported declarations return a
blocker. Inline assembly and external includes are outside this candidate-C API.

FUNCTION_WITH_DATA_MATCH, MODULE_MATCH and OVERLAY_NODE_MATCH are reserved stronger
states, not currently granted by the function verifier. They require complete
data/layout/dependency contributions and a normal whole-module `+oN` link. The
next expansion is call/data proof support and more ranked leaves, then ov07 and
the remaining overlays, with resident reconstruction later.

## Cache, fingerprints and ledgers

One worker invocation handles all missing trials in a batch. Cache identity
includes source, compiler/assembler/linker hashes, flags, harness, headers,
library, link recipe and worker implementation. Identical successes **and failures**
are reused. Malformed candidates receive explicit negative responses to compiler
questions. The guest shell permits status 254 (5.0a syntax failure) so later trials
still run; each trial retains its own status. Both behaviors were exercised with
bad and good sources in one batch. Artifact hashes and independently re-extracted contribution metadata
are checked before use. Corrupt cache entries stop with a blocker, never silently
masquerade as valid results. JSON ledger writes use atomic replacement.

The matrix contains 24 programs × four profiles = 96 compiled trials:
3.6a default / `+L`, 5.0a default / `-ps`. It covers integer widths/signs,
arguments/returns, frames/registers/MOVEM, branches/loops/switches, pointers,
structs/arrays, globals/statics, indirect calls, library calls and K&R varargs.
The latest additions measure char returns versus expression fallthrough, embedded
string literals, and compiler-generated arithmetic helpers.
`build/compile-cache` retains source, assembly, AJ/CJ object, linked HUNK, symbols,
logs, relocations and hash receipts. The searchable fingerprint index retains
code, assembly, symbols, identities and artifact hashes. A repeated 96-trial run
used zero worker invocations; see `evidence/experiments/fingerprint-cache.json`.

- `evidence/functions/ledger.json`: generated recursive evidence and uncertainty.
- `evidence/executable/instructions.json`: expanded decoded instruction database.
- `evidence/functions/ranking.json`: generated remaining work order.
- `evidence/fingerprints/index.json`: measured compiler matrix.
- `recovery/ledger.json`: canonical promotions, attempts and blockers.
- `recovery/proofs`: source/extent/tool/object hashes, reference proofs, comparisons,
  regression receipts and dependencies.
- `src/recovered`: canonical C only after EQUAL and host regression success.
- `recovery/attempts` and `recovery/candidates`: failed or provisional work.

Failures never change canonical ownership. `census.py` validates promoted source
and proof hashes, original extents, complete normalized comparison hashes, and
non-overlap before deriving coverage. Function heuristics never add matched bytes.

After intentional changes, regenerate and check:

```powershell
python tools/function_census.py
python tools/census.py --write
python tools/census.py --check
python -m unittest discover -s tests -v
```
