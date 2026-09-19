# Agent Prompt — DuckTales Amiga Historical Reconstruction

You are starting a new, independent historical reconstruction project for the Amiga version of **DuckTales** from the supplied original game assets.

The project is not a source port yet.

It is not an emulator project.

It is not a decompiler dump.

It is not a modern reimplementation.

The immediate goal is to reconstruct the original game project as completely and faithfully as practical in readable source form, preserving the original executable architecture, overlay structure, data layout, historical build behaviour, and subsystem boundaries.

The long-term goal is that this reconstructed project becomes the authoritative foundation for a later clean source port.

---

## Project location

Create a new sibling project, conceptually:

```text
D:\Prog\ducktales_reconstruction
```

Do not turn any existing Amiga source-port/research project into this reconstruction.

The supplied original disks/executable are verification fixtures and archaeological evidence, not normal build inputs.

---

# North star

The target pipeline is:

```text
original Amiga disks
        ↓
recover filesystem + executable topology
        ↓
recover HUNK root + overlay architecture
        ↓
recover original runtime/library ownership
        ↓
recover readable C / 68k ASM / data modules
        ↓
build real Amiga HUNK objects
        ↓
reproduce the historical overlay-linked executable
        ↓
use the reconstructed source as the basis of a later source port
```

The strongest desired historical endpoint is a naturally linked executable matching the original as closely as technically possible, ideally byte-identical where the historical toolchain and surviving evidence permit it.

Do not weaken this goal prematurely.

---

# Existing evidence from the supplied game

The supplied game is unusually favourable for historical reconstruction.

The first analysis established:

- Disk 1 and Disk 2 are normal AmigaDOS/OFS filesystems, labelled `DT1` and `DT2`.
- Disk 1 boots through a normal `startup-sequence`.
- The main game is a real Amiga HUNK executable named `DuckTales`.
- The executable is not one flat program.
- It contains a resident/root part plus **13 real overlay modules**.
- The root contains at least:
  - HUNK 0: CODE
  - HUNK 1: DATA
  - HUNK 2: BSS
- Overlay code occupies hunks 3 through 15.
- The linker therefore preserved a major part of the original runtime/module architecture.
- Several overlays can already be associated with specific game areas by their embedded file references and strings.
- The resident executable contains a `MANX` marker and code/runtime characteristics consistent with **Manx Aztec C**.
- Therefore, begin with the working hypothesis:
  - substantial portions of the game were written in C and built with a Manx/Aztec toolchain;
  - some performance-sensitive or hardware-specific routines may be 68k assembly;
  - runtime/library code is linked into the resident executable.
- This hypothesis must be tested, not blindly assumed.

The assets include files such as:

```text
DuckTales
dt1.as
dt2.as
main.arc
plane.arc
mbin.arc
invest.arc
invart.arc
loot.arc
loc.arc
chart.arc
exp.arc
jg.arc
mac.arc
mt.arc
ps.arc
cavemaps.arc
clues.arc
```

Treat executable reconstruction and asset-format reconstruction as related but separate workstreams.

---

# Philosophical model

Study the philosophy of `D:\Prog\empires_reconstruction`.

Reuse its strongest ideas:

- reconstruct historical software rather than writing a modern approximation;
- recover complete modules, not only isolated functions;
- preserve natural linker layout;
- use exact toolchain provenance where possible;
- maintain explicit proof levels;
- keep machine-readable progress and blocker ledgers;
- retain failed experiments and exact first mismatches;
- never use per-function placement tricks as evidence of reconstruction success;
- distinguish historical facts from reconstructed semantics and modern conveniences.

Also study the successful ideas from `D:\Prog\icytower_recon`:

- separate third-party/runtime ownership from game-owned code;
- avoid decompiling known library code;
- fingerprint the historical compiler;
- compare generated code and relocations;
- distinguish FUNCTION/CODE match from OBJECT/CU/HUNK/executable match;
- use the original binary only as an oracle.

Adapt all of this to an Amiga HUNK executable with overlays.

---

# Fundamental rule

Do not start by decompiling functions.

