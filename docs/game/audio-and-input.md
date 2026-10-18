# Audio driver, palette cycling and input

What the recovered code shows this part of the game doing. Names are the ones in
`recovery/names.json` (applied in src/); mechanical names (`ovNN_F_XXXX`, `G_h01_XXXX`) are
things not yet understood well enough to name. First written from the 2026-10-18 naming
review; the driver is the reconstructed 68000 assembly in src/recovered/asm-reconstructed/
(the SDL3 port runs it translated instruction by instruction, docs/sdl3-port.md).

## Start-up

`initialize_audio_and_input` opens input.device and adds the game's input handler
(IND_ADDHANDLER), installs the four Paula channel interrupts
(`audio_channel_0_interrupt_record`..`3`, SetIntVector) and the VBlank server
(`vertical_blank_interrupt_record`, AddIntServer 5), and clears the driver
(`clear_audio_driver_state`). `shutdown_audio_and_input` undoes it in reverse.

## Playing a sound

The game asks for every tune and effect with `play_sound(n)` (about 290 call sites). For any
`n` whose low byte is not 8 it falls through into the driver's start routine: score `n` is
picked from the selector table (`audio_sequence_pointer_table`, pointing at the typed table
`G_h00_6200`); the score's header byte names the channel and a priority, and a score only
replaces the one playing on that channel if its priority is at least as high. `n` = 8 instead
stores a period offset (`noise_period_offset`) that the random-period note command uses.

## Every frame

`vblank_server` increments `game_frame_tick`, runs the palette-cycle callback
(`dispatch_palette_cycle_callback`) and steps the four channels. For each channel record
(`audio_channel_0_state`..`3`, 0x4C bytes each, reached through
`audio_channel_0_state_pointer`..`3`) it counts down the current note; when it runs out, the
score interpreter reads the next bytes: a byte below 0x80 is a note (index into
`audio_note_period_table`, plus the channel's transpose), a byte with bit 7 set is a command
dispatched through `audio_score_command_handlers` (44 entries: tempo, envelope selection,
calls and returns, loops with counters, jumps, transpose, vibrato and pitch ramps, random
notes, master attenuation, sound on/off). The envelope stepper (`audio_envelope_state_handlers`,
six states that step the level by a delta toward a target and then read the next envelope
bytes) computes the volume, from
which `audio_global_volume_attenuation` is subtracted before it is written to AUDxVOL, if
`audio_volume_output_enabled` is set.

## Samples and Paula interrupts

A note selects a sample descriptor (`audio_sample_descriptor_table`): a list of blocks, each a
repeat count, a length and an address. The note loads the first block into Paula; each
channel's interrupt (`audio_channel_0_block_interrupt`..`3`) fires when Paula starts playing
a block, counts the repeats down (`audio_channel_0_block_countdown`..) and then loads the next
block through the cursor (`audio_channel_0_sample_block_cursor`..). A negative count ends the
list, zero stops the channel. Random-noise samples are generated at start-up with
`generate_audio_noise_byte`.

## Palette cycling

Some scenes animate colours: `configure_palette_cycle` selects one of five callbacks
(`palette_cycle_callbacks`, index `palette_cycle_callback_index`) and a speed. Each frame
`advance_palette_cycle` subtracts the speed from `palette_cycle_frame_countdown`; when it
underflows, the cycle position (`palette_cycle_word_index`) moves back by one and a run of
colour words from the scene's table (`palette_cycle_descriptors`, `palette_cycle_values_1`..4)
is written straight into the colour MOVEs of the copper list.

## Input

Two paths. Keys: the input handler (`input_device_handler_trampoline` then
`input_device_event_handler`) appends each raw key event to a 128-byte ring
(`input_key_ring_bytes`); an event of class 16 (IECLASS_DISKINSERTED) sets a flag byte in
the ring that the recovered source calls `quit`.
`drain_input_key_queue` consumes the ring, tracks the keyboard fire key
(`keyboard_fire_key_held`) and translates raw codes through `raw_key_code_translation_table`.
Joystick: `poll_controller_and_keyboard_input` reads JOY1DAT and the fire button (CIA-A PRA),
maps them through `joystick_action_translation_table` to a direction/fire action, merges the
keyboard's action, and handles the special keys - P pause, Escape/Q quit
(`input_quit_key_seen`), S sound toggle (`sound_toggle_state`, sound commands 0x7F/0x7E).

Randomness: `seed_random` stores the beam position plus the frame tick in `random_state`, the
16-bit LFSR state that the random routine `resident_F_463E` advances (still original 68000
code). Because the seed depends on the beam position, two runs differ unless it is pinned
(tools/game_boot.py --rng-pin).

## Open questions

- With the build's selector table, S sends 0x7F (sound off) and 0x7E (an empty score), so
  sound could not be switched back on; 0x80 is "sound on". The table's first 8 bytes are
  still unrecovered (RAW_ORACLE_DEBT), which may shift these indexes - check against the
  original before naming the toggle further.
- `resident_F_1306` waits for bit 0x40 of the poll result; what that bit means is not shown.
- Channel record offsets 0x40 and 0x47, and the VBlank record's data target `G_h01_B27E`.
