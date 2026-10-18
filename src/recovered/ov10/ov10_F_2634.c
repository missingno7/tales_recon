extern long screen_rast_port;
extern long G_h01_46CE;
extern long G_h01_46D2;
extern int F_h00_30F0();
extern int F_h00_34E0();
extern unsigned int F_h00_463E();
extern int BltBitMap();
extern int BltBitMapRastPort();
extern int F_h10_22E6();
extern short G_h01_060A[1];
extern short G_h01_0626[1];
extern short G_h01_0636[1];
extern short G_h01_0646[1];
extern short G_h01_0656[1];
extern char G_h01_4356[1];
extern char *G_h01_5392;
extern short G_h01_726C;
extern short G_h01_726E;
extern short G_h01_72A2;
extern short G_h01_72A4;
extern char G_h01_72D6;
extern short G_h01_72D8;
extern short G_h01_72DA;
extern char G_h01_730C;
extern char G_h01_741C[1];
extern char G_h01_7452[1];
extern char G_h01_74F4[1];
extern long G_h01_7998;
extern char G_h01_79A2;
extern char G_h01_79A3;
extern char G_h01_79A4;
extern char G_h01_79A6;
extern char G_h01_72A0;
extern short G_h01_79AE;
extern short G_h01_79B0;
extern short G_h01_79B2;

void recovered(obj, kind, frame)
short *obj;
int kind, frame;
{
    short *shape;
    int frame_index, x, y, width, height;

    if (kind == 17) {
        obj[0] = 0x52;
        obj[1] = 0x26;
        if (G_h01_79A6 == 2) {
            obj[0] = 0x53;
            obj[1] = 0x2f;
        }
        if (frame == 6) {
            obj[0] = 0x55;
            obj[1] = 0x30;
        }
        shape = G_h01_060A;
        x = obj[0] - 0x1e;
        y = obj[1] - 0x1e;
        width = 0xb4;
        height = 0xa0;
    } else if (kind == 10) {
        shape = G_h01_0626;
        x = obj[0] - 0x20;
        y = obj[1] - 0x26;
        width = 0xb4;
        height = 0x9e;
    } else if (kind == 11) {
        shape = G_h01_0636;
        x = obj[0];
        y = obj[1] - 0x26;
        width = 0xb4;
        height = 0xb4;
    } else if (kind == 13) {
        shape = G_h01_0656;
        x = obj[0];
        y = obj[1] - 0x28;
        width = 0xb4;
        height = 0xaa;
    } else {
        shape = G_h01_0646;
        x = obj[0] - 0x28;
        y = obj[1] - 0x12;
        width = 0xbe;
        height = 0x9e;
    }

    if (x < 0)
        x = 0;
    else if (x > 0x140)
        x = 0x140;
    if (y < 0)
        y = 0;
    else if (y > 0xc8)
        y = 0xc8;

    BltBitMap(G_h01_46CE, 0L, 0L, G_h01_46D2, 0L, 0L,
               0x140L, 0xc8L, 0xc0L, 0xffL, 0L);

    frame_index = frame;
    BltBitMapRastPort(G_h01_7998, 0L, 0L, screen_rast_port,
               (long)(shape[frame_index * 2] + obj[0] - 0x48),
               (long)(shape[frame_index * 2 + 1] + obj[1] - 0x40),
               0x90L, 0x87L, 0xeeL);

    if (G_h01_79B2 == 0) {
        switch (G_h01_79A2) {
        case 0:
            ((short *)(G_h01_5392 + 0x36))[0] = 0x832;
            ((short *)(G_h01_5392 + 0x3c))[0] = 0xb20;
            break;
        case 1:
            ((short *)(G_h01_5392 + 0x36))[0] = 0x842;
            ((short *)(G_h01_5392 + 0x3c))[0] = 0xb30;
            break;
        case 2:
            ((short *)(G_h01_5392 + 0x36))[0] = 0x943;
            ((short *)(G_h01_5392 + 0x3c))[0] = 0xa30;
            break;
        case 3:
            ((short *)(G_h01_5392 + 0x36))[0] = 0x843;
            ((short *)(G_h01_5392 + 0x3c))[0] = 0xa20;
            break;
        }
        F_h00_30F0();
    }

    if ((kind == 17 && frame_index != 5 && frame_index != 6) || kind == 11)
        F_h00_34E0(obj);

    if (G_h01_79A4 < (G_h01_79AE >> 1)) {
        G_h01_72A0 = G_h01_79A2;
        G_h01_726C = shape[frame_index * 2] + obj[0] - 0x0f;
        G_h01_726E = shape[frame_index * 2 + 1] + obj[1] - 0x40;
        if (G_h01_79A6 == 2) {
            G_h01_726C = shape[frame_index * 2] + 0x43;
            G_h01_726E = shape[frame_index * 2 + 1] - 0x1a;
        }
        F_h00_34E0(&G_h01_726C);
    } else if (G_h01_79A4 < G_h01_79AE - G_h01_79B0) {
        G_h01_72D6 = G_h01_79A2;
        G_h01_72A2 = shape[frame_index * 2] + obj[0] - 0x0b;
        G_h01_72A4 = shape[frame_index * 2 + 1] + obj[1] - 0x33;
        if (G_h01_79A6 == 2) {
            G_h01_72A2 = shape[frame_index * 2] + 0x47;
            G_h01_72A4 = shape[frame_index * 2 + 1] - 0x0d;
        }
        F_h00_34E0(&G_h01_72A2);
    } else {
        G_h01_730C = G_h01_79A2;
        G_h01_72D8 = shape[frame_index * 2] + obj[0] - 6;
        G_h01_72DA = shape[frame_index * 2 + 1] + obj[1] - 0x2a;
        if (G_h01_79A6 == 2) {
            G_h01_72D8 = shape[frame_index * 2] + 0x4c;
            G_h01_72DA = shape[frame_index * 2 + 1] - 4;
        }
        F_h00_34E0(&G_h01_72D8);
    }

    if (kind != 11 && (kind != 17 || (kind == 17 && (frame_index == 5 || frame_index == 6))))
        F_h00_34E0(obj);
    F_h00_34E0(G_h01_74F4);
    F_h00_34E0(G_h01_7452);
    F_h00_34E0(G_h01_741C);

    if (kind == 17 && G_h01_79A6 == 0)
        F_h10_22E6(G_h01_4356);

    G_h01_79A2 = F_h00_463E() & 3;
    if (G_h01_79A3 == G_h01_79A2) {
        G_h01_79A2++;
        if (G_h01_79A2 > 3)
            G_h01_79A2 = 0;
    }
    G_h01_79A3 = G_h01_79A2;
}