First reconstruct the historical executable topology.

The first deliverable is not C source.

The first deliverable is an evidence model that answers:

```text
What was on disk?
What was loaded?
What belonged to the resident program?
What belonged to each overlay?
What was code?
What was initialized data?
What was BSS/common storage?
What was runtime/library code?
What was game-owned code?
What referenced which asset?
How were overlays linked and invoked?
```

Only after this structure is reliable should large-scale source recovery begin.

---

# Phase 0 — immutable fixtures and provenance

Hash every supplied original input.

Record:

- complete disk image hashes;
- main executable hash;
- every extracted game file hash;
- filesystem metadata that matters;
- any transformation performed during extraction.

Normal reconstruction builds must never silently depend on mutable copies of the original binary.

Use a structure such as:

```text
evidence/
    fixture-lock.json
    disks/
    filesystem/
    executable/
```

The original executable is the oracle.

It is not source material to copy bytes from into the reconstructed build.

---

# Phase 1 — filesystem census

Create deterministic tools to parse both AmigaDOS/OFS disks.

Record:

- volume labels;
- directories;
- filenames;
- exact file sizes;
- block chains;
- protection flags;
- comments/dates when available;
- startup-sequence contents;
- hashes of file contents.

Generate a machine-readable manifest.

Example:

```text
evidence/filesystem/disk1.json
evidence/filesystem/disk2.json
```

This should become reproducible evidence, not an ad-hoc note.

---

# Phase 2 — complete HUNK census

Build or adopt a strict Amiga HUNK parser.

Parse the complete `DuckTales` executable.

Record every:

- HUNK_HEADER
- HUNK_CODE
- HUNK_DATA
- HUNK_BSS
- HUNK_RELOC*
- HUNK_EXT
- HUNK_SYMBOL
- HUNK_DEBUG
- HUNK_OVERLAY
- HUNK_BREAK
- other encountered records.

Do not assume symbols/debug records exist.

Record their absence explicitly.

Generate:

```text
evidence/executable/hunks.json
evidence/executable/relocations.json
evidence/executable/overlay-tree.json
```

For every hunk record:

- file offset;
- logical hunk number;
- type;
- allocated size;
- initialized size;
- relocation targets;
- relationship to root or overlay node.

---

# Phase 3 — preserve the original overlay architecture

The overlay topology is historical evidence.

Do not flatten all code into one modern executable during reconstruction.

Represent the initial project roughly as:

```text
src/
    resident/
    overlays/
        ov03/
        ov04/
        ov05/
        ...
        ov15/
```

The numeric names are initially preferred over invented semantic filenames.

As evidence improves, attach semantic labels separately:

```text
ov07
    semantic_role = investment / stock market
    name_origin = RECONSTRUCTED_SEMANTIC
```

Do not claim that `stock.c`, `moneybin.c`, etc. were original filenames unless direct evidence is found.

The linker-preserved overlay node is historical.

Our semantic name is reconstructed.

Keep those facts distinct.

---

# Phase 4 — complete 68k code/data map

For every resident and overlay hunk, classify all bytes.

Possible classifications:

```text
M68K_CODE
INITIALIZED_DATA
BSS
STRING
POINTER_TABLE
JUMP_TABLE
LIBRARY_RUNTIME
COMPILER_RUNTIME
OVERLAY_RUNTIME
ASSET_DESCRIPTOR
UNKNOWN
```

Do not mechanically disassemble data.

Do not mechanically treat executable-looking values as code.

Build a relocation-aware 68k instruction database containing:

- hunk;
- hunk-relative offset;
- raw bytes;
- decoded instruction;
- instruction length;
- direct calls;
- direct branches;
- indirect calls/jumps;
- referenced relocated symbols/hunks;
- strings referenced;
- likely stack arguments;
- register saves/restores;
- confidence that the bytes are executable code.

Generate an explicit unknown/unclassified byte metric.

The census must account for every byte.

---

# Phase 5 — identify the toolchain

The current strongest lead is Manx Aztec C.

Treat this as a hypothesis requiring fingerprinting.

Investigate historically plausible Amiga versions of:

