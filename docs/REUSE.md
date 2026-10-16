# What transfers to the next project

This page lists what carries over from DuckTales to the next Amiga game, and
to other matching decompilation projects. It also records the process
lessons. Keep it short. Update it when a tool changes tier or a lesson is
confirmed.

## Any matching decompilation (platform-independent)

| Piece | Where | Notes |
| --- | --- | --- |
| Exact verify loop: candidate -> pinned compiler -> compare with relocation/symbol identity | `check_function.py`, `check_unit.py`, `function_compare.py` | The comparison core is generic. Profiles and harness are toolchain-specific. |
| Ownership ledger + hash-bound proofs + quarantine | `recovery/ledger.json`, `repo_paths.py`, `to_delete/` | One map per proof class; canonical writes behind one lock (`recovery_transaction.py`). |
| Proof-class registry, one publisher CLI, per-proof validation memo | `acceptance.py`, `promote.py`, `validation_memo.py` | Each class declares ledger map, accounting categories, validator, contributions and publisher. The memo keys each accepted row by the content of every file its validator read plus the tools import closure. |
| Proof classes kept separate (exact, asm, behavioral, unresolved) | `docs/proof-levels.md`, `behavioral.py` | The behavioral route (exact after deleting a whitelisted codegen delta + caller observability check) generalizes to other compiler-version gaps. |
| Whole-image accounting, every byte classified | `hybrid_image.py` | Needs only a parsed executable and per-class contributions. |
| Behavior coverage report | `behavior.py` | Derived view; no stored state. |
| Semantic naming layer | `recovery/names.json`, `readable.py` | Reviewed names with evidence notes; applied only to a generated readable view, never to matched sources. |
| Compile cache/queue, hypothesis ledger, declaration views | `compile_queue.py`, `shape_search.py`, `declaration_views.py` | |
| Supervisor + Codex worker briefs | `codex-workers` skill, AGENTS.md worker loop | One target per worker, supervisor owns canonical writes. |

## Amiga (68000, HUNK, AmigaDOS)

| Piece | Where |
| --- | --- |
| Strict OFS/ADF reader | `ofs.py` |
| HUNK parser incl. relocations and Manx overlay tree | `hunk.py` |
| 68000 recursive-descent function census (Capstone) | `function_census.py`, `analysis_support.py` |
| Unattended WinUAE compiler worker | `aztec_worker.py`, `run_worker.ps1`, `docs/build-worker.md` |
| Aztec/Manx toolchain profiles, AJ object parser, c.lib/m.lib member identification | `compiler_oracle.py`, `aj.py`, `runtime_members.py`, `runtime_match.py` |
| A4 small-data ABI, resident/overlay call routing | `resident_interfaces.py`, `library_a4.py`, `runtime_entry_routes.py` |
| Platform-service inventory (OS glue members called by game code) | `behavior.py` platform section |

Aztec C 3.6a knowledge (`docs/COMPILER_LEARNINGS.md`) transfers to any game
built with the same compiler.

## DuckTales only

The audio driver and score providers (`audio_*`), the specific DATA and
code-data providers, the story tables, and the `.arc`/`.as` formats
(`formats/`).

## Process lessons

1. **Measure behavior coverage from day one** (`behavior.py`), not only
   matched bytes. Matched bytes hid that nothing was named, no asset was
   decoded and nothing had run.
2. **Tier the gate by what changed.** A promotion that adds only canonical
   sources and proofs re-proves canonical state; the full tooling suite runs
   when tools or tests change, and before every commit. Never let tool file
   hashes leak into generated evidence (every tool edit then forces a
   regeneration). **Keep the full suite fast.** Profile it with `--durations` and cProfile when it
   passes about 10 minutes. One per-instruction disassembler construction cost
   15 minutes of every gate run. Prefer synthetic fixtures. Keep real-repo
   replays few.
3. **Do not let one codegen quirk block understood code for weeks.** Add an
   explicit, separately accounted behavioral class early. Keep it
   upgradeable to exact.
4. **Retain the best candidate source for every blocked function** under the
   blocker record. Pruned attempt history forced re-authoring.
5. **One admission interface per proof class:** check, validate,
   contributions, promote, replay (`behavioral.py` is the template). Do not
   grow a provider, promoter and catalogue triple per byte class. Measured
   cost of not doing so: admitting the first unit with a behavioral member
   meant finding seven separate hard-coded "verdict == EQUAL" gates (unit
   compare, unit promotion, member comparison, retain_unit, durable_unit,
   the census receipt validator and the hybrid replay). A shared acceptance
   predicate per class would have been one edit. Now implemented as
   `acceptance.py` with one `promote.py CLASS MANIFEST` entry point.
6. **No gated promotion while any worker can write under `tests/` or
   `tools/`.** The gate fails closed, and the run is wasted.
7. **Build orchestration only for a large frontier.** A fleet scheduler
   outlived its frontier. Plain worker briefs were enough afterwards.
8. **Plan the semantic layer early:** a reviewed map from mechanical to
   semantic names, applied to a readable view, never to matched sources.
9. **Parallel workers deliver patches against a named HEAD, and reuse
   general mechanisms.** Two workers once solved "C unit depends on an
   assembled member" twice in parallel. One rewrote a file with CRLF line
   endings (936 changed lines for 9 real ones). Brief workers to rebase onto
   the current HEAD, extend the general recipe, and keep LF only.
10. **Memoize validation per proof, keyed by observed reads.** A memo keyed
    by the whole input closure was slower than re-validating, because every
    lookup rehashed everything. Keying each accepted proof by the files its
    validator actually opened (an audit hook records them), plus the tools
    import closure, made warm canonical checks 10x faster. "Once exact, it
    is exact" then holds mechanically: an unchanged proof is never
    re-derived, and any changed input still is.
11. **Workers must not copy the repository.** A worker that cloned the tree
    for scratch verification used 24 GB on a nearly full disk. Brief workers
    to verify through isolated imports and their own directory.

12. **Prove entry and boundary separately.** A relocated address alone does not
    establish executable entry. Bind the actual caller or typed SDK callback,
    then prove every outgoing edge. Explicit tails can reuse an independently
    replayed destination without absorbing its bytes or inheriting its predicate.
