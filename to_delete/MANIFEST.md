# Quarantine manifest

Retired material lives here, outside all discovery and canonical inputs (`tools/repo_paths.py`). Review it, then delete it manually. Git history keeps every file.

## 2026-10-15 reassessment

All paths below moved under `to_delete/retired-2026-10-15/` with their original relative paths.

### Fleet orchestration

Supervised Haiku fleet orchestration. The C frontier is drained; every remaining target is blocked by a named structural blocker. Live compile-queue, file-lock and resident-recovery tests were kept (tests/test_compile_queue.py, tests/test_resident_recovery.py).

4 files, 190588 bytes.

| Original path | Bytes | SHA-256 |
| --- | ---: | --- |
| tools/fleet.py | 115094 | 6888f838e6297c57388d1880f9f6d33adf27241c3a0edb75a823379be74d92e1 |
| tools/fleet_regions.py | 16964 | 84d117ec677f3b3eace4667044916df3e19bf18d2da65146490387bb3fb723f4 |
| tests/test_fleet.py | 47711 | d1d031ae9697f6c8a5c14882fd09ee06f33dea1f5f27172753b97ec6eb79b91b |
| docs/fleet.md | 10819 | 88881307660d2907e078bd49420e3aafef85a4fa6e4ccadbf0009ca32d9ffb19 |

### Local-LLM proposer stack

Local-LLM proposer stack. Zero promotions in calibration (LOCAL-GRINDER-QUALITY-001); workers are now Codex sessions.

13 files, 85423 bytes.

| Original path | Bytes | SHA-256 |
| --- | ---: | --- |
| tools/local_grinder_smoke.py | 3026 | 8c4a09bd6666563727aaa9191a4d0b19d00e049ab1ae7696735f63cab067b3d9 |
| tools/local_model_proposer.py | 7784 | 628e8a8ed9ff172151b058dacb1634ca74bf6d8e6fe18d35bda270bfbf0c1deb |
| tools/local_model_server.py | 7078 | dd744dfa90171940b1331d628700c3b8a80681ffd1da96d0557557bc470f5566 |
| tools/local_http.py | 1941 | 5818e58203695c789486f51ea59045148203b7df91e890aa65194f6d5bf52f2e |
| tools/local_proposer.py | 5414 | 2468ac14eb85606641633042d003a69e07064b6db65c506d2487d2074eaf7a2f |
| tools/model_proposer.py | 7259 | deb4294f31d4ca68fb992f27a5e37796c609b7a24994606e3276f642b9a4c6c1 |
| tools/setup_local_model.py | 3439 | 5a1c6194e01359845ad2697f515751fadb9fcfac66e8887c2012a1250f12ccd5 |
| tools/gpu_telemetry.py | 2002 | 68ea8cee898c851cd9d7b8e9e925458858bc669b9777b83dc183e9ec5cbc717d |
| tools/local_fact_pack.py | 7215 | 9c46c4236676ae85ce9cf0c3d72c546200e5f12fe09195ca7081b9d7cfef7352 |
| tests/test_local_grinding.py | 15173 | 8455f46eb5eff4287a402a523dc7fe191dd94427ccb271d160e853971130f527 |
| tests/test_local_proposer.py | 2594 | 886d80b77ded9a26b0e0404894e871df0df96fd6740e2c9ffdf16f38b4bda739 |
| tests/test_model_proposer.py | 7882 | fc1fa9400b78996a1f65d05dd49590dfed9e44adf5aa622d7ac30230349e6c99 |
| evidence/experiments/local-grinder-calibration.json | 14616 | a6d9497dd386fd41aa6bb16563e38bab82ecf724e3a63808aed729373d63d8fb |

### DOS secondary-oracle pilot

DOS secondary-oracle pilot. Never an input to Amiga acceptance; its tools only wrote to build/. The DOS executable stays in assets/dos as a possible behavior reference for the port.

18 files, 1285314 bytes.

| Original path | Bytes | SHA-256 |
| --- | ---: | --- |
| tools/dos_capstone.py | 1181 | 3411cce77e0c35c62a2426d70f7048b7f789d9a9da1e89641959a1cbf731a82f |
| tools/dos_cross_probe.py | 12336 | 7347124af5e2d4c9685369d06aeeaef47c50b72acacd21544c082ab77d89b633 |
| tools/dos_functions.py | 5514 | 2c11f7c1f10e3a65fdfa0978033188bc17c7678a1d8d0d8968a4e1c26dd68706 |
| tools/dos_pair_receipt.py | 4624 | df223e7bce478b640d698cc248990001b1530814d75d119f4f1dab42fe1772b2 |
| tools/dos_specimen_receipts.py | 4434 | b8ecb496a7079e3779f968344179ba41d05eebbc6dadda18c4bc4e993014b9f2 |
| tools/dos_structure.py | 8630 | e3abca25247345e8528935ff191c57c7412a033ae03869bf60e4a6206e8e5cbe |
| tests/test_dos_secondary.py | 1303 | 00d59de34b8f0186fe181346fd4a0a875ea2dd6440e327703c86c2086c47cb74 |
| docs/dos-secondary-oracle.md | 5401 | dd57d5f55b4a4c0eae12274233700be89722708d4e43fce0fd320c516f4e4e9f |
| docs/fixup-and-dos-assessment.md | 7442 | a820020cedc9f7b9ce0adfd7395c1ee65a81221bb45909b3c054dfc9aecc4d9f |
| evidence/dos/correspondence.json | 3236 | 4f6216b5a51598512ea988385f361ba24eed3cd9bb2f6c6ca42033fa4e5d4010 |
| evidence/dos/cross-probe-os.json | 8624 | a9f565bb840ccd3a96ad6b31b24a065c4ebc84ed17fb49434acf86121a72be12 |
| evidence/dos/cross-probe.json | 27247 | de5d75bf5e7a490a82c03e573e335f1589df4dfb88869d006acb8091c541f0b5 |
| evidence/dos/function-census.json | 946045 | 3fceded9547f1639539af20df67ca83535c00d64549e615e861f8bf8307e48e7 |
| evidence/dos/pair-receipt.json | 12174 | e6b707960e12d71700eecac6afa12e0edff8c202eb73eb37342e49c32d54f70e |
| evidence/dos/specimen-receipts.json | 5682 | 9556b7652009facc9e607da5f7e5b6dac61bb016fd46e13fbebbe2a0fc32c76e |
| evidence/dos/structure.json | 229094 | 46fa314eec1a700896f1af8c64d290c5ec599e518d0d66d6eb2c04245245590e |
| evidence/dos/toolchain.json | 1935 | 08360654e3f77984a802a0eb2061a515924a2742bfcafbd6de7935a207f961bd |
| evidence/rules/dos/ov10_shared_pair.c | 412 | 5aa33392996f34032bc41569d112e68fbf23d32f120ed1de91a515e39e9a39b6 |

