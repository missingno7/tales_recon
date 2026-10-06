# Startup routing and binding frontier

The complete pinned startup object has 312 CODE bytes. The original closed
CFG has 310; the independently emitted trailing word2a00 matches the original
gap before cli_parse. All ordinary bytes now match under a diagnostic address
correspondence. The receipt is explicitly not an accepted source/runtime proof.

Two calls required different link conditions from the first standalone control.
The user main callback belongs to encoded node1, physical CODE hunk3. A
DATA-defined exit jump entry makes the linker emit an A4 call rather than a
same-root PC call. Its six-byte payload and CODE relocation are verified.
The authored exit target and user main are stand-ins for routing research;
neither represents the original implementation or establishes its ownership.

Negative controls are retained in history.json. A resident function pointer
reference and a large-code callee did not reproduce the exit call. Compiling
the whole SDK startup in +c/+cd changed its shape to338/386 bytes. An assembly
jmp under dseg produced no DATA bytes; its symbol overlapped numdev and could
not be an executable jump entry. Opcode equality alone therefore failed the
payload/relocation gate. The corrected control uses the jump-table record
recognized by the independently pinned SDK freeseg source, without importing
original game bytes, fixed addresses or patched linked output.

Eight global roles and eleven PC target identities are enumerated in
../../experiments/startup-bindings.json. Their correspondence remains advisory.
Before acceptance, bind every target independently and re-derive the complete
actual object. The allocator and task public/private units now contribute
34 strict runtime bytes; they independently establish two startup helper
entries. All original DATA/COMMON ownership and whole-root layout remain open.