```text
Manx Aztec C
Manx assembler
Manx linker
Manx runtime libraries
```

Pin any acquired historical tools by hash and provenance.

Separate:

```text
PROVEN_HISTORICAL
LIKELY_HISTORICAL
COMPATIBLE_TOOL
ANALYSIS_ONLY
```

Do not call a tool historical merely because it produces similar code.

---

# Phase 6 — runtime/library ownership

Before reconstructing game logic, identify linked runtime/library code.

Search for exact or near-exact matches against candidate Manx runtime objects/libraries.

Likely categories include:

- startup code;
- stack setup;
- memory allocation;
- stdio/file wrappers;
- overlay manager;
- integer helpers;
- floating-point helpers;
- Amiga library wrappers;
- compiler support routines.

The goal is analogous to identifying Allegro in Icy Tower:

```text
known historical runtime/library code
    → reuse or reconstruct from the historical library
    → do not decompile it function-by-function
```

Produce an ownership map:

```text
GAME
MANX_RUNTIME
MANX_LIBRARY
AMIGA_SYSTEM_GLUE
UNKNOWN
```

for every code range.

---

# Phase 7 — compiler fingerprint harness

Build a small experimental corpus of C programs and compile them with candidate historical Aztec C versions.

Probe:

- function prologues/epilogues;
- stack argument layout;
- register allocation;
- `movem` patterns;
- switch lowering;
- loops;
- signed/unsigned comparisons;
- structure field access;
- pointer arithmetic;
- global addressing;
- static data;
- function pointers;
- callbacks;
- varargs if present;
- floating-point operations;
- library-call lowering.

Compare these patterns against the original executable.

The harness must retain:

```text
source
compiler/version
flags
assembler
linker
generated assembly
object/hunk bytes
```

This is a scientific fingerprint experiment.

Do not tune arbitrary source until one function matches while ignoring compiler provenance.

---

# Phase 8 — recover one complete overlay before scaling

Do not begin with the resident core.

Choose one small, semantically coherent overlay as the pilot.

A strong initial candidate is the investment/stock-market overlay because:

- it is relatively small;
- it has clear text anchors;
- it references dedicated assets;
- it appears functionally isolated;
- it is easier to understand than the resident runtime/overlay manager.

The pilot success criterion is NOT:

```text
five functions look correct
```

The pilot is successful when an entire historical overlay node is understood and reconstructed end-to-end.

Aim for:

```text
overlay original
        ↓
routine/data census
        ↓
C/ASM ownership
        ↓
readable reconstructed source
        ↓
historical compiler/assembler
        ↓
real object/HUNK contribution
        ↓
normal overlay link
        ↓
matching code/data/relocations/layout
```

---

# Phase 9 — recover C as C

Where compiler evidence supports C origin, reconstruct C.

Do not translate all 68k instructions into assembly just because assembly is easy to make byte-identical.

The desired artifact is a readable historical source reconstruction.

Prefer:

```c
void update_portfolio(...)
{
    ...
}
```

when the evidence supports compiler-generated C.

Use the historical compiler as the code-generation oracle.

Matching machine code is evidence that the recovered C expression is plausible.

It is not proof of exact original source spelling.

Track:

```text
semantic source match
codegen match
historical source text unknown
```

separately.

---

# Phase 10 — recover assembly as assembly

Where evidence shows hand-written 68k assembly, preserve it as assembly.

Examples may include:

- blitter routines;
- copper handling;
- graphics inner loops;
- sound routines;
- interrupt handlers;
- copy/decompression kernels;
- hardware setup.

Do not rewrite proven assembly as C merely for cleanliness.

Do not assume that every hardware-facing routine is hand-written ASM.

Let evidence decide.

---

# Phase 11 — reconstruct the resident DATA model

The resident DATA hunk must not remain an anonymous byte array.

Recover:

- globals;
- structures;
- tables;
- strings;
- asset descriptors;
- overlay state;
- game state;
- system/library handles;
- function-pointer tables.

Use relocation/reference analysis to discover object relationships.

Where possible, express these as meaningful C structs or assembly labels.