### ov11 cycle and frontier audits

ov11 cycle-gap and overlay-frontier audits. ov11 is exact apart from a 2-byte terminal gap; the audited windows are owned by canonical complete-C objects.

7 files, 33730 bytes.

| Original path | Bytes | SHA-256 |
| --- | ---: | --- |
| tools/cycle_gap_audit.py | 3219 | 42edcbc3ae4724c132362ac8bd1ae8de6a08b44db8d3caff8ac6646060902533 |
| tools/cycle_layout_gap_audit.py | 6974 | 6d8cfdc463f7fa46870aa1f5af3b0f8eada34929eb1ae6d0e91024dc127c01f8 |
| tools/overlay_frontier.py | 7750 | ea39648bb44de47b7848b5ae226a9b1d7449845a2ce07c6b1ceb1147b56785df |
| tests/test_cycle_gap_audit.py | 794 | 637a3da46e73aefa9eb6c0729fcaa74287ee61ac0fe7b6458757c8f2ecf79fd1 |
| tests/test_cycle_layout_gap_audit.py | 3089 | 72523d7a6b2240739925937942c13dc8caf3581721e24da0f55f3040aeca588e |
| tests/test_overlay_frontier.py | 1078 | 63c5e22af91b28d1beae52a697cd268ea1c570f11bce6403aa5d49ddbfa33989 |
| evidence/experiments/linker-cycle-layout-frontier.json | 10826 | e196bbdbeaaf2df078b9e057cba3ed5aa82b5024daad671ff99a3f05725af0d6 |

### Stale documentation

Stale documentation: the 2026-10-05 consolidation checkpoint, the grinder/local-model narrative, the recovery-planning note, and placeholder overlay/asm READMEs that said no source existed.

17 files, 32649 bytes.

| Original path | Bytes | SHA-256 |
| --- | ---: | --- |
| docs/CONSOLIDATION.md | 3933 | 3c62f40c90001e81372817f61352b8bce093d10c02895645eadd5a9a7237c7fb |
| docs/grinder-pipeline.md | 21065 | fda6644085b57310fd460bc118b1a34427453f51990457adbd3e8039c7715db7 |
| docs/recovery-planning.md | 3248 | f135da1030f9db142c3607b2b10dcce3535746c32ae6f34dbaed95ab1ae1afe9 |
| src/overlays/ov03/README.md | 325 | 0cb1bdd77fa85afb3b6b6b850498a3b69fafa3553eee35cb090ef8f6d1232cb8 |
| src/overlays/ov04/README.md | 325 | f0571866c4058ae56dfda8ccbe947f41d1a7749fc6966fe0a8b3c535dc7563f2 |
| src/overlays/ov05/README.md | 325 | 1dbccd4fef858970e9f1129f901c78977aeae0cfa1a2fd1e2442c57e31ee92cc |
| src/overlays/ov06/README.md | 325 | 48b101c87722a012e7216f757a1d3b7300afdf4baadd5781393cfc1e23dd3643 |
| src/overlays/ov07/README.md | 325 | a072a218670d4a1b743fa2de97fef59ec5dc4b8d3724c657a02895f90c7833e6 |
| src/overlays/ov08/README.md | 325 | fca5bf70719260de58300c4a9b91f8e9188fa5846240dd66efef02cf0e1f6262 |
| src/overlays/ov09/README.md | 325 | 24ec6b78602e766cc72151b26b4f0108804c1d5a8f1c424a1a75a40c95a5793d |
| src/overlays/ov10/README.md | 326 | fa0a01f438e6788f20c14273cfdcc4201f0552f16268ff5382a303c38707d713 |
| src/overlays/ov11/README.md | 326 | 9134951e6fedae578af325463fc58d822dcc59a41116a4948352c8b2673a903a |
| src/overlays/ov12/README.md | 326 | d3cdea1dadb286e702a2d10f2e1b23f7431777328fa54622a18c8f61e9880e3f |
| src/overlays/ov13/README.md | 326 | dc41e162822b6dd5edfbf9d83c358920573cf57f9504b87016322dbdb69e70af |
| src/overlays/ov14/README.md | 326 | 9e68556ed0306f2f5061c0480612c86bf8cd2701b6cbe21a8996c76da516385a |
| src/overlays/ov15/README.md | 326 | b638d3f0cd9223831de569485091cec3c319b27f5748231ce988c40009f79235 |
| src/asm/README.md | 172 | 766e1d3c6c460a45e9f6de0ea9860024a675306dab029b7451786dcd4407d955 |
