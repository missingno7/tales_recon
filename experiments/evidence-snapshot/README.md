# Bounded evidence snapshot control

Run `python experiments/evidence-snapshot/probe.py` from the repository root.
The probe runs twelve real canonical standalone sources through the isolated
exact verifier, using only already validated compiler-cache artifacts. Missing
current recipes are excluded before timing; launching a compiler is forbidden.
Three baseline and three snapshot runs alternate their order. Every complete
comparison report must have the same hash, every verdict must remain EQUAL,
and canonical ledger/source/proof hashes must remain unchanged.

`report.json` records a median 6.73 seconds without reuse versus 4.11 seconds
with reuse (1.64x, 39% less elapsed time). Each snapshot run uses one strict
derivation and thirteen content-checked reuses. These are host verification
measurements, not guest compilation or sustained fleet throughput measurements.

The initial request selection included standalone sources whose current recipe
was not cached. The probe stopped before launching a compiler or publishing
anything. It now records these preflight exclusions in the report. An earlier
implementation also lost time deep-copying the full census result: five image
reads took about 2.63 seconds versus 1.91 seconds without reuse. Replacing that
recursive copy with locally created, memory-only serialization removed the
copying bottleneck. Neither experiment changed proof acceptance or recovery.

Focused tests cover content edits with preserved metadata, canonical and unit
dependencies, additions/deletions, mid-derivation changes, independent returned
objects, nested/disabled scopes, thread isolation, and advisory/strict separation.
Real fixture/proof read controls reject altered bytes without modifying originals.
