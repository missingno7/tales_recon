/* ov11_F_15C8 candidate (worker v9; unread struct spans renamed neutrally). */
struct Descriptor { long object; int word4; int type; int word8; int word10; int dy; int dx; };
struct Controller { int x; int y; char f4[48]; char state; };
struct Object { char f0[52]; char state; };
struct Header { int count; char *data; };
extern int G_h01_12FE;
extern int G_h01_7A94;
extern struct Header *G_h01_7A96;
extern char G_h01_7A9A[1];
extern int G_h01_8A3A; extern int G_h01_8A3C; extern int G_h01_8A3E; extern int G_h01_8A40; extern int G_h01_8A42;
extern long archive_image_bitmap; extern long arc_file; extern long G_h01_9FA6;
extern long G_h01_9F4E; extern long G_h01_9F52; extern long G_h01_9F56;
extern long G_h01_9F5E; extern long G_h01_9F62; extern long G_h01_9F6A; extern long G_h01_9F82; extern long G_h01_9F7E;
extern long G_h01_9F6E; extern long G_h01_9F66; extern long G_h01_9F76; extern long G_h01_9F8A; extern long G_h01_9F9E;
extern long G_h01_9FA2; extern long G_h01_9F92; extern long G_h01_9F96; extern long G_h01_9F9A;
extern long G_h01_9F8E; extern long G_h01_9F5A;
extern struct Descriptor jg_player_move_right_descriptors[10]; extern struct Descriptor jg_player_move_left_descriptors[10]; extern struct Descriptor jg_player_state_4_right_descriptors[8];
extern struct Descriptor jg_player_state_4_left_descriptors[8]; extern struct Descriptor jg_player_state_10_right_descriptors[3]; extern struct Descriptor jg_player_state_10_left_descriptors[3];
extern struct Descriptor jg_player_state_12_descriptors[7]; extern struct Descriptor jg_player_state_13_descriptors[7]; extern struct Descriptor jg_player_state_5_descriptors[5];
extern struct Descriptor jg_player_state_3_right_descriptors[9]; extern struct Descriptor jg_player_state_17_descriptors[2]; extern struct Descriptor jg_player_state_16_descriptors[2];
extern struct Descriptor jg_player_state_18_right_descriptors[5]; extern struct Descriptor jg_player_state_18_left_descriptors[5]; extern struct Descriptor jg_player_state_19_descriptors[3];
extern struct Descriptor jg_player_state_14_descriptors[1]; extern struct Descriptor jg_player_state_6_descriptors[5]; extern struct Descriptor jg_player_state_20_descriptors[7];
extern struct Descriptor jg_player_state_21_descriptors[7]; extern struct Descriptor jg_platform_animation_descriptors[6];
extern long request_disk(); extern long Open(); extern int arc_read_index(); extern long load_arc_record();
extern int report_loader_error(); extern int free_text_block(); extern int free_archive_bitmap();
extern int jg_parse_l_section_records(); extern int jg_parse_grid_and_platform_sections(); extern int jg_parse_p_section(); extern int jg_parse_s_section();
extern int jg_parse_moving_object_sections(); extern int jg_parse_m_section(); extern int jg_parse_x_section(); extern int jg_parse_f_section(); extern int jg_initialize_scrolling_scene();

