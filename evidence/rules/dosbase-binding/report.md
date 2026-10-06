# DOSBase and CRT0 controls

These controls use the Amiga DOS library. They extend no PC/DOS reconstruction.

The two wave12 jobs completed before the updated task-card instruction. Their
successful steps and artifact hashes are retained in receipts.json; they were
not rerun. SDK source and authored routing/data controls are separate inputs.
The five dos.arc members are retained whole and their bytes were checked
against the pinned source archive. Names are SDK provenance, not original
program filenames or original object membership.

The DOSBase initializer obtains ExecBase from address4, calls vector -408
with the independently bounded dos.library string, and stores D0 at H1+A98E.
Five complete DOS leaves match uniquely with this handle. Library/source links
are byte-identical in both authored DATA orders. The original handle storage
provider and ordering remain UNKNOWN. None of these54 bytes is accepted.

The subsequent one-trial CRT0 review used a worker-local task card at HEAD
436c8545b76cd5061df3dc2fd35e12dd86c3edfe. The whole122-byte object has108 equal
ordinary bytes; all differences occupy seven SDK fields. The H1/BSS boundary
and clear count derive from actual original allocations. Its single relocation
matches. Library/source executables are equal; object bytes are different.
The saved-stack and startup-callee correspondences remain pending. This is
experimental field correspondence, not a normalized accepted contribution.

See ../../experiments/dosbase-bindings.json and
../../experiments/crt0-bindings.json. The strict current accepted-caller entry
policy is unchanged. No stronger proof level, source acceptance, runtime
accounting, original storage ownership, or exact release attribution is granted.
