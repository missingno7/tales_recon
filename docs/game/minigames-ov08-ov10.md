# Minigames: ov08 (mt.arc), ov09 (ps.arc), ov10 (the cave)

What the recovered code shows this part of the game doing. Names are the ones in `recovery/names.json` (applied in src/); mechanical names (`ovNN_F_XXXX`, `G_h01_XXXX`) are things not yet understood well enough to name. First written from the 2026-10-18 naming review.

These three overlays are self-contained game scenes loaded by the main adventure. Their archive abbreviations are present in the code, but the source does not establish expansions for `mt` or `ps`; this note describes their observed behavior without treating those abbreviations as titles.

## ov08: grid movement

`run_grid_movement_minigame` opens `DT2:mt.arc`, selects one of three character maps from a 21-column layout, loads the background and entity records, and runs the movement scene. The map has rows and columns used directly for floor and obstacle checks. The game polls the controller, updates player screen coordinates and action states, advances entities, and ends a life when the player falls; the outer loop starts with three lives and stops when they run out or the scene completes. `advance_grid_player_and_entities` contains the per-frame player and hazard transitions, while `draw_grid_visible_entities` draws the visible entity records.

The exact minigame title and the expansion of `mt` remain unresolved. Suggested comment only: `mt` may refer to a mine track; the scene uses a row-and-column obstacle map. The code itself supports the map and movement description, but does not contain a readable title.

## ov09: timed event selection

`run_timed_event_minigame` opens `DT2:ps.arc`, prepares a scene with twelve fixed screen positions, creates three live event slots, and enters a timed phase. The player moves a selector among three options with the controller and uses fire to record an eligible event. Each fire action consumes one of twelve attempts. `update_timed_scene_event_slots` chooses and advances events; `spawn_timed_scene_event` selects an event type and row from the spawn-mask table; `place_timed_scene_event_sprite` positions its sprite; and `draw_timed_scene_event_art` draws type-specific art. `load_timed_scene_route_indices` loads the route-point indices and `draw_timed_scene_status_panel` draws the status panel.

The `arg` passed to the entry point determines a bonus event type, with a random choice among eligible types. At settlement, matching recorded events add 500 and other recorded events add 50 to the displayed reward total, which is then added to the player's money (`run_timed_event_minigame`). Difficulty and elapsed rounds change the event spawn chance (`update_timed_scene_event_slots`, `spawn_timed_scene_event`). The source shows the selector, event state, attempt count, status panel, and payouts; graphics and names inside the archive provide no readable title here.

The expansion of `ps` is not established. Suggested comment: `ps` is the archive abbreviation used by this timed event scene; its full title is unknown. No character or event species is named from sprite IDs alone.

## ov10: cave maze

`run_cave_maze_minigame` reads eight lines of eight decimal values from `DT2:cavemaps.arc` into 64 cave-cell words, then loads scene graphics from `DT2:exp.arc`. Each word contains connection and state bits. The low four bits encode passages: bit 0 opens west, bit 1 east, bit 2 south, and bit 3 north. Bit `0x10` marks a visited cell and also identifies the initial player cell in the loaded map; bit `0x20` identifies the finish cell; bit `0x40` marks a special cell that routes through an event/ending branch. The cell word is read through both 16-bit pointers and a byte view at offset one; preserve that big-endian view when interpreting the data (`run_cave_maze_minigame`, `draw_cave_cell_connections`, `draw_cave_map`; the byte-order handling is noted in `docs/sdl3-port.md`, "The reconstructed assembly, translated" and the byte-order audit immediately above it).

The player moves between adjacent cells only when the corresponding passage bit is set. A second moving marker starts on a random cell and moves through open passages. Difficulty changes the time budget and map visibility. `draw_cave_map` draws revealed cells and their connections, `draw_cave_actors` draws the player, finish, and moving markers, and `draw_cave_cell_scene` draws the current cell scene. The code counts elapsed movement/idle time against limits of 64, 48, or 32, plays distance and directional cues (`play_cave_distance_cue`, `play_cave_direction_cue`), and can award 50 for certain traversal events (`play_cave_traversal_event`). Timeout calls `play_cave_timeout_sequence` for a timed sequence; the moving-marker and special-cell paths run separate sequences. Reaching the finish sets the returned result to one. When the result remains zero, the entry point displays "Launchpad McQuack saves the day!" and waits for fire input.

The cell words support precise names for the grid, player index, finish index, and moving marker. The remaining archive-loaded sprite records and several mode bits are not named because the source does not establish the depicted objects' identities.

## Coverage and deliberately unnamed

- `ov08_F_3F70`: it passes three indexed record arrays to `free_bitmap_planes`, but the semantic roles of those arrays and the helper's operation are not established by this subsystem alone.
- `ov10_F_320C`: it checks four low flag bits and draws four records after requesting the disk, but the code does not establish what those records depict.
- The `clear` field in `configure_timed_item_animation.c`'s local state structure is set to zero for two item types, but no scoped code reads it, so its meaning is left as `field_XX`.

Suggested comment only: `ov08_F_3F70` may update animation or position records because it passes paired values to `free_bitmap_planes`; this is not used as a name. The `ov10_F_320C` records may represent cave clues or objects, but their visual meanings remain unproven and are not named.
