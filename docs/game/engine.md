# Resident engine: archives, decoding, graphics, memory

What the recovered code shows this part of the game doing. Names are the ones in `recovery/names.json` (applied in src/); mechanical names (`ovNN_F_XXXX`, `G_h01_XXXX`) are things not yet understood well enough to name. First written from the 2026-10-18 naming review.

This resident code is the shared machinery behind what the player sees between game states. A map entry packs an overlay selector into its low nibble and passes the remaining value to that overlay (`run_location_overlay`). The overlays choose which location, clue, menu, or result is on screen; these resident routines provide the shared display and resource operations. They load archive images, draw text, prepare sprites, and update the display.

## Screens and presentation

The display is a 320-by-200, five-plane bitmap. AV setup creates two screen bitmaps and a separate bitmap used as an archive-image destination (`initialize_av`). `switch_display_buffer` switches the screen bitmap attached to the RastPort, waits for a viewport boundary, and loads the view, so drawing and display changes follow the original buffer order. `load_scene_graphic` reads an indexed archive image and, for the cases that draw a scene image, blits it to the active screen bitmap.

The display uses a 32-word 0RGB palette. `copy_palette_to_color_map` copies palette words into the ColorMap color array; `copy_palette_to_copper_lists` copies them into both Copper lists. `fade_palette_to_target` approaches a target by moving each color component one nibble at a time, while `fade_palette_to_black` steps the current palette toward black. These transitions are visible screen fades, not palette metadata stored in each bitmap record. The source that chooses the fade target depends on the screen being loaded (`show_clue_screen`, `load_scene_graphic`).

`draw_text` draws a string at the requested x coordinate and six pixels below the supplied y coordinate, using the current RastPort pens and draw mode. `draw_decimal_value` formats an integer as decimal text and can shift the x coordinate to align the digits. The clue page uses these helpers to show a Junior Woodchuck Guide heading and one topic line, then calls `show_random_clue` for the selected topic (`show_clue_screen`, `show_random_clue`). The strings identify mountain climbing, jungle survival, nature photography, or cave exploring; the functions select them from an argument value.

Sprites use an embedded Amiga BitMap view. `build_sprite_mask` clears and builds a mask with the blitter, and `draw_masked_sprite` sends the bitmap and mask to the graphics.library blit operation before freeing the temporary mask. Their caller supplies destination position, width in eight-pixel units, and height. The code does not establish the meaning of the final byte at sprite-record offset +0x34; it is used as a source offset multiplied by the bitmap row stride.

## Archive resources and codecs

An `.arc` file begins with a little-endian record count and a table of little-endian 32-bit record offsets. `arc_read_index` reads that index, and `read_arc_record_header` seeks to an indexed offset and reads a 16-byte record header. The header gives a stored byte count, a kind, and kind-specific words (`formats/arc.md`). The loader dispatches kinds in `load_arc_record`:

- Kinds 1 and 2 are five-plane RLE bitmaps. Tokens encode either a run of literal bytes or a run that repeats one byte; `decode_rle_bitmap` writes the resulting bytes plane by plane and row by row.
- Kind 3 allocates a text block and reads its stored bytes. Its exposed `TextBlock.length` comes from the low word of the stored-size field.
- Kind 4 uses the LZW decoder (`lzw_decode`, `lzw_read_code`, `lzw_append_output_byte`). Codes are packed low-bit first, start at 9 bits, and grow to 12 bits as the dictionary fills.
- Kind 6 allocates the size in header word +14 and reads the stored byte count. If those sizes differ, the source does not initialize the unused tail.

The RLE and sample routines consume bytes through a shared 1024-byte refill buffer (`arc_next_byte`). The RLE decoder receives no header length argument, so one supplied record consumes beyond its declared span; this observed behavior is documented in `formats/arc.md` and should not be silently changed. Separately, `initialize_audio_and_input` and `arc_read_index` establish that `DT1:dt1.as` has a count/offset index. That proves an index read only; its record payload meanings remain unknown (`docs/platform.md`, `formats/as.md`).

## Memory and frame timing

AV setup requests a contiguous cleared chip-memory block through `initialize_chip_memory_pool`; teardown releases it through `free_chip_memory_pool`. The tracked region records its address bounds, a free-byte value, and a linked list used by the memory reports (`free_memory_checked`, `report_memory_usage`, `dump_memory_list`). Archive-created bitmap and text records allocate from the game memory header and have matching cleanup helpers (`allocate_bitmap_planes`, `free_bitmap_planes`, `allocate_bitmap`, `free_bitmap`, `free_archive_bitmap`, `free_text_block`). Allocation failure and invalid frees take the existing error paths (`report_loader_error`, `allocate_memory_or_report`, `free_memory_checked`).

The frame clock comes from the vertical-blank server `vblank_server`: each VBlank increments `game_frame_tick`, invokes the registered game callback, and then updates frame-based audio state. `wait_for_next_frame_tick` waits until that tick changes. This means a port must preserve the callback order and the frame at which a wait resumes; the code does not use a free-running host timer as its game clock (`docs/platform.md`, section `Timing and interrupt model`).

## Deliberately unnamed items and suggested comments

- `resident_F_4184` is clearly a packed adaptive-delta sample decoder, but I left it unnamed with the audio functions as requested. Suggested future name if audio is brought into scope: `decode_adpcm_samples`.
- `resident_F_0976` skips writes for carriage returns but still advances the destination pointer; after the loop it steps back once and writes a terminator. Its exact intended line-normalization rule is unclear. Suggested code comment: `CR bytes are not copied, but the output pointer still advances for them; preserve this observed behavior.`
- `resident_F_1306` waits for bit 0x40 from the input poller. The meaning of that action bit is not established here, so it remains mechanical with input names untouched.
- `run_location_overlay` sets bits in `G_h01_46C8` after loading selected overlays, but no accepted consumer in this path explains the flags. The global remains mechanical.
- The palette arrays at `G_h01_1526`, `G_h01_1926`, `G_h01_1966`, and `G_h01_19A6` are fade targets for particular screen paths, but the source does not establish stable scene names for all of them. Suggested comment: `Target palette selected by this caller; exact scene association is caller-specific.`
- `G_h01_0971` aliases the low byte of the five-plane count at `bitmap_plane_count`; `G_h01_A7D8` aliases the low word of the stored-size word at `arc_record_stored_length`. Kind 3 reads the latter as the text-block length. I named the full globals and left both aliases unnamed. The other record-header words have kind-specific or unresolved meanings, so I did not give them universal names. `G_h01_ADCF` is the low byte of the LZW prefix-walk word at `lzw_dictionary_walk_code`; it also remains unnamed as a separate symbol.
- `G_h01_53E8` is assigned during memory setup and later reused for a ColorMap pointer. It remains mechanical because its role changes across setup stages.
- The BitMap flag/padding bytes and sprite record byte +0x34 remain unnamed. The latter is multiplied by row stride for the blit source argument, but the code alone does not establish whether it represents a row, frame, or another source offset.
- The CLI/Workbench startup helpers (`resident_F_2E30` through `resident_F_3008`, `resident_F_766C`, `resident_F_77A4`, `resident_F_8534`, `resident_F_8552`, `resident_F_8640`) are outside the requested presentation/resource/memory/timing group. Their mechanical types and original source ownership remain uncertain. Existing audio and input names were not changed.
