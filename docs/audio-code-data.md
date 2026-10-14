# Resident audio DATA in CODE

The curated classification input is `evidence/data-facts/resident-audio-sequences.json`.
It records H0+[0x13B8,0x2816) as audio sequence bytecode inside the historical CODE
container. It grants no recovered-source or accounting credit. Historical source
language, filename, object/TU membership and author/provider remain UNKNOWN.
The six zero alignment candidates and unreferenced continuation at 0x19F7 remain
explicit in the fact and its replay output.

`audio_sequence_data.load` verifies the fixture/extent hashes, complete reviewed
interpreter and adjoining code anchors, dispatch and selector relocations, stream
headers and every bytecode pointer field. It rejects accepted-source overlaps and
positive executable entry/control-flow evidence. The census records this as DATA
with UNKNOWN ownership. The function census excludes it from executable seeds and
retains raw relocations as typed data references. Its input identity and snapshot
cache depend on the curated fact's content and presence. Regeneration removes52
phantom functions in this interval (including the32 reviewed in [13B8,1BA6)) and
therefore removes their review-ranking entries; coverage/debt cannot gain credit.

After reviewing and applying the change, regenerate with the existing tools,
never by editing generated ledgers. A supervisor should run the function census,
census write/check and the full regression gate, with the usual type/hybrid
refresh steps required by the repository's promotion-boundary workflow. No ledger
or accounting write is part of this patch or the isolated experiment.

The independent score recipe is `evidence/rules/audio-score-16e4/recipe.json`;
its human-readable assembly is `score.asm` beside it. `audio_score_recipe.source`
rederives that exact source from named notes, durations, channel and player-state
commands. The assembler emits the jump from a local `_score_pattern` label and
natural word alignment, without ORG, numerical historical addresses or an oracle
byte array. The source emits72 CODE bytes, zero object DATA/BSS, pattern+18 and
one long pointer at+68. The pinned linker independently allocates a minimum4-byte
BSS hunk; it is link-only allocation and receives no provider/data credit.

Prepare and run a fresh ordinary isolated `aztec_worker` job containing only the
assembly source and these explicit commands:

```text
Old1:bin/as -o score.o score.asm >score-as.log
Old1:bin/ln -m -t -o score.exe score.o >score-ln.log
```

Then use the isolated bounded route:

```text
python tools/check_data_contribution.py --isolated --job build/worker-jobs/NAME
```

It audits the full pinned tool inventory, exact source/command/script/mount
recipes, guest OS copies, artifact inventories and hashes, complete AJ object,
natural linked extent and all labels. Independent semantic encoding also rejects
consistently rehashed recipe/source/receipt changes with stale object output.
All68 ordinary bytes of original [16E4,172C) compare exactly. The remaining four
bytes compare by the independently established local label identity: original
H0+1728 -> H0+16F6; candidateH0+68 -> `_score_pattern` at+18. No other field can be
normalized. Missing/extra relocations, wrong addends/targets, clipping, additional
CODE content and nonlocal bindings reject.

The successful verdict is `EQUAL_CANDIDATE`, not promotion. The report explicitly
retains source/accounting acceptance=false, proof_level=null and unknown historical
object ownership. Ordinary function acceptance and its CLOSED_CFG gate are
unchanged. Whole resident layout/TU provenance remains unproved.

`tests/test_audio_code_data.py` includes strict negative controls and a complete
in-memory function-census/review-ranking integration check. Tests use independently
produced pinned score object/link fixtures. Set `AUDIO_DATA_JOB` to a fresh score
job to include the full producer audits; without it those nine explicit controls
skip. No compiler fixture is sourced from original executable bytes.
