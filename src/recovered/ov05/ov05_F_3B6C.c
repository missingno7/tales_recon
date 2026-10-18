/* Worker haiku-fn-ov05_F_3B6C: structured candidate for ov05_F_3B6C (v1). */
struct Lookup { int index; int f2; };
struct Record { char b0[4]; int value; char rest[8]; };
struct Pos { int x; int y; };

extern int G_h01_5E42;
extern int G_h01_5E64[1][2];
extern struct Lookup G_h01_5E66[16];
extern struct Record G_h01_606C[16];
extern char G_h01_5E5F;
extern char G_h01_5E60;
extern char G_h01_5E61;
extern char G_h01_5E62;
extern char G_h01_5E58;
extern long G_h01_5484[17];
extern struct Pos *G_h01_55A0;
extern struct Pos *G_h01_5898;
extern char G_h01_54C8;
extern char G_h01_54FE;
extern char G_h01_5534;
extern char G_h01_556A;
extern char G_h01_55A4;
extern char G_h01_55DA;
extern char G_h01_5610;
extern char G_h01_5646;
extern char G_h01_567C;
extern char G_h01_56B2;
extern char G_h01_56E8;
extern char G_h01_571E;
extern char G_h01_5754;
extern char G_h01_578A;
extern char G_h01_57C0;
extern char G_h01_57F6;
extern char G_h01_582C;
extern char G_h01_5862;
extern char G_h01_589C;
extern char G_h01_58D2;
extern char G_h01_5908;
extern char G_h01_59E0;
extern char G_h01_5A16;
extern char G_h01_5A4C;
extern char G_h01_5A82;
extern char G_h01_5AB8;
extern char G_h01_5AEE;
extern char G_h01_5B24;
extern char G_h01_5B5A;
extern char G_h01_5B90;
extern char G_h01_5BC6;
extern char G_h01_5BFC;
extern char G_h01_5C32;
extern char G_h01_5C68;
extern char G_h01_5C9E;
extern char G_h01_5D40;
extern unsigned int F_h00_463E();
extern int request_disk();
extern long load_arc_record();
extern int plane_generate_course_segment_types();
extern int plane_populate_course_objects();