Preserve layout.

Do not modernize field order.

Use layout assertions.

For C, use compile-time checks where the historical compiler permits them or external verification where it does not.

For assembler, assert offsets and sizes.

Maintain a generated data-layout map:

```text
symbol
type
resident/overlay ownership
offset
size
references
confidence
semantic meaning
```

---

# Phase 12 — recover asset formats separately

Create a separate format-recovery layer for:

```text
*.arc
dt1.as
dt2.as
```

Do not entangle asset format decoding with executable source reconstruction.

For each format determine:

- container/header structure;
- directory/index layout;
- compression;
- graphics/audio/map records;
- cross-file references.

Use recovered formats to improve semantic naming of executable code.

For example:

```text
overlay N loads X.arc
X.arc contains map/graphics/data of subsystem Y
        ↓
stronger evidence for overlay semantic role
```

But do not let an asset interpretation override contradictory executable evidence.

---

# Phase 13 — readable reconstruction tree

The final historical reconstruction should become a normal project.

A plausible target shape is:

```text
ducktales_reconstruction/
├── src/
│   ├── resident/
│   │   ├── startup.c
│   │   ├── core.c
│   │   ├── overlays.c
│   │   ├── io.c
│   │   ├── graphics.c
│   │   └── data.c
│   │
│   ├── overlays/
│   │   ├── ov03/
│   │   ├── ov04/
│   │   └── ...
│   │
│   └── asm/
│
├── include/
│   ├── game.h
│   ├── structs.h
│   ├── assets.h
│   └── amiga_hw.i
│
├── formats/
├── evidence/
├── tools/
├── toolchain/
├── docs/
└── build/
```

This is a target architecture, not a mandate to invent unsupported historical filenames.

The reconstructed tree should optimize for:

1. fidelity to original ownership and layout;
2. readability;
3. explicit provenance;
4. suitability as the basis of a future source port.

---

# Phase 14 — proof ladder

Use strict proof levels.

Suggested levels:

```text
SEMANTIC_ONLY
CODEGEN_SIMILAR
FUNCTION_CODE_MATCH
MODULE_CODE_MATCH
DATA_LAYOUT_MATCH
HUNK_CONTENT_MATCH
HUNK_RELOCATION_MATCH
OVERLAY_NODE_MATCH
ROOT_LAYOUT_MATCH
LINKED_HUNK_LAYOUT_MATCH
EXECUTABLE_MATCH
WHOLE_FILE_MATCH
```

These are not interchangeable.

Examples:

## FUNCTION_CODE_MATCH

The machine-code bytes of a recovered function match under independently resolved relocations.

## MODULE_CODE_MATCH

Every routine and relevant padding/data contribution in the reconstructed historical module matches.

## HUNK_CONTENT_MATCH

All initialized content in a historical hunk matches.

## HUNK_RELOCATION_MATCH

Relocation records and targets match the original model.

## OVERLAY_NODE_MATCH

The overlay is naturally produced with the expected hunk set, ordering, allocation and relocation relationships.

## LINKED_HUNK_LAYOUT_MATCH

Addresses and relationships arise from normal object/module/linker behaviour.

No post-link patching or per-function placement.

## WHOLE_FILE_MATCH

The entire executable file matches exactly.

---

# Absolute prohibitions

Do not use any of these as final reconstruction techniques:

```text
copy original executable bytes into output
original-code fallback
runtime patching
per-function fixed placement
one ORG per function
custom linker script forcing individual function addresses
post-link byte patching
manual insertion of original code ranges
carrier runtime
emulator-backed normal execution
```

Temporary experiments may use fixed placement only when clearly labelled as experiments.

They do not count as reconstruction progress.

---

# Natural-layout rule

The correct final build must work like this:

```text
source module order
+
object order
+
segment/hunk declarations
+
historical compiler/assembler
+
historical linker
        ↓
original addresses/layout emerge naturally
```

If a source module only matches because it was manually forced to the original address, the reconstruction is incomplete.

---

# Runtime oracle

Use WinUAE only where runtime evidence is required.

