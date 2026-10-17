# Original-game traces

A trace records the original game after restoring a pinned WinUAE save state. Each sample contains the complete resident DATA+BSS allocation (46,048 bytes), a SHA-256, loaded-overlay bases, the interrupted execution context, and the CIA-A tick and cycle clock. `trace.bin` is the byte witness; `index.jsonl` carries frame/context metadata; `named.jsonl` is a derived typed view. These files are observations of the original executable, not a source match or a behavioral proof for another build.

## Frame boundary and layout

Sampling stops at the first instruction of the game's live Exec `IT V Blank` interrupt server. The server address comes from WinUAE's live interrupt-server listing. At each sample the CIA-A TOD counter must advance by exactly one tick. Raster position is recorded because graphics work can delay interrupt delivery; line zero is not assumed. Scripted joystick input for frame N is applied after the previous server entry and the resulting resident state is sampled at the next entry.

Resident CODE is located from a unique relocation-free signature. Its 528 DATA relocation fields derive the loaded DATA base; DOS BPTR segment links and allocation headers cross-check the measured HUNK addresses. Each frame is H1's 46,044-byte allocation (11,956 initialized bytes plus 34,088 zero-fill bytes), followed by the separate four-byte H2 BSS allocation. Overlay trampoline entries and loaded overlay bases are recorded as context, not folded into the fixed resident frame.

The schema is generated on each run from `recovery/data_model.json` and `recovery/names.json`. It preserves evidence basis and only decodes typed, bounded fields. Pointers remain numeric Amiga addresses and are never dereferenced. Uncovered bytes remain in the raw frame; their coverage complements are not object boundaries.

## Limits

- Reproducibility starts from the same checkpoint. Cold boot, startup timing and unrelated WinUAE state are outside this replay claim.
- The trace is specific to WinUAE 4.10.1, the recorded A500/PAL profile, media hashes and a modified KS1.3 ROM dump. The ROM modification is recorded in `docs/toolchain.json`; it is not an unmodified Commodore ROM.
- WinUAE's restored profile exposes an RTC despite the cold-boot `rtc=none` setting. Any scenario that reads RTC needs a controlled clock.
- Resident DATA+BSS and selected interrupt/overlay context are captured. Mutable heap objects reached through pointers, custom-chip state, complete machine memory, and audio PCM are not comprehensively captured.
- Raw addresses, BPTR handles, runtime buffers and trampolines are witnesses for this run. They are not automatically comparable across independently linked builds.
- A deterministic original replay is evidence about the original only. It does not establish source equivalence or prove the reconstruction complete.

## From-source build comparison (b)

Boot an independently compiled and naturally linked build on a private volume with the same machine profile, but create an independent checkpoint for that build. Never restore the original `.uss` into the reconstructed executable. Derive that build's HUNK bases and global addresses from its own link map and relocations, then locate its live VBlank server. Compare a separately specified typed projection keyed by canonical global/field identity. Normalize pointers and handles only through independently named targets, object identities and explicit ABI evidence. Keep untyped spans visible as unassessed evidence. Natural link order, padding and whole-file identity are category C and do not gate behavior recovery. Report the first semantic or timing divergence after reproducibly matching initial game/RNG state.

## Later port hook (c)

Add a test-only hook at the equivalent VBlank/game-model phase. Specify input-before-step and state-after-step ordering. Serialize fixed-width fields in canonical byte order; retain FFP bits where they define behavior, include RNG state and logical scene identity, and add mutable entity/heap state with stable object IDs. Replay events on a virtual frame clock, independent of SDL wall time and host devices. Disk reads, decompression and fades consume frames in the original, so strict acceptance needs a deterministic test-backend completion schedule for platform work or an explicitly agreed scene-milestone contract with aligned recordings. Add render-frame and PCM-interval sidecars, then widen cases to movement/collision, markets, audio, endings and error paths. This trace package adds no SDL3 code.

## Commands

```powershell
python tools/game_trace.py prepare title-checkpoint
python tools/game_trace.py trace title-to-money-bin-a --frames 6000 --input evidence/trace/title-to-money-bin.json --checkpoint build/trace/title-checkpoint/checkpoint.json
python tools/game_trace.py compare title-to-money-bin-a title-to-money-bin-b
python tools/game_trace.py decode title-to-money-bin-a 5000 --all
```

Checkpoints contain original memory. Keep `.uss` files inside ignored `build/trace/<RUN>/` directories; never add them to a patch or commit. Each run has a private INI, config, TMP/TEMP, ROM copy and read-only disk copies. The checked-in input covers a title-to-Money-Bin scenario; its exact frame count is 6,000.

## Emulator settings

Runs are headless (`headless=true`, `gfx_api=directdraw`): no Direct3D, no GPU
rendering, and about 30% faster (a 240-frame replay: 12.0 s to 8.5 s, byte
identical). Screenshots need rendering, so headless runs record state rather
than images. Run one WinUAE instance at a time and batch probes into one
session; `tools/game_boot.py` boots a from-source build and collects registers,
a symbolized stack and stack-referenced strings before it stops the emulator.
