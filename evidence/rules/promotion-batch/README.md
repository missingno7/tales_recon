# Supervisor batch-promotion control

`python experiments/promotion-batch/probe.py` re-verifies two already-owned
sources through the exact cached compiler comparator, runs one real complete
host regression suite, and publishes their individual proofs in a fresh retained
workspace under `build/promotion-control`. The independent census proof loader
then accepts both proofs. Canonical repository source/proof/ledger hashes are
checked before and after; this control adds no recovery coverage.

`report.json` is the control for the current implementation. `report-initial.json`
retains the earlier successful control before an audit tightened regression
input binding: the current gate additionally hashes test/tool source before and
after the suite, rejecting a concurrent edit even when the test process returns
zero. These are workflow controls, not new historical compiler evidence.

The fault-injection tests in `tests/test_promotion_batch.py` retain the failure
cases as reproducible experiments: member mismatch, overlapping literal spans,
changed inputs, write failure, interruptions before/after ledger commit, later
foreign edits and concurrent ledger writers. Scratch transaction journals are
ignored local artifacts; no original executable bytes are copied into source.