Windows should remain the primary reconstruction workstation.

Prefer:

```text
Windows:
    filesystem parsing
    HUNK parsing
    disassembly
    source editing
    compile/assemble orchestration
    link orchestration
    byte comparison
    relocation comparison
    progress reports

WinUAE:
    original-game runtime oracle
    breakpoints
    memory/register snapshots
    overlay-load observation
    behaviour traces
    historical Amiga-only compiler/linker execution when necessary
```

Do not make WinUAE part of the shipping/runtime architecture.

If historical Manx tools only run on Amiga, automate them as a black-box build worker.

The agent should still be able to:

```text
write source on Windows
launch historical build automatically
retrieve output
compare it
iterate
```

without interactive Workbench use.

---

# Semantic naming policy

The final source should be readable.

But do not fabricate historical names.

Every symbol should have naming provenance.

Example:

```text
UpdatePortfolio
    origin = RECONSTRUCTED_SEMANTIC
    confidence = VERIFIED
```

versus:

```text
foo
    origin = HISTORICAL_SYMBOL
```

if direct historical evidence is found.

Use explicit states:

```text
UNKNOWN
CANDIDATE
OBSERVED
ASM_MATCHED
VERIFIED
CANONICAL_RECONSTRUCTED
HISTORICAL
```

A semantic name must be traceable back to evidence.

---

# Module naming policy

Overlay boundaries are historical.

Source filenames within them may not be.

Therefore:

```text
overlay07
```

is always safe.

```text
stock_market.c
```

is a reconstructed semantic filename unless proven historical.

Maintain both:

```text
historical container identity
semantic role
source filename provenance
```

separately.

---

# Progress reporting

Maintain machine-readable ledgers:

```text
docs/progress.json
docs/blockers.json
docs/modules.json
docs/symbols.json
docs/data-layout.json
docs/toolchain.json
```

For every historical root/overlay module record:

```text
byte size
classified bytes
game-owned bytes
runtime bytes
unknown bytes
functions identified
functions reconstructed
code-matched bytes
data-matched bytes
relocations resolved
current proof level
next blocker
```

Do not hide unknowns.

---

# Blocker format

Every blocker should include:

```text
id
target
current_evidence
first_mismatch
hypotheses
experiments_tried
missing_artifact
next_experiment
status
```

Keep failed hypotheses.

They prevent future agents from repeating dead ends.

---

# Completion criteria for the reconstruction phase

The historical reconstruction phase is complete when:

- every executable hunk and overlay node is accounted for;
- game code is separated from compiler/runtime/library code;
- every meaningful code region has readable reconstructed source;
- C-origin code is represented as C where practical;
- hand-written ASM is represented as ASM;
- important data structures and globals are named and typed;
- asset formats needed to understand the game are documented;
- original overlay/module architecture is preserved;
- the project builds independently from reconstructed source and historical/pinned dependencies;
- no original-code fallback exists;
- the original executable is required only for verification;
- natural linker layout is reproduced as far as surviving evidence allows;
- remaining differences are explicit and localized.

---

# The second project phase: source port

Do NOT begin the source-port architecture until the historical reconstruction has become structurally reliable.

The later source port should be derived from the reconstructed source tree, not independently reimplemented from screenshots or behaviour.

The desired transition is:

```text
historical reconstructed project
        ↓
well-understood game data model
        ↓
portable platform abstraction
        ↓
portable renderer/audio/input/filesystem
        ↓
native source port
```

The source port may later:

- remove overlays;
- replace AmigaOS calls;
- replace custom-chip rendering;
- use a modern renderer;
- replace audio backends;
- run on modern operating systems;
- support widescreen or quality-of-life changes.

But those changes belong to a later layer.

The reconstruction project must remain a fidelity reference.

---

# One rule to remember

> First recover what the original project was. Only then decide what the modern project should become.

Begin now by building the immutable disk/HUNK/overlay census, compiler/runtime provenance model, and Windows-hosted verification pipeline.

Do not begin mass decompilation until the topology and proof infrastructure are stable.

Then recover one complete overlay end-to-end as the methodology pilot.
