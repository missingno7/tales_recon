# Independent startup leaf-target checks

Complete Alert (24), WaitPort (12) and GetMsg (12) library objects match
uniquely at their original startup call targets. Independently assembled
exec.arc source produces identical links. Moving the authored SysBase DATA
definition by six bytes changes only its A4 displacement. Original targets
all use the already established SysBase address at DATA+B3A2.

No runtime accounting contribution is published. The strict existing consumer
requires accepted caller bindings, and startup itself is still unaccepted.
The source/library/object evidence is retained for the binding campaign.

One rejected association is important: the initial target list mistakenly put
Forbid at resident869C. Whole-object plus known-base verification rejected it.
Forbid matches uniquely at8974; the startup audit already identifies869C as
CurrentDir. Original-entry and known-base checks were retained. Candidate
artifacts copied before the failed check were moved back to ignored scratch.

Next: independently establish DOSBase, check the four DOS leaf targets, and
bind CLI/Workbench parser globals across routines. A matching startup template
does not establish those target identities or original storage ownership.