recovered(arg)
int arg;
{
    int i;

    G_h01_8A3E = 0;
    G_h01_8A40 = 0;
    G_h01_8A42 = 0;
    G_h01_8A3C = 3;
    G_h01_12FE = 0;
    if (arg) {
        G_h01_9FA6 = arc_file;
        request_disk(2);
        arc_file = Open("DT2:jg.arc", 1005L);
        arc_read_index(arc_file);
        if (G_h01_7A94 == 0)
            G_h01_7A96 = (struct Header *)load_arc_record(1, 0L);
        else if (G_h01_7A94 == 1)
            G_h01_7A96 = (struct Header *)load_arc_record(2, 0L);
        else
            G_h01_7A96 = (struct Header *)load_arc_record(3, 0L);
        G_h01_8A3A = G_h01_7A96->count;
        if (G_h01_8A3A > 4000)
            report_loader_error(0x8A4);
        for (i = 0; i < G_h01_8A3A; i++)
            G_h01_7A9A[i] = G_h01_7A96->data[i];
        free_text_block(G_h01_7A96);
        jg_parse_l_section_records(G_h01_7A9A);
        jg_parse_grid_and_platform_sections(G_h01_7A9A);
        jg_parse_p_section(G_h01_7A9A);
        jg_parse_s_section(G_h01_7A9A);
        jg_parse_moving_object_sections(G_h01_7A9A);
        jg_parse_m_section(G_h01_7A9A);
        jg_parse_x_section(G_h01_7A9A);
        jg_parse_f_section(G_h01_7A9A);
        load_arc_record(4, archive_image_bitmap);
        G_h01_9F5A = load_arc_record(7, 0L);
        jg_initialize_scrolling_scene();
        free_archive_bitmap(G_h01_9F5A);
        G_h01_9F8E = load_arc_record(0, 0L);
        G_h01_9F4E = load_arc_record(5, 0L);
        G_h01_9F52 = load_arc_record(6, 0L);
        G_h01_9F56 = load_arc_record(17, 0L);
        G_h01_9F5E = load_arc_record(8, 0L);
        G_h01_9F62 = load_arc_record(9, 0L);
        G_h01_9F6A = load_arc_record(11, 0L);
        G_h01_9F82 = load_arc_record(12, 0L);
        G_h01_9F7E = load_arc_record(13, 0L);
        G_h01_9F6E = load_arc_record(14, 0L);
        G_h01_9F66 = load_arc_record(10, 0L);
        G_h01_9F76 = load_arc_record(15, 0L);
        G_h01_9F8A = load_arc_record(16, 0L);
        G_h01_9F9E = load_arc_record(18, 0L);
        G_h01_9FA2 = load_arc_record(19, 0L);
        ((struct Object *)G_h01_9FA2)->state = 0;
        G_h01_9F92 = load_arc_record(20, 0L);
        G_h01_9F96 = load_arc_record(21, 0L);
        G_h01_9F9A = load_arc_record(22, 0L);
        *(int *)G_h01_9F96 = 8;
        *((int *)G_h01_9F96 + 1) = 0xb2;
        ((struct Object *)G_h01_9F96)->state = 0;
        *(int *)G_h01_9F9A = 0x28;
        *((int *)G_h01_9F9A + 1) = 0xb1;
        ((struct Object *)G_h01_9F9A)->state = 0;
        for (i = 0; i < 5; i++) {
            jg_player_state_5_descriptors[i].object = G_h01_9F4E;
        }
        jg_player_state_5_descriptors[0].word4 = 0x14;
        jg_player_state_5_descriptors[1].word4 = 0x18;
        for (i = 0; i < 10; i++) {
            jg_player_move_right_descriptors[i].object = G_h01_9F4E;
        }
        jg_player_move_right_descriptors[0].object = G_h01_9F4E;
        jg_player_move_right_descriptors[0].word4 = 0;
        jg_player_move_right_descriptors[0].dy = 0x10;
        jg_player_move_right_descriptors[1].word4 = 0x1;
        jg_player_move_right_descriptors[2].word4 = 0x2;
        jg_player_move_right_descriptors[3].word4 = 0x3;
        jg_player_move_right_descriptors[4].word4 = 0x4;
        jg_player_move_right_descriptors[5].word4 = 0x5;
        jg_player_move_right_descriptors[5].dy = 0x10;
        jg_player_move_right_descriptors[6].word4 = 0x6;
        jg_player_move_right_descriptors[7].word4 = 0x7;
        jg_player_move_right_descriptors[8].word4 = 0x8;
        jg_player_move_right_descriptors[9].word4 = 0x9;
        for (i = 0; i < 10; i++) {
            jg_player_move_left_descriptors[i].object = G_h01_9F4E;
        }
        jg_player_move_left_descriptors[0].object = G_h01_9F4E;
        jg_player_move_left_descriptors[0].word4 = 0xa;
        jg_player_move_left_descriptors[0].dy = 0xfff0;
        jg_player_move_left_descriptors[1].word4 = 0xb;
        jg_player_move_left_descriptors[2].word4 = 0xc;
        jg_player_move_left_descriptors[3].word4 = 0xd;
        jg_player_move_left_descriptors[4].word4 = 0xe;
        jg_player_move_left_descriptors[5].word4 = 0xf;
        jg_player_move_left_descriptors[5].dy = 0xfff0;
        jg_player_move_left_descriptors[6].word4 = 0x10;
        jg_player_move_left_descriptors[7].word4 = 0x11;
        jg_player_move_left_descriptors[8].word4 = 0x12;
        jg_player_move_left_descriptors[9].word4 = 0x13;
        for (i = 0; i < 8; i++) {
            jg_player_state_4_right_descriptors[i].object = G_h01_9F4E;
        }
        jg_player_state_4_right_descriptors[0].word4 = 0x15;
        jg_player_state_4_right_descriptors[0].dy = 0xa;
        jg_player_state_4_right_descriptors[0].dx = 0;
        jg_player_state_4_right_descriptors[1].word4 = 0x14;
        jg_player_state_4_right_descriptors[1].dy = 0x2;
        jg_player_state_4_right_descriptors[1].dx = 0xfff4;
        jg_player_state_4_right_descriptors[2].word4 = 0x7;
        jg_player_state_4_right_descriptors[2].dy = 0x2;
        jg_player_state_4_right_descriptors[2].dx = 0xc;
        jg_player_state_4_right_descriptors[2].object = G_h01_9F56;
        jg_player_state_4_right_descriptors[3].word4 = 0x7;
        jg_player_state_4_right_descriptors[3].dy = 0x2;
        jg_player_state_4_right_descriptors[3].dx = 0x8;
        jg_player_state_4_right_descriptors[3].object = G_h01_9F56;
        jg_player_state_4_right_descriptors[4].word4 = 0x7;
        jg_player_state_4_right_descriptors[4].dy = 0x2;
        jg_player_state_4_right_descriptors[4].dx = 0xa;
        jg_player_state_4_right_descriptors[4].object = G_h01_9F56;
        jg_player_state_4_right_descriptors[5].word4 = 0x7;
        jg_player_state_4_right_descriptors[5].dy = 0x2;
        jg_player_state_4_right_descriptors[5].dx = 0xe;
        jg_player_state_4_right_descriptors[5].object = G_h01_9F56;
        jg_player_state_4_right_descriptors[6].word4 = 0x15;
        jg_player_state_4_right_descriptors[6].dy = 0xa;
        jg_player_state_4_right_descriptors[6].dx = 0;
        jg_player_state_4_right_descriptors[7].word4 = 0x14;
        jg_player_state_4_right_descriptors[7].dy = 0xfff6;
        jg_player_state_4_right_descriptors[7].dx = 0;
        for (i = 0; i < 8; i++) {
            jg_player_state_4_left_descriptors[i].object = G_h01_9F4E;
        }
        jg_player_state_4_left_descriptors[0].word4 = 0x19;
        jg_player_state_4_left_descriptors[0].dy = 0xfff6;
        jg_player_state_4_left_descriptors[0].dx = 0;
        jg_player_state_4_left_descriptors[1].word4 = 0x18;
        jg_player_state_4_left_descriptors[1].dy = 0xfffe;
        jg_player_state_4_left_descriptors[1].dx = 0xfff4;
        jg_player_state_4_left_descriptors[2].word4 = 0x3;
        jg_player_state_4_left_descriptors[2].dy = 0xfffe;
        jg_player_state_4_left_descriptors[2].dx = 0xc;
        jg_player_state_4_left_descriptors[2].object = G_h01_9F56;
        jg_player_state_4_left_descriptors[3].word4 = 0x3;
        jg_player_state_4_left_descriptors[3].dy = 0xfffe;
        jg_player_state_4_left_descriptors[3].dx = 0x8;
        jg_player_state_4_left_descriptors[3].object = G_h01_9F56;
        jg_player_state_4_left_descriptors[4].word4 = 0x3;
        jg_player_state_4_left_descriptors[4].dy = 0xfffe;
        jg_player_state_4_left_descriptors[4].dx = 0xa;
        jg_player_state_4_left_descriptors[4].object = G_h01_9F56;
        jg_player_state_4_left_descriptors[5].word4 = 0x3;
        jg_player_state_4_left_descriptors[5].dy = 0xfffe;
        jg_player_state_4_left_descriptors[5].dx = 0xe;
        jg_player_state_4_left_descriptors[5].object = G_h01_9F56;
        jg_player_state_4_left_descriptors[6].word4 = 0x19;
        jg_player_state_4_left_descriptors[6].dy = 0xfff6;
        jg_player_state_4_left_descriptors[6].dx = 0;
        jg_player_state_4_left_descriptors[7].word4 = 0x18;
        jg_player_state_4_left_descriptors[7].dy = 0xa;
        jg_player_state_4_left_descriptors[7].dx = 0;
        for (i = 0; i < 3; i++) {
            jg_player_state_10_right_descriptors[i].object = G_h01_9F4E;
            jg_player_state_10_left_descriptors[i].object = G_h01_9F4E;
        }
        jg_player_state_10_right_descriptors[0].word4 = 0x15;
        jg_player_state_10_right_descriptors[0].dy = 0x10;
        jg_player_state_10_right_descriptors[1].word4 = 0x16;
        jg_player_state_10_right_descriptors[1].dy = 0;
        jg_player_state_10_right_descriptors[1].type = 0x7;
        jg_player_state_10_right_descriptors[2].word4 = 0x14;
        jg_player_state_10_right_descriptors[2].dy = 0xfff0;
        jg_player_state_10_left_descriptors[0].word4 = 0x19;
        jg_player_state_10_left_descriptors[0].dy = 0xfff0;
        jg_player_state_10_left_descriptors[1].word4 = 0x1a;
        jg_player_state_10_left_descriptors[1].dy = 0;
        jg_player_state_10_left_descriptors[1].type = 0x7;
        jg_player_state_10_left_descriptors[2].word4 = 0x18;
        jg_player_state_10_left_descriptors[2].dy = 0x10;
        for (i = 0; i < 7; i++) {
            jg_player_state_12_descriptors[i].object = G_h01_9F52;
        }
        jg_player_state_12_descriptors[0].word4 = 0x4;
        jg_player_state_12_descriptors[0].dx = 0xfff8;
        jg_player_state_12_descriptors[1].word4 = 0x5;
        jg_player_state_12_descriptors[1].dx = 0xfff4;
        jg_player_state_12_descriptors[2].word4 = 0x6;
        jg_player_state_12_descriptors[2].dx = 0xfff8;
        jg_player_state_12_descriptors[3].word4 = 0x7;
        jg_player_state_12_descriptors[3].dx = 0xfffa;
        jg_player_state_12_descriptors[4].word4 = 0x8;
        jg_player_state_12_descriptors[4].dx = 0;
        jg_player_state_12_descriptors[5].word4 = 0x7;
        jg_player_state_12_descriptors[5].dx = 0;
        jg_player_state_12_descriptors[6].word4 = 0x4;
        jg_player_state_12_descriptors[6].dx = 0xffeb;
        for (i = 0; i < 7; i++) {
            jg_player_state_13_descriptors[i].object = G_h01_9F52;
        }
        jg_player_state_13_descriptors[0].word4 = 0x4;
        jg_player_state_13_descriptors[0].dx = 0x3;
        jg_player_state_13_descriptors[1].word4 = 0x7;
        jg_player_state_13_descriptors[1].dx = 0xe;
        jg_player_state_13_descriptors[2].word4 = 0x8;
        jg_player_state_13_descriptors[2].dx = 0;
        jg_player_state_13_descriptors[3].word4 = 0x7;
        jg_player_state_13_descriptors[3].dx = 0;
        jg_player_state_13_descriptors[4].word4 = 0x6;
        jg_player_state_13_descriptors[4].dx = 0x6;
        jg_player_state_13_descriptors[5].word4 = 0x5;
        jg_player_state_13_descriptors[5].dx = 0xa;
        jg_player_state_13_descriptors[6].word4 = 0x4;
        jg_player_state_13_descriptors[6].dx = 0x6;
        for (i = 0; i < 7; i++) {
            jg_player_state_20_descriptors[i].object = G_h01_9F52;
        }
        jg_player_state_20_descriptors[0].word4 = 0x4;
        jg_player_state_20_descriptors[0].dx = 0xfff9;
        jg_player_state_20_descriptors[1].word4 = 0x5;
        jg_player_state_20_descriptors[1].dx = 0x3;
        jg_player_state_20_descriptors[2].word4 = 0x6;
        jg_player_state_20_descriptors[2].dx = 0xfff9;
        jg_player_state_20_descriptors[3].word4 = 0x7;
        jg_player_state_20_descriptors[3].dx = 0xfffa;
        jg_player_state_20_descriptors[4].word4 = 0x8;
        jg_player_state_20_descriptors[4].dx = 0;
        jg_player_state_20_descriptors[5].word4 = 0x7;
        jg_player_state_20_descriptors[5].dx = 0;
        jg_player_state_20_descriptors[6].word4 = 0x4;
        jg_player_state_20_descriptors[6].dx = 0xffea;
        for (i = 0; i < 7; i++) {
            jg_player_state_21_descriptors[i].object = G_h01_9F52;
        }
        jg_player_state_21_descriptors[0].word4 = 0x4;
        jg_player_state_21_descriptors[0].dx = 0xfff9;
        jg_player_state_21_descriptors[1].word4 = 0x7;
        jg_player_state_21_descriptors[1].dx = 0x17;
        jg_player_state_21_descriptors[2].word4 = 0x8;
        jg_player_state_21_descriptors[2].dx = 0;
        jg_player_state_21_descriptors[3].word4 = 0x7;
        jg_player_state_21_descriptors[3].dx = 0;
        jg_player_state_21_descriptors[4].word4 = 0x6;
        jg_player_state_21_descriptors[4].dx = 0x6;
        jg_player_state_21_descriptors[5].word4 = 0x5;
        jg_player_state_21_descriptors[5].dx = 0x8;
        jg_player_state_21_descriptors[6].word4 = 0x4;
        jg_player_state_21_descriptors[6].dx = 0xfffc;
        for (i = 0; i < 9; i++) {
            jg_player_state_3_right_descriptors[i].object = G_h01_9F56;
        }
        jg_player_state_3_right_descriptors[0].word4 = 0x4;
        jg_player_state_3_right_descriptors[1].word4 = 0x5;
        jg_player_state_3_right_descriptors[2].word4 = 0;
        jg_player_state_3_right_descriptors[2].object = G_h01_9F52;
        jg_player_state_3_right_descriptors[2].dy = 0x5;
        jg_player_state_3_right_descriptors[2].dx = 0xfff2;
        jg_player_state_3_right_descriptors[3].word4 = 0;
        jg_player_state_3_right_descriptors[3].object = G_h01_9F52;
        jg_player_state_3_right_descriptors[3].dy = 0x5;
        jg_player_state_3_right_descriptors[3].dx = 0xfff4;
        jg_player_state_3_right_descriptors[4].word4 = 0;
        jg_player_state_3_right_descriptors[4].object = G_h01_9F52;
        jg_player_state_3_right_descriptors[4].dy = 0x5;
        jg_player_state_3_right_descriptors[4].dx = 0xfff6;
        jg_player_state_3_right_descriptors[5].word4 = 0x7;
        jg_player_state_3_right_descriptors[5].dy = 0x5;
        jg_player_state_3_right_descriptors[5].dx = 0xfff8;
        jg_player_state_3_right_descriptors[6].word4 = 0x7;
        jg_player_state_3_right_descriptors[6].dy = 0x5;
        jg_player_state_3_right_descriptors[6].dx = 0x2;
        jg_player_state_3_right_descriptors[7].word4 = 0x6;
        jg_player_state_3_right_descriptors[7].dy = 0xd;
        jg_player_state_3_right_descriptors[7].dx = 0x3;
        jg_player_state_3_right_descriptors[8].word4 = 0x14;
        jg_player_state_3_right_descriptors[8].object = G_h01_9F4E;
        jg_player_state_3_right_descriptors[8].dy = 0xfff6;
        jg_player_state_3_right_descriptors[8].dx = 0x4;
        jg_player_state_14_descriptors[0].object = G_h01_9F52;
        jg_player_state_14_descriptors[0].word4 = 0x9;
        jg_player_state_14_descriptors[0].type = 0x5;
        jg_player_state_17_descriptors[0].object = G_h01_9F56;
        jg_player_state_17_descriptors[0].word4 = 0x5;
        jg_player_state_17_descriptors[1].object = G_h01_9F52;
        jg_player_state_17_descriptors[1].word4 = 0;
        jg_player_state_17_descriptors[1].dy = 0x4;
        jg_player_state_17_descriptors[1].dx = 0xfff9;
        jg_player_state_16_descriptors[0].object = G_h01_9F56;
        jg_player_state_16_descriptors[0].word4 = 0x1;
        jg_player_state_16_descriptors[1].object = G_h01_9F52;
        jg_player_state_16_descriptors[1].word4 = 0x2;
        jg_player_state_16_descriptors[1].dy = 0xfffc;
        jg_player_state_16_descriptors[1].dx = 0xfff9;
        for (i = 0; i < 5; i++) {
            jg_player_state_18_left_descriptors[i].object = G_h01_9F4E;
        }
        jg_player_state_18_left_descriptors[0].word4 = 0x15;
        jg_player_state_18_left_descriptors[0].dy = 0xe;
        jg_player_state_18_left_descriptors[1].word4 = 0x4;
        jg_player_state_18_left_descriptors[1].dy = 0xfff8;
        jg_player_state_18_left_descriptors[1].object = G_h01_9F56;
        jg_player_state_18_left_descriptors[2].word4 = 0x7;
        jg_player_state_18_left_descriptors[2].type = 0x8;
        jg_player_state_18_left_descriptors[2].dx = 0xffe8;
        jg_player_state_18_left_descriptors[2].dy = 0xfff8;
        jg_player_state_18_left_descriptors[2].object = G_h01_9F56;
        jg_player_state_18_left_descriptors[3].word4 = 0x4;
        jg_player_state_18_left_descriptors[3].dy = 0x8;
        jg_player_state_18_left_descriptors[3].dx = 0x18;
        jg_player_state_18_left_descriptors[3].object = G_h01_9F56;
        jg_player_state_18_left_descriptors[4].word4 = 0x15;
        jg_player_state_18_left_descriptors[4].dy = 0x8;
        for (i = 0; i < 5; i++) {
            jg_player_state_18_right_descriptors[i].object = G_h01_9F4E;
        }
        jg_player_state_18_right_descriptors[0].word4 = 0x19;
        jg_player_state_18_right_descriptors[0].dy = 0xfff2;
        jg_player_state_18_right_descriptors[1].word4 = 0;
        jg_player_state_18_right_descriptors[1].dy = 0x8;
        jg_player_state_18_right_descriptors[1].object = G_h01_9F56;
        jg_player_state_18_right_descriptors[2].word4 = 0x3;
        jg_player_state_18_right_descriptors[2].type = 0x8;
        jg_player_state_18_right_descriptors[2].dx = 0xffe8;
        jg_player_state_18_right_descriptors[2].dy = 0x6;
        jg_player_state_18_right_descriptors[2].object = G_h01_9F56;
        jg_player_state_18_right_descriptors[3].word4 = 0;
        jg_player_state_18_right_descriptors[3].dy = 0xfffa;
        jg_player_state_18_right_descriptors[3].dx = 0x18;
        jg_player_state_18_right_descriptors[3].object = G_h01_9F56;
        jg_player_state_18_right_descriptors[4].word4 = 0x19;
        jg_player_state_18_right_descriptors[4].dy = 0xfff8;
        for (i = 0; i < 3; i++) {
            jg_player_state_19_descriptors[i].object = G_h01_9F52;
        }
        jg_player_state_19_descriptors[0].word4 = 0x4;
        jg_player_state_19_descriptors[0].dx = 0xfff8;
        jg_player_state_19_descriptors[1].word4 = 0x5;
        jg_player_state_19_descriptors[2].word4 = 0x4;
        for (i = 0; i < 5; i++) {
            jg_player_state_6_descriptors[i].object = G_h01_9F8E;
            jg_player_state_6_descriptors[i].type = 3;
        }
        jg_player_state_6_descriptors[0].word4 = 0;
        jg_player_state_6_descriptors[0].dy = 0xffe9;
        jg_player_state_6_descriptors[1].word4 = 0x1;
        jg_player_state_6_descriptors[2].word4 = 0x2;
        jg_player_state_6_descriptors[3].word4 = 0x3;
        jg_player_state_6_descriptors[4].word4 = 0x4;
        for (i = 0; i < 6; i++) {
            jg_platform_animation_descriptors[i].object = G_h01_9F62;
            jg_platform_animation_descriptors[i].dx = -6;
        }
        jg_platform_animation_descriptors[0].word4 = 0;
        jg_platform_animation_descriptors[0].word8 = 0;
        jg_platform_animation_descriptors[0].type = 0x1;
        jg_platform_animation_descriptors[1].word4 = 0x1;
        jg_platform_animation_descriptors[1].word8 = 0xa;
        jg_platform_animation_descriptors[1].type = 0x1;
        jg_platform_animation_descriptors[2].word4 = 0x2;
        jg_platform_animation_descriptors[2].type = 0x4;
        jg_platform_animation_descriptors[2].word8 = 0x17;
        jg_platform_animation_descriptors[3].word4 = 0x1;
        jg_platform_animation_descriptors[3].type = 0x1;
        jg_platform_animation_descriptors[3].word8 = 0xa;
        jg_platform_animation_descriptors[4].word4 = 0;
        jg_platform_animation_descriptors[4].word8 = 0;
        jg_platform_animation_descriptors[4].type = 0x1;
        jg_platform_animation_descriptors[5].word4 = 0x3;
        jg_platform_animation_descriptors[5].type = 0x3;
        jg_platform_animation_descriptors[5].word8 = 0xfffc;
    }
}
