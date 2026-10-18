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
extern long G_h01_46CE; extern long arc_file; extern long G_h01_9FA6;
extern long G_h01_9F4E; extern long G_h01_9F52; extern long G_h01_9F56;
extern long G_h01_9F5E; extern long G_h01_9F62; extern long G_h01_9F6A; extern long G_h01_9F82; extern long G_h01_9F7E;
extern long G_h01_9F6E; extern long G_h01_9F66; extern long G_h01_9F76; extern long G_h01_9F8A; extern long G_h01_9F9E;
extern long G_h01_9FA2; extern long G_h01_9F92; extern long G_h01_9F96; extern long G_h01_9F9A;
extern long G_h01_9F8E; extern long G_h01_9F5A;
extern struct Descriptor G_h01_94EC[10]; extern struct Descriptor G_h01_958C[10]; extern struct Descriptor G_h01_962C[8];
extern struct Descriptor G_h01_96AC[8]; extern struct Descriptor G_h01_972C[3]; extern struct Descriptor G_h01_975C[3];
extern struct Descriptor G_h01_978C[7]; extern struct Descriptor G_h01_97FC[7]; extern struct Descriptor G_h01_986C[5];
extern struct Descriptor G_h01_98BC[9]; extern struct Descriptor G_h01_99DC[2]; extern struct Descriptor G_h01_99FC[2];
extern struct Descriptor G_h01_9A1C[5]; extern struct Descriptor G_h01_9A6C[5]; extern struct Descriptor G_h01_9ABC[3];
extern struct Descriptor G_h01_9AEC[1]; extern struct Descriptor G_h01_9AFC[5]; extern struct Descriptor G_h01_9B4C[7];
extern struct Descriptor G_h01_9BBC[7]; extern struct Descriptor G_h01_9C2C[6];
extern long request_disk(); extern long Open(); extern int arc_read_index(); extern long F_h00_291E();
extern int report_loader_error(); extern int F_h00_3C0E(); extern int F_h00_3BD2();
extern int F_h11_20F2(); extern int F_h11_6080(); extern int F_h11_506A(); extern int F_h11_67B0();
extern int F_h11_6A44(); extern int F_h11_2C96(); extern int F_h11_7194(); extern int F_h11_3926(); extern int F_h11_49EA();

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
            G_h01_7A96 = (struct Header *)F_h00_291E(1, 0L);
        else if (G_h01_7A94 == 1)
            G_h01_7A96 = (struct Header *)F_h00_291E(2, 0L);
        else
            G_h01_7A96 = (struct Header *)F_h00_291E(3, 0L);
        G_h01_8A3A = G_h01_7A96->count;
        if (G_h01_8A3A > 4000)
            report_loader_error(0x8A4);
        for (i = 0; i < G_h01_8A3A; i++)
            G_h01_7A9A[i] = G_h01_7A96->data[i];
        F_h00_3C0E(G_h01_7A96);
        F_h11_20F2(G_h01_7A9A);
        F_h11_6080(G_h01_7A9A);
        F_h11_506A(G_h01_7A9A);
        F_h11_67B0(G_h01_7A9A);
        F_h11_6A44(G_h01_7A9A);
        F_h11_2C96(G_h01_7A9A);
        F_h11_7194(G_h01_7A9A);
        F_h11_3926(G_h01_7A9A);
        F_h00_291E(4, G_h01_46CE);
        G_h01_9F5A = F_h00_291E(7, 0L);
        F_h11_49EA();
        F_h00_3BD2(G_h01_9F5A);
        G_h01_9F8E = F_h00_291E(0, 0L);
        G_h01_9F4E = F_h00_291E(5, 0L);
        G_h01_9F52 = F_h00_291E(6, 0L);
        G_h01_9F56 = F_h00_291E(17, 0L);
        G_h01_9F5E = F_h00_291E(8, 0L);
        G_h01_9F62 = F_h00_291E(9, 0L);
        G_h01_9F6A = F_h00_291E(11, 0L);
        G_h01_9F82 = F_h00_291E(12, 0L);
        G_h01_9F7E = F_h00_291E(13, 0L);
        G_h01_9F6E = F_h00_291E(14, 0L);
        G_h01_9F66 = F_h00_291E(10, 0L);
        G_h01_9F76 = F_h00_291E(15, 0L);
        G_h01_9F8A = F_h00_291E(16, 0L);
        G_h01_9F9E = F_h00_291E(18, 0L);
        G_h01_9FA2 = F_h00_291E(19, 0L);
        ((struct Object *)G_h01_9FA2)->state = 0;
        G_h01_9F92 = F_h00_291E(20, 0L);
        G_h01_9F96 = F_h00_291E(21, 0L);
        G_h01_9F9A = F_h00_291E(22, 0L);
        *(int *)G_h01_9F96 = 8;
        *((int *)G_h01_9F96 + 1) = 0xb2;
        ((struct Object *)G_h01_9F96)->state = 0;
        *(int *)G_h01_9F9A = 0x28;
        *((int *)G_h01_9F9A + 1) = 0xb1;
        ((struct Object *)G_h01_9F9A)->state = 0;
        for (i = 0; i < 5; i++) {
            G_h01_986C[i].object = G_h01_9F4E;
        }
        G_h01_986C[0].word4 = 0x14;
        G_h01_986C[1].word4 = 0x18;
        for (i = 0; i < 10; i++) {
            G_h01_94EC[i].object = G_h01_9F4E;
        }
        G_h01_94EC[0].object = G_h01_9F4E;
        G_h01_94EC[0].word4 = 0;
        G_h01_94EC[0].dy = 0x10;
        G_h01_94EC[1].word4 = 0x1;
        G_h01_94EC[2].word4 = 0x2;
        G_h01_94EC[3].word4 = 0x3;
        G_h01_94EC[4].word4 = 0x4;
        G_h01_94EC[5].word4 = 0x5;
        G_h01_94EC[5].dy = 0x10;
        G_h01_94EC[6].word4 = 0x6;
        G_h01_94EC[7].word4 = 0x7;
        G_h01_94EC[8].word4 = 0x8;
        G_h01_94EC[9].word4 = 0x9;
        for (i = 0; i < 10; i++) {
            G_h01_958C[i].object = G_h01_9F4E;
        }
        G_h01_958C[0].object = G_h01_9F4E;
        G_h01_958C[0].word4 = 0xa;
        G_h01_958C[0].dy = 0xfff0;
        G_h01_958C[1].word4 = 0xb;
        G_h01_958C[2].word4 = 0xc;
        G_h01_958C[3].word4 = 0xd;
        G_h01_958C[4].word4 = 0xe;
        G_h01_958C[5].word4 = 0xf;
        G_h01_958C[5].dy = 0xfff0;
        G_h01_958C[6].word4 = 0x10;
        G_h01_958C[7].word4 = 0x11;
        G_h01_958C[8].word4 = 0x12;
        G_h01_958C[9].word4 = 0x13;
        for (i = 0; i < 8; i++) {
            G_h01_962C[i].object = G_h01_9F4E;
        }
        G_h01_962C[0].word4 = 0x15;
        G_h01_962C[0].dy = 0xa;
        G_h01_962C[0].dx = 0;
        G_h01_962C[1].word4 = 0x14;
        G_h01_962C[1].dy = 0x2;
        G_h01_962C[1].dx = 0xfff4;
        G_h01_962C[2].word4 = 0x7;
        G_h01_962C[2].dy = 0x2;
        G_h01_962C[2].dx = 0xc;
        G_h01_962C[2].object = G_h01_9F56;
        G_h01_962C[3].word4 = 0x7;
        G_h01_962C[3].dy = 0x2;
        G_h01_962C[3].dx = 0x8;
        G_h01_962C[3].object = G_h01_9F56;
        G_h01_962C[4].word4 = 0x7;
        G_h01_962C[4].dy = 0x2;
        G_h01_962C[4].dx = 0xa;
        G_h01_962C[4].object = G_h01_9F56;
        G_h01_962C[5].word4 = 0x7;
        G_h01_962C[5].dy = 0x2;
        G_h01_962C[5].dx = 0xe;
        G_h01_962C[5].object = G_h01_9F56;
        G_h01_962C[6].word4 = 0x15;
        G_h01_962C[6].dy = 0xa;
        G_h01_962C[6].dx = 0;
        G_h01_962C[7].word4 = 0x14;
        G_h01_962C[7].dy = 0xfff6;
        G_h01_962C[7].dx = 0;
        for (i = 0; i < 8; i++) {
            G_h01_96AC[i].object = G_h01_9F4E;
        }
        G_h01_96AC[0].word4 = 0x19;
        G_h01_96AC[0].dy = 0xfff6;
        G_h01_96AC[0].dx = 0;
        G_h01_96AC[1].word4 = 0x18;
        G_h01_96AC[1].dy = 0xfffe;
        G_h01_96AC[1].dx = 0xfff4;
        G_h01_96AC[2].word4 = 0x3;
        G_h01_96AC[2].dy = 0xfffe;
        G_h01_96AC[2].dx = 0xc;
        G_h01_96AC[2].object = G_h01_9F56;
        G_h01_96AC[3].word4 = 0x3;
        G_h01_96AC[3].dy = 0xfffe;
        G_h01_96AC[3].dx = 0x8;
        G_h01_96AC[3].object = G_h01_9F56;
        G_h01_96AC[4].word4 = 0x3;
        G_h01_96AC[4].dy = 0xfffe;
        G_h01_96AC[4].dx = 0xa;
        G_h01_96AC[4].object = G_h01_9F56;
        G_h01_96AC[5].word4 = 0x3;
        G_h01_96AC[5].dy = 0xfffe;
        G_h01_96AC[5].dx = 0xe;
        G_h01_96AC[5].object = G_h01_9F56;
        G_h01_96AC[6].word4 = 0x19;
        G_h01_96AC[6].dy = 0xfff6;
        G_h01_96AC[6].dx = 0;
        G_h01_96AC[7].word4 = 0x18;
        G_h01_96AC[7].dy = 0xa;
        G_h01_96AC[7].dx = 0;
        for (i = 0; i < 3; i++) {
            G_h01_972C[i].object = G_h01_9F4E;
            G_h01_975C[i].object = G_h01_9F4E;
        }
        G_h01_972C[0].word4 = 0x15;
        G_h01_972C[0].dy = 0x10;
        G_h01_972C[1].word4 = 0x16;
        G_h01_972C[1].dy = 0;
        G_h01_972C[1].type = 0x7;
        G_h01_972C[2].word4 = 0x14;
        G_h01_972C[2].dy = 0xfff0;
        G_h01_975C[0].word4 = 0x19;
        G_h01_975C[0].dy = 0xfff0;
        G_h01_975C[1].word4 = 0x1a;
        G_h01_975C[1].dy = 0;
        G_h01_975C[1].type = 0x7;
        G_h01_975C[2].word4 = 0x18;
        G_h01_975C[2].dy = 0x10;
        for (i = 0; i < 7; i++) {
            G_h01_978C[i].object = G_h01_9F52;
        }
        G_h01_978C[0].word4 = 0x4;
        G_h01_978C[0].dx = 0xfff8;
        G_h01_978C[1].word4 = 0x5;
        G_h01_978C[1].dx = 0xfff4;
        G_h01_978C[2].word4 = 0x6;
        G_h01_978C[2].dx = 0xfff8;
        G_h01_978C[3].word4 = 0x7;
        G_h01_978C[3].dx = 0xfffa;
        G_h01_978C[4].word4 = 0x8;
        G_h01_978C[4].dx = 0;
        G_h01_978C[5].word4 = 0x7;
        G_h01_978C[5].dx = 0;
        G_h01_978C[6].word4 = 0x4;
        G_h01_978C[6].dx = 0xffeb;
        for (i = 0; i < 7; i++) {
            G_h01_97FC[i].object = G_h01_9F52;
        }
        G_h01_97FC[0].word4 = 0x4;
        G_h01_97FC[0].dx = 0x3;
        G_h01_97FC[1].word4 = 0x7;
        G_h01_97FC[1].dx = 0xe;
        G_h01_97FC[2].word4 = 0x8;
        G_h01_97FC[2].dx = 0;
        G_h01_97FC[3].word4 = 0x7;
        G_h01_97FC[3].dx = 0;
        G_h01_97FC[4].word4 = 0x6;
        G_h01_97FC[4].dx = 0x6;
        G_h01_97FC[5].word4 = 0x5;
        G_h01_97FC[5].dx = 0xa;
        G_h01_97FC[6].word4 = 0x4;
        G_h01_97FC[6].dx = 0x6;
        for (i = 0; i < 7; i++) {
            G_h01_9B4C[i].object = G_h01_9F52;
        }
        G_h01_9B4C[0].word4 = 0x4;
        G_h01_9B4C[0].dx = 0xfff9;
        G_h01_9B4C[1].word4 = 0x5;
        G_h01_9B4C[1].dx = 0x3;
        G_h01_9B4C[2].word4 = 0x6;
        G_h01_9B4C[2].dx = 0xfff9;
        G_h01_9B4C[3].word4 = 0x7;
        G_h01_9B4C[3].dx = 0xfffa;
        G_h01_9B4C[4].word4 = 0x8;
        G_h01_9B4C[4].dx = 0;
        G_h01_9B4C[5].word4 = 0x7;
        G_h01_9B4C[5].dx = 0;
        G_h01_9B4C[6].word4 = 0x4;
        G_h01_9B4C[6].dx = 0xffea;
        for (i = 0; i < 7; i++) {
            G_h01_9BBC[i].object = G_h01_9F52;
        }
        G_h01_9BBC[0].word4 = 0x4;
        G_h01_9BBC[0].dx = 0xfff9;
        G_h01_9BBC[1].word4 = 0x7;
        G_h01_9BBC[1].dx = 0x17;
        G_h01_9BBC[2].word4 = 0x8;
        G_h01_9BBC[2].dx = 0;
        G_h01_9BBC[3].word4 = 0x7;
        G_h01_9BBC[3].dx = 0;
        G_h01_9BBC[4].word4 = 0x6;
        G_h01_9BBC[4].dx = 0x6;
        G_h01_9BBC[5].word4 = 0x5;
        G_h01_9BBC[5].dx = 0x8;
        G_h01_9BBC[6].word4 = 0x4;
        G_h01_9BBC[6].dx = 0xfffc;
        for (i = 0; i < 9; i++) {
            G_h01_98BC[i].object = G_h01_9F56;
        }
        G_h01_98BC[0].word4 = 0x4;
        G_h01_98BC[1].word4 = 0x5;
        G_h01_98BC[2].word4 = 0;
        G_h01_98BC[2].object = G_h01_9F52;
        G_h01_98BC[2].dy = 0x5;
        G_h01_98BC[2].dx = 0xfff2;
        G_h01_98BC[3].word4 = 0;
        G_h01_98BC[3].object = G_h01_9F52;
        G_h01_98BC[3].dy = 0x5;
        G_h01_98BC[3].dx = 0xfff4;
        G_h01_98BC[4].word4 = 0;
        G_h01_98BC[4].object = G_h01_9F52;
        G_h01_98BC[4].dy = 0x5;
        G_h01_98BC[4].dx = 0xfff6;
        G_h01_98BC[5].word4 = 0x7;
        G_h01_98BC[5].dy = 0x5;
        G_h01_98BC[5].dx = 0xfff8;
        G_h01_98BC[6].word4 = 0x7;
        G_h01_98BC[6].dy = 0x5;
        G_h01_98BC[6].dx = 0x2;
        G_h01_98BC[7].word4 = 0x6;
        G_h01_98BC[7].dy = 0xd;
        G_h01_98BC[7].dx = 0x3;
        G_h01_98BC[8].word4 = 0x14;
        G_h01_98BC[8].object = G_h01_9F4E;
        G_h01_98BC[8].dy = 0xfff6;
        G_h01_98BC[8].dx = 0x4;
        G_h01_9AEC[0].object = G_h01_9F52;
        G_h01_9AEC[0].word4 = 0x9;
        G_h01_9AEC[0].type = 0x5;
        G_h01_99DC[0].object = G_h01_9F56;
        G_h01_99DC[0].word4 = 0x5;
        G_h01_99DC[1].object = G_h01_9F52;
        G_h01_99DC[1].word4 = 0;
        G_h01_99DC[1].dy = 0x4;
        G_h01_99DC[1].dx = 0xfff9;
        G_h01_99FC[0].object = G_h01_9F56;
        G_h01_99FC[0].word4 = 0x1;
        G_h01_99FC[1].object = G_h01_9F52;
        G_h01_99FC[1].word4 = 0x2;
        G_h01_99FC[1].dy = 0xfffc;
        G_h01_99FC[1].dx = 0xfff9;
        for (i = 0; i < 5; i++) {
            G_h01_9A6C[i].object = G_h01_9F4E;
        }
        G_h01_9A6C[0].word4 = 0x15;
        G_h01_9A6C[0].dy = 0xe;
        G_h01_9A6C[1].word4 = 0x4;
        G_h01_9A6C[1].dy = 0xfff8;
        G_h01_9A6C[1].object = G_h01_9F56;
        G_h01_9A6C[2].word4 = 0x7;
        G_h01_9A6C[2].type = 0x8;
        G_h01_9A6C[2].dx = 0xffe8;
        G_h01_9A6C[2].dy = 0xfff8;
        G_h01_9A6C[2].object = G_h01_9F56;
        G_h01_9A6C[3].word4 = 0x4;
        G_h01_9A6C[3].dy = 0x8;
        G_h01_9A6C[3].dx = 0x18;
        G_h01_9A6C[3].object = G_h01_9F56;
        G_h01_9A6C[4].word4 = 0x15;
        G_h01_9A6C[4].dy = 0x8;
        for (i = 0; i < 5; i++) {
            G_h01_9A1C[i].object = G_h01_9F4E;
        }
        G_h01_9A1C[0].word4 = 0x19;
        G_h01_9A1C[0].dy = 0xfff2;
        G_h01_9A1C[1].word4 = 0;
        G_h01_9A1C[1].dy = 0x8;
        G_h01_9A1C[1].object = G_h01_9F56;
        G_h01_9A1C[2].word4 = 0x3;
        G_h01_9A1C[2].type = 0x8;
        G_h01_9A1C[2].dx = 0xffe8;
        G_h01_9A1C[2].dy = 0x6;
        G_h01_9A1C[2].object = G_h01_9F56;
        G_h01_9A1C[3].word4 = 0;
        G_h01_9A1C[3].dy = 0xfffa;
        G_h01_9A1C[3].dx = 0x18;
        G_h01_9A1C[3].object = G_h01_9F56;
        G_h01_9A1C[4].word4 = 0x19;
        G_h01_9A1C[4].dy = 0xfff8;
        for (i = 0; i < 3; i++) {
            G_h01_9ABC[i].object = G_h01_9F52;
        }
        G_h01_9ABC[0].word4 = 0x4;
        G_h01_9ABC[0].dx = 0xfff8;
        G_h01_9ABC[1].word4 = 0x5;
        G_h01_9ABC[2].word4 = 0x4;
        for (i = 0; i < 5; i++) {
            G_h01_9AFC[i].object = G_h01_9F8E;
            G_h01_9AFC[i].type = 3;
        }
        G_h01_9AFC[0].word4 = 0;
        G_h01_9AFC[0].dy = 0xffe9;
        G_h01_9AFC[1].word4 = 0x1;
        G_h01_9AFC[2].word4 = 0x2;
        G_h01_9AFC[3].word4 = 0x3;
        G_h01_9AFC[4].word4 = 0x4;
        for (i = 0; i < 6; i++) {
            G_h01_9C2C[i].object = G_h01_9F62;
            G_h01_9C2C[i].dx = -6;
        }
        G_h01_9C2C[0].word4 = 0;
        G_h01_9C2C[0].word8 = 0;
        G_h01_9C2C[0].type = 0x1;
        G_h01_9C2C[1].word4 = 0x1;
        G_h01_9C2C[1].word8 = 0xa;
        G_h01_9C2C[1].type = 0x1;
        G_h01_9C2C[2].word4 = 0x2;
        G_h01_9C2C[2].type = 0x4;
        G_h01_9C2C[2].word8 = 0x17;
        G_h01_9C2C[3].word4 = 0x1;
        G_h01_9C2C[3].type = 0x1;
        G_h01_9C2C[3].word8 = 0xa;
        G_h01_9C2C[4].word4 = 0;
        G_h01_9C2C[4].word8 = 0;
        G_h01_9C2C[4].type = 0x1;
        G_h01_9C2C[5].word4 = 0x3;
        G_h01_9C2C[5].type = 0x3;
        G_h01_9C2C[5].word8 = 0xfffc;
    }
}
