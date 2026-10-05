# Runtime vars provider controls

The unchanged SDK vars.c compiles against pinned headers and reproduces the
actual 3.6a library's DATA/COMMON layouts in four normal link arrangements.
The same source, with contemporary headers and 5.0a-short tools, reproduces
the c16 library's layouts. Separate extraction also measures the c32 object.
Every extracted complete object occurs exactly once in its pinned archive.
These controls contain no original game bytes or fixed-address storage.

All three objects initialize ten bytes: short20, zero pointer, zero long.
The original initialized DATA contains no matching complete ten-byte range.
Its last four bytes are00140000. That suffix does not establish original
_numdev ownership or justify clipping an incompatible library object.
No original DATA or COMMON bytes are accepted by this experiment.

The 16-bit-int objects define64 COMMON bytes; c32 defines72. The two releases
emit different common-field order: isolated SysBase is relative0 in3.6a and
relative56 in5.0a c16. Authored independent DATA/COMMON controls shift objects
naturally. Earlier declarations of MathBase/errno merge without duplicate
storage; their order affects field positions. This does not prove original
names/TUs or select a compiler release.

Retained failures: volume INCLUDE assignment was insufficient for3.6a cc;
explicit -I Old1:include succeeds. A5.0a source control rejected old header
#endif labels, and its linker rejected the old assembler's AJ root objects.
Contemporary headers and its own CJ assembler succeeded in a fresh job.
failures.json retains the failed steps and errors; no failed output is counted.

The final original DATA word has three consumers. A normal link of the pinned
startup _main object provides context for resident766C: the known CFG ends
after310 bytes, while the complete library object has312 and the extra two
bytes2a00 agree with the original gap before the next known entry77A4.
All code/callee/global bindings remain to be verified. main-context.json
records this distinction; no startup or DATA contribution is promoted.

Measured receipts and bulky outputs remain in the named ignored worker jobs.
commands36.json uses the old sources here; commands50.json uses modern/.
The filename vars-source.c is a worker label. SDK provenance is vars.c in
sysio.arc. Its source hash and distribution archive are retained separately.
