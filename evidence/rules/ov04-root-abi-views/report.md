# Root COMMON ABI frontier

Baseline and finish HEAD: `87f86c63457da586a6f88a016320de9bf505f12c`.
Ledger SHA-256 unchanged: `f68e97864dcc7f1cb5ba9685efa18fcd240387d7ea24740030ef53ace6a9afa4`.
Budget used 2/2, self-authored compiler controls only; no canonical writes.
Categories DATA_OWNERSHIP / OBJECT/TU_LAYOUT. No layout or node proof granted.

## Independent ABI and call facts

Pinned SDK `graphics/gfx.h` defines BitMap; `graphics/view.h` defines RasInfo.
`exec/types.h` makes SHORT/UWORD 16-bit. Fresh aztec36 controls emit
sizeof(RasInfo)=12, fields BitMap+4/RxOffset+8/RyOffset+10;
sizeof(BitMap)=40, Planes[8]+8. Hashes and source lines: provenance.json.
This establishes ABI compatibility, not historical release/TU/name provenance.

Original resident_F_8AF6 loads stack+4 into A0, stack+8 into D0-D2,
G_h01_5374 into A6 and jumps -390(A6), exactly the argument/vector pattern of
pinned graphics.arc `_InitBitMap`. Accepted F1E36 calls at h04+2168/21E8/227E
initialize bases 2EC0, 2EE8 and a separately allocated 0x28-byte bitmap.
First two plane writes start at 2EC8 and 2EF0 respectively. G2EE8[8] and scalar
G2EF0 are accepted codegen views, not proved original storage boundaries.
Do not collapse their distinct roles into one guessed alias.

RasInfo also has a consumer chain: F8B14 matches InitVPort (A0,-204),
F8B08 InitView (A1,-360), F8B3E MakeVPort (A0/A1,-216), and F8B5E MrgCop
(A1,-210). F1E36 initializes ViewPort at53B4 and stores &2EB4 at53D8 (+36),
the SDK ViewPort.RasInfo offset. It clears long2EB4, stores bitmap pointer at
2EB8, clears SHORTs2EBC/2EBE, and switches the bitmap pointer from2EC0 to2EE8.
This supports a RasInfo view independently of adjacency. ABI call facts are
retained in worker scratch; canonical source/proof and SDK provenance remain authoritative.

## Two natural COMMON controls

control1.c declares typed info/first/second externs, which the ordinary oracle
defines as uninitialized objects in its separate root harness. Assembly emits
`global info,12`, `global first,40`, `global second,40`. COMMON-relative symbol
offsets are0/12/52. Cache key
`ccc5c74407bb04b0b391476f69bd5cf7df6b319dd2869ea7d115d513d9c9bbd0`.
control2.c reverses declaration order; second/first/info emit at0/40/80.
Reversal is a negative order control: SDK compatibility does not force order.
Both H1 initialized40/allocated208, H2 allocated4; __H2_org=40. Logical-H2
symbols refer to folded H1 zero tail, corroborating the verifier convention.
Compact cache identities are retained in controls.json; full results remain in worker scratch.
No synthetic filler, fixed addresses, or original game bytes enter controls.

## Root frontier

Compatible ABI spans: 2EB4..2EC0, 2EC0..2EE8, 2EE8..2F10, total92 bytes.
2F10 is an ABI extent end, not a proved original object boundary. Source
ownership/order remains unknown. Original H1 initialized11956/allocated46044,
zero tail34088, H2 allocated4. Startup resident_F_75F2 points twice at2EB4
and clears (0x2149+1)*4=34088 bytes, independently corroborating the frontier.

Whole ov04 has185 H1 RELOC32 sites to63 offsets; only16 sites/8 offsets lie
in this cluster. Other references include initialized0970, COMMON46CA..46F8,
and COMMON5370..544A. Initialized resident call-vector/trampoline obligations
are additional. Exact relocation inventory: root-relocation-frontier.json.
Therefore these views cannot resolve raw ov04 equality by themselves. Actual
11956-byte initialized contributions and intervening COMMON objects must be
recovered naturally; arrays cannot stand in for unknown gaps.

## Curated shape and smallest next experiment

views.json records ABI views, field bounds and evidence basis
separately from unknown ownership/TU membership; DATA_LAYOUT_MATCH=false.
Such inputs can support derived metrics without directly editing generated
ledgers. Do not grant source aliases merely to keep old field proxies linkable.

Next: worker-local F1E36 variant with three typed base declarations and ordinary
Next/BitMap/RxOffset/RyOffset/Planes accesses replacing the eight field proxies.
Reverify isolated with unchanged dependency objects/export routing; require
all base+addend identities and complete exact code. This tests stronger
declaration views, not root ownership. Then recover real initialized root
contributions and intervening COMMON allocations with boundaries left unknown
until independent evidence exists. Budget exhausted; no additional controls.

Supervisor follow-up: typed trial 1 failed SOURCE_SHAPE; trial 2 cast the pointer before addition and matched exactly. The unchanged candidate passed normal promotion and its regression gate. See typed-trials.json and canonical F1E36 source/proof. This grants no root DATA ownership, original names, TU membership or natural node proof.
