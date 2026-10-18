# Minigame ov11 (jg.arc)

What the recovered code shows this part of the game doing. Names are the ones in `recovery/names.json` (applied in src/); mechanical names (`ovNN_F_XXXX`, `G_h01_XXXX`) are things not yet understood well enough to name. First written from the 2026-10-18 naming review.

The game enters this overlay through jg_run. It opens DT2:jg.arc, selects one of three indexed data sets, parses tagged text sections, loads graphics, and initializes the player and scene objects (jg_run, jg_load_level_resources). The code does not expand the archive tag jg, so this note uses “ov11 minigame” rather than assigning it a title.

The parsed text is section-tagged and line-oriented: section readers locate a letter tag, read a row count, then parse indexed integer records (jg_parse_c_section_header, jg_parse_l_section_records, jg_parse_p_section, jg_parse_m_section, jg_parse_f_section, jg_parse_grid_and_platform_sections, jg_parse_s_section, jg_parse_moving_object_sections, jg_parse_x_section). The visible tags include C, L, P, M, F, A, B, S, V, J, and X. J-section values are indexed by grid row and help select moving-object records (jg_parse_moving_object_sections, jg_update_player_state).

The playfield is a 41-by-4 grid of tile-record indices. The A section fills the grid, while B fills platform records; zero cells are treated as empty and nonzero entries select records (jg_parse_grid_and_platform_sections, jg_draw_visible_platforms). Rows are spaced 53 pixels horizontally and columns 32 pixels vertically. The camera follows the player through the horizontal world and redraws a 320-by-176 play area above the lower status band (jg_update_camera_scroll, jg_redraw_scrolled_scene_region, jg_draw_status_bar).

Input comes from the shared controller/keyboard poller. This overlay accepts mapped actions 3 and 7 for horizontal movement, 1 and 5 for vertical/action transitions, and 128 for another state change; it does not attach button labels to these values (jg_handle_player_input, jg_update_player_state). The player can board and ride moving platforms. A nonzero reward flag is collected on overlap, cleared, and adds 50 to total_money (jg_collect_tile_reward_and_check_fall, jg_update_player_platform_attachment, jg_follow_moving_platform).

The M section supplies actors whose state machine reacts to position, random thresholds, timers, and player proximity (jg_parse_m_section, jg_update_actor_behavior). F supplies events placed in horizontal pages, advanced over time, drawn in view, and checked against the player's rectangle (jg_parse_f_section, jg_initialize_events, jg_update_visible_events, jg_advance_event_records). P-section objects have timer and interaction states (jg_parse_p_section, jg_update_p_section_object). S-section records describe contact hazards: overlap changes player/hazard animation state to 45 and plays sound 98 (jg_parse_s_section, jg_check_player_hazard_collision, jg_update_hazard_state). V configures moving objects whose coordinates use bounded phase values and two lookup tables (jg_parse_moving_object_sections, jg_update_moving_object). X records become drawable triggers; touching one sets the overlay return flag, but source does not explain the returned value to its caller (jg_parse_x_section, jg_draw_end_trigger, jg_check_end_trigger_collision, jg_run).

Animation descriptors hold a sprite pointer, sprite state, frame delay, and horizontal/vertical coordinate deltas. The selector chooses sequences by player state/direction and a shared updater advances them (jg_select_player_animation, jg_advance_player_animation). The status band draws attempt markers, cash, and game day. On player state 7, the main loop either resets for another attempt while the counter is below three or exits; cleanup restores the prior archive handle and returns the overlay result (jg_run, jg_begin_attempt, jg_draw_status_bar).

## Deliberately unnamed

- ov11_F_21F8 resets counters and copies one pointer into four slots, but consumers do not establish what those values represent.
- ov11_F_405A only tests whether another record state equals 4.
- ov11_F_40AE clears a flag, delays, and plays sound 91; its gameplay event is unclear.
- ov11_F_45EC compares two indexed motion-record values; the intended predicate name is not established.
- ov11_F_4A92 delegates to a resident helper on an offscreen bitmap, but its meaning is unclear from this caller.
- ov11_F_5F2A combines interval checks whose exact geometric contract is unclear.

The 67 scalar members reviewed across seven field contexts produced 43 names; 24 stay mechanical. Descriptor offsets 8 and 10 remain unknown; platform offsets 8, 10, 40, and 42; actor offsets 0, 24, 26, 28, and 46; event offsets 12, 14, 16, 24, and 26; and moving-object offsets 0, 2, 4, 6, 8, 10, 30, and 32 remain unnamed. Hazard and end-trigger members in the reviewed contexts are all named. Field keys are byte offsets in decimal.

Suggested comments for hunches, not names:

- “The filename tag jg is not expanded by the recovered code.”
- “The four copied pointers and difficulty values in ov11_F_21F8 may be shared timing setup; trace consumers before naming them.”
- “The moving-object phase and lookup arrays produce bounded, periodic-looking movement; the formula is visible but its original gameplay label is not.”
- “State 45 is the contact animation state observed here; this does not establish the original programmer's label.”
