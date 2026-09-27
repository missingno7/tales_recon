# Medium overlay frontier audit

Read-only audit of the current 526-entry Amiga ranked snapshot. The slice is `CLOSED_CFG`, overlay only, 256–768 bytes, excluding `ov04_F_0536`, `ov09_F_298E`, and `ov11_F_4B0C`. No sources were guessed, no compilation was run, and no canonical files were changed.

The slice contains 24 candidates. Six have no pending same-node dependency. None meets the current grinder admission rules: three exceed only the 40-data-reference cap, two exceed that cap and have `same_node_unit_ready=false`, and one exceeds the cap and has PC-relative data. The other 18 have at least one pending local dependency. There are no low-confidence, indirect-flow, >1 unknown-call, or relocation-table hits among the six dependency-free candidates.

| Rank | Candidate | Size | Calls / unknown | Data refs | PC data | Unit ready | Admission issue |
| ---: | --- | ---: | ---: | ---: | ---: | --- | --- |
| 1 | `ov08_F_1D42` | 522 | 20 / 0 | 56 A4-relative | 0 | Yes | 40-reference cap only |
| 2 | `ov04_F_0B50` | 622 | 32 / 0 | 65 A4-relative | 0 | Yes | 40-reference cap only |
| 3 | `ov05_F_3836` | 616 | 34 / 0 | 75 A4-relative | 0 | Yes | 40-reference cap only |
| 4 | `ov04_F_149C` | 688 | 31 / 0 | 61 total: 47 A4-relative, 14 PC-relative strings | 14 | Yes | 40-reference cap; string-tail ownership needed |
| 5 | `ov11_F_27CC` | 622 | 21 / 0 | 60 A4-relative | 0 | No | 40-reference cap and one incomplete natural local interval |

The first three are the strongest strict-function candidates in this size band: their callees are all independently identified A4 call stubs, their data references are all A4-relative, they have no pending same-node dependencies, and their same-node unit is ready. The only ranked-loop obstacle is the configured 40-reference cap; it is a prompt/admission bound, not an unresolved relocation or data-ownership claim. All three have zero entries in the function evidence `relocations` list.

`ov04_F_149C` is the best special-case candidate. Its 688-byte function ends at offset 5964, exactly where the first of 14 referenced printable candidates begins. Those referenced starts form a contiguous sequence through the final string at 6160; its text plus NUL ends at 6177, and the next discovered function, `ov04_F_1822`, starts at 6178. This makes it a plausible `--owned-code-data` tail, but the string evidence still labels these as printable candidates, and the final byte/boundary needs explicit proof. The 14 PC-relative literals must all be source-produced and match this natural tail before any function-plus-data proof is available.

## Nearest natural unit

`ov11_F_27CC` has no pending callee, but its only same-node call is to the already recovered `ov11_F_25D6` (34 bytes; call site `0x27FC`, target `0x25D6`). The direct-call interval is `0x25D6..0x2A3A`, 1,124 bytes. It contains `F_25D6` (34), `F_25F8` (54), `F_262E` (54), and `F_27CC` (622), plus a 360-byte unassigned gap between `F_262E` and `F_27CC`. The first three functions have recovered sources. That 360-byte gap is the specific layout obstacle behind `same_node_unit_ready=false`; resolving its ownership and natural contribution would make this a plausible next unit. It would still exceed the current 40-reference queue cap through its 60 A4-relative references.

`ov10_F_2FA0` is a weaker second unit candidate: its two local callees (`ov10_F_1F90` and `ov10_F_320C`) are recovered, but they span a wider and more fragmented same-node interval. It also exceeds the 40-reference cap with 66 A4-relative references.
