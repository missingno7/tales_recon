/* Isolated source-shape probe for ov11_F_4B0C; no source ownership claimed. */
struct Descriptor { long object; char pad4; char state; int type; char pad8[4]; int dy; int dx; };
struct Object { char pad[52]; char state; };
extern int G_h01_94B0; extern int G_h01_94B0; extern int G_h01_94B2; extern int G_h01_94B4; extern int G_h01_94B6;
extern int G_h01_94BE; extern int G_h01_94C0; extern int G_h01_94C0; extern int G_h01_94D8;
extern struct Object *G_h01_94DA; extern int G_h01_94DE; extern int G_h01_94E0; extern int G_h01_94E0;
extern int G_h01_94E4; extern int G_h01_94E6; extern struct Descriptor *G_h01_94E8;
extern struct Object *G_h01_9F4E; extern struct Object *G_h01_9F52;
extern struct Descriptor jg_player_move_right_descriptors[1]; extern struct Descriptor jg_player_move_left_descriptors[1];
extern struct Descriptor jg_player_state_4_right_descriptors[1]; extern struct Descriptor jg_player_state_4_left_descriptors[1];
extern struct Descriptor jg_player_state_10_right_descriptors[1]; extern struct Descriptor jg_player_state_12_descriptors[1];
extern struct Descriptor jg_player_state_10_left_descriptors[1]; extern struct Descriptor jg_player_state_13_descriptors[1];
extern struct Descriptor jg_player_state_5_descriptors[1]; extern struct Descriptor jg_player_state_5_left_animation_start[1];
extern struct Descriptor jg_player_state_3_right_descriptors[1]; extern struct Descriptor jg_player_state_3_left_descriptors[1];
extern struct Descriptor jg_player_state_17_descriptors[1]; extern struct Descriptor jg_player_state_16_descriptors[1];
extern struct Descriptor jg_player_state_18_right_descriptors[1]; extern struct Descriptor jg_player_state_18_left_descriptors[1];
extern struct Descriptor jg_player_state_19_descriptors[1]; extern struct Descriptor jg_player_state_14_descriptors[1];
extern struct Descriptor jg_player_state_6_descriptors[1]; extern struct Descriptor jg_player_state_20_descriptors[1];
extern struct Descriptor jg_player_state_21_descriptors[1]; extern struct Object *G_h01_9F52; extern struct Object *G_h01_9F4E;
extern int play_sound(); extern int jg_get_moving_object_positions();

recovered(mode)
int mode;
{
    int x;
    int y;
    G_h01_94DE = 0;
    G_h01_94E4 = 0;
    G_h01_94E6 = 1;
    G_h01_94E8 = 0;
    switch (mode) {
    case 20: G_h01_94E0 = 7; G_h01_94E8 = jg_player_state_20_descriptors; break;
    case 21: G_h01_94E0 = 7; G_h01_94E8 = jg_player_state_21_descriptors; break;
    case 6: play_sound(0x58); G_h01_94C0 = 0x8e; G_h01_94E0 = 5; G_h01_94E8 = jg_player_state_6_descriptors; break;
    case 19: G_h01_94E0 = 3; G_h01_94E8 = jg_player_state_19_descriptors; break;
    case 18: G_h01_94E0 = 5; G_h01_94E8 = (G_h01_94B0 == 0) ? jg_player_state_18_right_descriptors : jg_player_state_18_left_descriptors; play_sound(0x64); break;
    case 17: G_h01_94E0 = 2; G_h01_94E8 = jg_player_state_17_descriptors; break;
    case 16: G_h01_94E0 = 2; G_h01_94E8 = jg_player_state_16_descriptors; break;
    case 14: G_h01_94E0 = 1; G_h01_94E8 = jg_player_state_14_descriptors; break;
    case 45: G_h01_94E0 = 0; break;    case 12: G_h01_94E0 = 7; G_h01_94E8 = jg_player_state_12_descriptors; break;
    case 13: G_h01_94E0 = 7; G_h01_94E8 = jg_player_state_13_descriptors; break;
    case 3: G_h01_94E0 = 9; G_h01_94E8 = (G_h01_94B0 == 1) ? jg_player_state_3_right_descriptors : jg_player_state_3_left_descriptors; break;
    case 10: G_h01_94E0 = 3; G_h01_94E8 = (G_h01_94B0 == 1) ? jg_player_state_10_right_descriptors : jg_player_state_10_left_descriptors; break;
    case 4: G_h01_94E0 = 8; G_h01_94E8 = (G_h01_94B0 == 1) ? jg_player_state_4_right_descriptors : jg_player_state_4_left_descriptors; break;
    case 5: G_h01_94E0 = 0; G_h01_94E8 = (G_h01_94B0 == 1) ? jg_player_state_5_descriptors : jg_player_state_5_left_animation_start; break;
    case 1:
        if (G_h01_94B2 != 0) { G_h01_94DE = 0; G_h01_94E0 = 5; }
        else { G_h01_94DE = 5; G_h01_94E0 = 10; }
        if (G_h01_94B0 == 1) G_h01_94E8 = &jg_player_move_right_descriptors[G_h01_94DE];
        else G_h01_94E8 = &jg_player_move_left_descriptors[G_h01_94DE];
        break;
    case 2:
        G_h01_94B6 = 0; G_h01_94B4 = 0; G_h01_94E0 = 0; G_h01_94DA = G_h01_9F52;
        if (G_h01_94B0 == 1) G_h01_94DA->state = 1; else G_h01_94DA->state = 3;
        play_sound(0xf); break;
    case 8:
        G_h01_94E0 = 1; G_h01_94DA = G_h01_9F4E;
        jg_get_moving_object_positions(G_h01_94D8, &x, &y, &G_h01_94BE, &G_h01_94C0);
        if (G_h01_94BE < x) {
            G_h01_94DA->state = (G_h01_94B0 == 1) ? 0x1c : 0x1e;
            if (G_h01_94B0 == 0) { G_h01_94BE -= 12; G_h01_94C0 += 8; }
            else { G_h01_94BE -= 3; G_h01_94C0 += 9; }
        } else if (G_h01_94BE > x) {
            G_h01_94DA->state = (G_h01_94B0 == 1) ? 0x1d : 0x1f;
            if (G_h01_94B0 == 0) { G_h01_94BE += 0; G_h01_94C0 += 10; }
            else { G_h01_94BE += 10; G_h01_94C0 += 17; }
        } else {
            G_h01_94DA->state = (G_h01_94B0 == 1) ? 0x17 : 0x1b;
            if (G_h01_94B0 == 0) { G_h01_94BE -= 6; G_h01_94C0 += 22; }
            else { G_h01_94BE += 1; G_h01_94C0 += 22; }
        }
        G_h01_94BE -= 6; G_h01_94C0 -= 21; break;

    }
    if (G_h01_94E8 != 0) {
        G_h01_94DA = G_h01_94E8->object;
        G_h01_94BE += G_h01_94E8->dy;
        G_h01_94C0 += G_h01_94E8->dx;
        G_h01_94DA->state = G_h01_94E8->state;
        G_h01_94E4 = G_h01_94E8->type;
    }
}
