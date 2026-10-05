# Pinned graphics wrapper controls

Twenty-eight successful guest commands in wave7-graphics-003 extract five
objects from the pinned 3.6a c.lib, assemble their independently supplied
graphics.arc source, and link both forms against two authored DATA objects.
No game bytes enter any input. All twenty links resolve normally.

InitBitMap, InitView, InitVPort, MakeVPort and MrgCop cover 68 complete
resident code bytes. The library and source forms match byte-for-byte in each
link. Moving the GfxBase symbol by six bytes changes only its A4 displacement.
Each output's displacement resolves to the actual symbol-map definition.
Exact AJ object sizes bound the contributions; per-link HUNK padding is
excluded. Complete bytes outside that independently controlled address field
match the original. All five original fields refer to DATA+5374.

Canonical F1E36 stores the result of the graphics.library open call in that
same mechanically named global and calls all five original wrapper entries.
Its source and accepted proof provide separate call/reference evidence; the
SDK ABI by itself does not select library provenance or storage ownership.
InitView has another structural candidate at resident+89FA using a different
base. The audit retains both candidates and requires the GfxBase identity.

This is curated experimental evidence, not a canonical runtime contribution.
The accounting total remains 430 pinned runtime bytes. Before counting these
68 bytes, add a strict consumer that re-derives the actual library/source/link
identities, binds the original base/call evidence, rejects mutations and stale
dependencies, and uses produced bytes for the accounting comparison. Recover
the OpenLibrary dependency to strengthen the graphics handle binding. No
exact original compiler release, COMMON ownership, TU or root layout is proved.

Retained failures: wave7-graphics-001 invoked cc without -a and passed object
bytes to as, so the DATA definitions were absent. wave7-graphics-002 authored
CRLF assembly; as rejected carriage returns. The corrected LF assembly controls
passed in a fresh job. These are TOOLCHAIN setup failures, never near matches.
Bulky job requests, artifacts and logs remain under ignored build/worker-jobs.

Follow-up: the pinned OpenLibrary frontend and separate __OpenLibrary helper
also match their complete 4+16 byte natural link at resident+89D0..89E4.
Independent exec.arc source and c.lib objects agree across both DATA orders;
the frontend's PC jump resolves to the actual helper symbol. The original
helper's A4 load binds SysBase at DATA+B3A2. The two wrappers were split into
UNCERTAIN extents by static CFG analysis; their pinned object boundaries and
natural call binding now establish the complete 20-byte library unit. See
`../../experiments/openlibrary-wrappers.json` and the retained openlibrary
inputs. This makes 88 experimental matched resident bytes, still unpromoted.
