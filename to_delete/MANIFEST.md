# Quarantine manifest

Historical quarantine contents were manually deleted by the user before this push. No historical material is reintroduced here. The consolidation originally quarantined 7866 files; see `../evidence/consolidation/audit.json` for the compact summary.

The safety check began restoring Git copies before the user clarified their deletion. Those copies remain locally under ignored `build/consolidation/restored-quarantine/`, together with the detailed audit. They are excluded from the push and from active discovery.

Future retirements belong here with their original relative paths and a size/hash/reason entry; no normal tool may consume them.

## Rejected automatic-unit receipt - 2026-10-05

Retired to `rejected-unit-ov04_F_1302-6737bb563080874a/`. This producer version retained filtered harness source instead of raw TU declarations; the strict proof consumer rejected it. The accepted replacement uses a new immutable producer identity.

| Original path | Bytes | SHA-256 |
| --- | ---: | --- |
| recovery/units/ov04_F_1302/14532338a3c9c896afdc8c58b37f7cea677695673733d8045f1d65378dd947be/6737bb563080874a/receipt.json | 154810 | 5a83304f1593c609e5f43a86b3067e819a7629e876ceedbcc82735576d691415 |
| recovery/units/ov04_F_1302/14532338a3c9c896afdc8c58b37f7cea677695673733d8045f1d65378dd947be/6737bb563080874a/unit.c | 15796 | 5fb47a3f5e716b9de904d7f89646948d7e8bf9a734106fb087efa85a5e3c7d36 |
