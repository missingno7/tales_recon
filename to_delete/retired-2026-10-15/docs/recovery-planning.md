# Read-only recovery planning

`tools/recovery_plan.py` is a bounded diagnostic step for a grinder run that
has no eligible work. It reads the function census, recovery ledger, attempts,
and candidate paths. It does not invoke a proposer or compiler, write recovery
state, change ownership, or promote a proof.

The supervisor API is:

```python
from recovery_plan import plan
report = plan(node=None, ids=None, limit=256, max_packages=4,
              max_unknown_calls=1, max_data_references=40)
```

The positional order is the same. Pass the grinder's `node`, requested `ids`,
and active limits through unchanged. An ID filter limits diagnosis to that
request; an empty or omitted filter means all current ranked candidates. The
CLI prints the same JSON report:

```text
python tools/recovery_plan.py --limit 256 --max-packages 4
```

`RECOVERY_REVIEW_REQUIRED` means no candidate in the selected scope meets the
grinder constraints. Each package is a bounded read-only diagnostic with an
action label, at most eight dispatched IDs, the measured constraints, and
references to the evidence needed for review. A same-hunk dependency SCC is a
source/layout hypothesis, never a compiler-ready unit. The report includes its
physical interval, canonical bridge entries, unclassified gaps, missing
candidate sources, and every external same-hunk PC-relative callee classified
as canonical or unresolved. An SCC is not proof of a compiler-coupled source
unit; external canonical calls still need layout context. A truncated SCC
becomes a review package and explicitly reports `members_complete: false`; its
shown IDs are only a bounded preview. `package_count_total` and
`omitted_package_count` make the package cap explicit.

The report keeps two views of the frontier. `first_constraint_counts` follows
the grinder's deferral order; `all_constraint_counts` includes overlapping
constraints and any canonical recovery blocker. Therefore these counts must
not be summed as unique functions. The source field distinguishes a verified
retained candidate file (path and SHA-256 both checked) from an attempt receipt
whose source bytes are unavailable. Prior proof blockers are grouped by
mechanism: byte-return/extension evidence is separate from persistent source
or algorithm-shape mismatches, dependency layout, data ownership, and external
call binding.

At the 2026-09-27 frontier measurement with a 256-byte grinder limit, there
were zero eligible functions. Grinder's first deferral reasons were 389
uncertain extents, 71 resident functions, 48 size-limit cases, 8 unresolved
local dependencies, and 3 unknown-call-limit cases. Seven explicit blocked
functions were present: three byte-return/ABI cases, two dependency-layout
cases, one persistent code-generation/source-shape case, and one external
register-call binding case. These figures are a snapshot; the planner reports
fresh counts from the current ledgers each time it runs.

The planner only diagnoses work. Its output is not a recovery proof, source
claim, or permission to reuse original bytes. Numeric overlay names remain
container identities; semantic names and source filenames still need separate
provenance. Fixture locking remains explicit and is never triggered by this
tool.