recovered()
{
    unsigned int s2;
    int j;
    int cursor;
    int delta;
    unsigned int kind;
    unsigned int r;

    kind = 0;
    G_h01_5E5F = 0;
    G_h01_5E61 = 0;
    G_h01_5E60 = 0;
    G_h01_5E62 = 0;
    for (j = 0; j < 130; j++) {
        G_h01_5E66[j].index = -1;
        G_h01_5E64[j][0] = 0;
    }
    for (j = 0; j < 260; j++) {
        G_h01_606C[j].b0[0] = -1;
        G_h01_606C[j].rest[6] = -1;
    }
    cursor = 0;
    delta = G_h01_5E42 / 4;
    kind = F_h00_463E() % 100;
    if (kind < 8)
        kind = 7;
    else if (kind < 14)
        kind = 3;
    else if (kind < 18)
        kind = 1;
    else
        kind = 20;
    plane_generate_course_segment_types(delta, kind, &cursor);

    s2 = F_h00_463E() % 100;
    if (s2 < 33) {
        s2 = F_h00_463E() & 1;
        if (s2 == 1) {
            plane_generate_course_segment_types(delta, 21, &cursor);
            plane_generate_course_segment_types(delta, kind, &cursor);
        } else {
            plane_generate_course_segment_types(delta, kind, &cursor);
            plane_generate_course_segment_types(delta, 21, &cursor);
        }
        if (kind != 20) {
            kind = F_h00_463E() % 100;
            if (kind < 10)
                kind = 7;
            else if (kind < 20)
                kind = 3;
            else if (kind < 30)
                kind = 1;
            else
                kind = 20;
        }
        plane_generate_course_segment_types(delta, kind, &cursor);
    } else if (s2 < 66) {
        for (j = 0; j < 2; j++)
            plane_generate_course_segment_types(delta, 21, &cursor);
        plane_generate_course_segment_types(delta, kind, &cursor);
    } else {
        for (j = 0; j < 3; j++) {
            if (kind != 20 && j == 1) {
                r = F_h00_463E() % 100;
                if (r < 10)
                    r = 7;
                else if (kind < 20)
                    r = 3;
                else if (kind < 30)
                    r = 1;
                else
                    r = 20;
                plane_generate_course_segment_types(delta, r, &cursor);
            } else {
                plane_generate_course_segment_types(delta, kind, &cursor);
            }
        }
    }

    G_h01_5E64[0][0] = 15;
    G_h01_5E66[0].f2 = 16;
    G_h01_5E64[G_h01_5E42 - 1][0] = 15;
    G_h01_5E64[G_h01_5E42][0] = 16;

    for (j = 0; j < 17; j++)
        G_h01_5484[j] = 0;
    request_disk(1);
    G_h01_5484[0] = load_arc_record(0, G_h01_5484[0]);
    G_h01_5484[1] = load_arc_record(1, G_h01_5484[1]);
    G_h01_5484[2] = load_arc_record(2, G_h01_5484[2]);
    G_h01_5484[3] = load_arc_record(3, G_h01_5484[3]);
    G_h01_5484[4] = load_arc_record(4, G_h01_5484[4]);
    G_h01_5484[5] = load_arc_record(5, G_h01_5484[5]);
    G_h01_5484[6] = load_arc_record(6, G_h01_5484[6]);
    G_h01_5484[7] = load_arc_record(7, G_h01_5484[7]);
    G_h01_5484[8] = load_arc_record(8, G_h01_5484[8]);
    G_h01_5484[9] = load_arc_record(9, G_h01_5484[9]);
    G_h01_5484[10] = load_arc_record(10, G_h01_5484[10]);
    G_h01_5484[11] = load_arc_record(11, G_h01_5484[11]);
    G_h01_5484[12] = load_arc_record(12, G_h01_5484[12]);
    G_h01_5484[13] = load_arc_record(13, G_h01_5484[13]);
    G_h01_5484[14] = load_arc_record(14, G_h01_5484[14]);
    G_h01_5484[15] = load_arc_record(15, G_h01_5484[15]);
    G_h01_5484[16] = load_arc_record(16, G_h01_5484[16]);

    load_arc_record(0x11, &G_h01_55A4);
    load_arc_record(0x12, &G_h01_55DA);
    load_arc_record(0x13, &G_h01_5610);
    load_arc_record(0x14, &G_h01_567C);
    load_arc_record(0x15, &G_h01_56B2);
    load_arc_record(0x16, &G_h01_56E8);
    load_arc_record(0x17, &G_h01_571E);
    load_arc_record(0x18, &G_h01_5754);
    load_arc_record(0x19, &G_h01_578A);
    load_arc_record(0x1a, &G_h01_54C8);
    load_arc_record(0x1b, &G_h01_54FE);
    load_arc_record(0x20, &G_h01_5646);
    load_arc_record(0x21, &G_h01_5534);
    load_arc_record(0x22, &G_h01_556A);

    G_h01_55A0 = 0;
    if ((s2 = F_h00_463E() % 6) == 0) {
        G_h01_55A0 = (struct Pos *)load_arc_record(0x23, G_h01_55A0);
        G_h01_5E61 = 1;
    } else if (s2 == 1) {
        G_h01_55A0 = (struct Pos *)load_arc_record(0x24, G_h01_55A0);
        G_h01_5E61 = 2;
    } else if (s2 == 2) {
        G_h01_55A0 = (struct Pos *)load_arc_record(0x25, G_h01_55A0);
        G_h01_5E61 = 3;
    } else if (s2 == 3) {
        G_h01_55A0 = (struct Pos *)load_arc_record(0x26, G_h01_55A0);
        G_h01_5E61 = 4;
    } else if (s2 == 4) {
        G_h01_55A0 = (struct Pos *)load_arc_record(0x27, G_h01_55A0);
        G_h01_5E61 = 5;
    } else {
        G_h01_5898 = 0;
        G_h01_5898 = (struct Pos *)load_arc_record(0x1c, G_h01_5898);
        G_h01_5E60 = 1;
    }

    if (G_h01_5E58 != 0) {
        load_arc_record(0x3b, &G_h01_5C68);
        load_arc_record(0x3c, &G_h01_5C9E);
    } else if (F_h00_463E() % 100 < 90) {
        if (G_h01_5E61 != 3 && G_h01_5E61 != 5 && G_h01_5E60 == 0)
            load_arc_record(0x28, &G_h01_57C0);
        else
            load_arc_record(0x29, &G_h01_57C0);
        load_arc_record(0x29, &G_h01_57F6);
        load_arc_record(0x2a, &G_h01_582C);
        load_arc_record(0x2b, &G_h01_5862);
        G_h01_5E5F = 1;
    } else if (G_h01_5E61 != 3 && G_h01_5E61 != 5 && G_h01_5E60 == 0) {
        load_arc_record(0x1d, &G_h01_589C);
        load_arc_record(0x1e, &G_h01_58D2);
        load_arc_record(0x1f, &G_h01_5908);
        G_h01_5E62 = 1;
    }

    load_arc_record(0x2c, &G_h01_59E0);
    load_arc_record(0x2d, &G_h01_5A16);
    load_arc_record(0x2e, &G_h01_5A4C);
    load_arc_record(0x2f, &G_h01_5A82);
    load_arc_record(0x30, &G_h01_5AB8);
    load_arc_record(0x31, &G_h01_5AEE);
    load_arc_record(0x34, &G_h01_5B24);
    load_arc_record(0x35, &G_h01_5B5A);
    load_arc_record(0x36, &G_h01_5B90);
    load_arc_record(0x37, &G_h01_5BC6);
    load_arc_record(0x38, &G_h01_5BFC);
    load_arc_record(0x39, &G_h01_5C32);
    load_arc_record(0x3a, &G_h01_5D40);
    plane_populate_course_objects(G_h01_5E42);
}
