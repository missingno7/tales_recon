struct BitmapScreenRecord { char pad0[4]; long field_4; char pad8[16]; char field_18; char field_19; char field_1a; char field_1b; char field_1c; char pad1d[5]; short field_22; };
struct BitmapLayout { char pad0[8]; long planes[8]; };
struct ScreenInfo { char pad0[12]; struct BitmapScreenRecord *field_c; };
struct S53B8 { long field_0; long field_4; };

extern long G_h01_0036;
extern long G_h01_004E;
extern long G_h01_0066;
extern long G_h01_0072;
extern long G_h01_0078;
extern long G_h01_00AE;
extern long G_h01_00C0;
extern long G_h01_010E;
extern long G_h01_0126;
extern long G_h01_012C;
extern long G_h01_0132;
extern long G_h01_0138;
extern long G_h01_013E;
extern long G_h01_0144;
extern long G_h01_0174;
extern long G_h01_0180;
extern long G_h01_0186;
extern long G_h01_018C;
extern long G_h01_0192;
extern long G_h01_0198;
extern long G_h01_019E;
extern long G_h01_01AA;
extern long G_h01_01B0;
extern long G_h01_01BC;
extern long G_h01_01C2;
extern long G_h01_01C8;
extern long G_h01_01CE;
extern long G_h01_01E0;
extern long G_h01_01E6;
extern long G_h01_01F2;
extern long G_h01_01F8;
extern long G_h01_020A;

extern short G_h01_0970;
extern long G_h01_2EB4;
extern long G_h01_2EB8;
extern short G_h01_2EBC;
extern short G_h01_2EBE;
extern long G_h01_2EC0;
extern long G_h01_2EC8[8];
extern long G_h01_2EE8[8];
extern long G_h01_2EF0;
extern struct BitmapScreenRecord *G_h01_46CA;
extern struct BitmapLayout *G_h01_46CE;
extern long G_h01_46D2;
extern long G_h01_46F8;
extern long G_h01_5370;
extern long G_h01_5374;
extern long G_h01_5378;
extern long G_h01_537C;
extern long G_h01_5380;
extern struct ScreenInfo *G_h01_5384;
extern long G_h01_5388;
extern long G_h01_538C;
extern unsigned char G_h01_5390;
extern long G_h01_5392;
extern long G_h01_5396;
extern short G_h01_539A;
extern char G_h01_539C;
extern char G_h01_539D;
extern long G_h01_53A2;
extern long G_h01_53A6;
extern long G_h01_53B4;
extern long G_h01_53B8;
extern short G_h01_53CC;
extern short G_h01_53CE;
extern long G_h01_53D8;
extern long G_h01_53DC;
extern long G_h01_53E0;
extern long G_h01_53E4;
extern long G_h01_53E8;
extern long G_h01_53EC;
extern long G_h01_53F0;
extern long G_h01_53F4;
extern char G_h01_53F8;
extern long G_h01_5422;
extern long G_h01_5426;
extern long G_h01_542A;
extern long G_h01_544A;

struct GraphicsBaseView { char pad[34]; long view; };
struct S3 { char pad[8]; long field_8; long field_c; };
struct S2 { char pad[4]; struct S3 *field_4; };
struct S1 { char pad[36]; struct S2 *field_24; };
struct S0 { struct S1 *field_0; };
struct InitBlock { char first; char pad[11]; long field_c; long field_10; };
struct Layer { char pad[0xb8]; long field_b8; };

extern long F_h00_89D0();
extern int F_h04_27FE();
extern long F_h00_876C();
extern int F_h04_26F0();
extern int F_h00_37C8();
extern int F_h00_8C66();
extern long F_h00_8926();
extern long F_h00_8CD0();
extern long F_h00_8C98();
extern long F_h00_8960();
extern long F_h00_3870();
extern int F_h00_8C6E();
extern int F_h00_8C86();
extern int F_h00_3930();
extern int F_h00_8AF6();
extern int F_h00_8534();
extern int F_h00_8B08();
extern int F_h00_8B14();
extern long F_h00_8AEA();
extern int F_h00_8B3E();
extern int F_h00_8B5E();
extern int F_h00_8B32();
extern long F_h00_8B6A();
extern int F_h00_8BB8();
extern int F_h00_8BA8();
extern int F_h00_8B88();
extern int F_h00_8BC8();
extern int F_h00_307C();
extern int F_h00_330E();
extern int F_h00_8AD2();
extern int F_h00_4676();
extern int F_h00_50E8();
extern int F_h00_897C();
extern int F_h00_8784();

recovered()
{
    unsigned int i;
    long memory;
    struct Layer *layer;
    long size;
    long unused_slot;
    long probe;

    G_h01_5374 = F_h00_89D0("graphics.library", 0L);
    if (!G_h01_5374)
        F_h04_27FE("InitAV:\tcannot open graphics library\n");
    G_h01_53DC = ((struct GraphicsBaseView *)G_h01_5374)->view;
    G_h01_5378 = F_h00_89D0("intuition.library", 0L);
    if (!G_h01_5378)
        F_h04_27FE("InitAV:\tcannot open intuition library\n");

    size = F_h00_876C(2L);
    if (size < 0x45948L)
        F_h04_26F0("Insufficient Chip Memory!");
    i = F_h00_37C8(0x40f10L);
    if (i < 0)
        F_h04_26F0("Memory Fragmentation:  Can't allocate enough contiguous chip memory.");

    i = F_h00_8C66();
    if (i)
        G_h01_53F8 = 1;
    else
        G_h01_53F8 = 0;
    if (G_h01_53F8) {
        G_h01_5422 = F_h00_8926(0x3e80L, 0x10002L);
        G_h01_5426 = F_h00_8926(0x3e80L, 0x10002L);
        if (!G_h01_5422 || !G_h01_5426)
            F_h04_26F0("Insufficient Chip Memory!");
    } else {
        G_h01_5422 = ((struct S0 *)G_h01_53DC)->field_0->field_24->field_4->field_8;
        G_h01_5426 = ((struct S0 *)G_h01_53DC)->field_0->field_24->field_4->field_c;
    }

    size = F_h00_876C(2L);
    if (size < 0x4a38L) {
        F_h04_26F0("Insufficient Chip Memory!");
    } else {
        size = 0x4a38L;
        do {
            probe = F_h00_8926(size, 2L);
            if (!probe)
                size -= 0x1f4L;
        } while (!probe);
        F_h00_897C(probe, size);
        if (size < 0x4a38L)
            F_h04_26F0("Memory Fragmentation:  Can't allocate enough contiguous chip memory.");
    }

    G_h01_537C = F_h00_89D0("layers.library", 0L);
    if (!G_h01_537C)
        F_h04_27FE("InitAV:\tcannot open layers library\n");
    G_h01_5380 = F_h00_8CD0();
    if (!G_h01_5380)
        F_h04_27FE("InitAV:\tcannot allocate Layer_Info");

    G_h01_5384 = F_h00_8C98(G_h01_5380, &G_h01_2EC0, 0L, 0L, 0x13fL, 0xc7L, 1L);
    layer = (struct Layer *)F_h00_8960(0L);
    layer->field_b8 = 0xffffffffL;
    G_h01_53EC = F_h00_3870(&G_h01_542A, 0xe8L);
    F_h00_8C6E(G_h01_53EC, 0xe8L);
    ((struct InitBlock *)G_h01_53EC)->first = 8;
    G_h01_53F0 = ((struct InitBlock *)G_h01_53EC)->field_c;
    ((struct InitBlock *)G_h01_53EC)->field_c = 0L;
    G_h01_53F4 = ((struct InitBlock *)G_h01_53EC)->field_10;
    ((struct InitBlock *)G_h01_53EC)->field_10 = 10L;
    F_h00_8C86(G_h01_53EC, 0xe8L, 1L);
    F_h00_3930(&G_h01_542A, G_h01_53EC, 0xe8L);
    F_h00_8784(G_h01_5378);

    G_h01_544A = F_h00_3870(&G_h01_542A, 0x4000L);
    if (!G_h01_544A)
        F_h00_8534(-1);
    F_h00_8B08(&G_h01_53A2);
    F_h00_8B14(&G_h01_53B4);
    G_h01_53A2 = &G_h01_53B4;

    F_h00_8AF6(&G_h01_2EC0, (long)G_h01_0970, 0x140L, 0xc8L);
    memory = F_h00_3870(&G_h01_542A, (long)G_h01_0970 * 0x1f40L);
    if (!memory)
        F_h00_8534(-1);
    for (i = 0; i < G_h01_0970; ++i)
        G_h01_2EC8[i] = memory + (long)i * 0x1f40L;

    F_h00_8AF6(&G_h01_2EE8, (long)G_h01_0970, 0x140L, 0xc8L);
    memory = F_h00_3870(&G_h01_542A, (long)G_h01_0970 * 0x1f40L);
    if (!memory)
        F_h00_8534(-1);
    for (i = 0; i < G_h01_0970; ++i)
        ((long *)&G_h01_2EF0)[i] = memory + (long)i * 0x1f40L;

    G_h01_46CE = F_h00_3870(&G_h01_542A, 0x28L);
    F_h00_8AF6(G_h01_46CE, (long)G_h01_0970, 0x140L, 0xc8L);
    memory = F_h00_3870(&G_h01_542A, (long)G_h01_0970 * 0x1f40L);
    if (!memory)
        F_h00_8534(-1);
    for (i = 0; i < G_h01_0970; ++i)
        G_h01_46CE->planes[i] = memory + (long)i * 0x1f40L;

    G_h01_2EB8 = &G_h01_2EC0;
    G_h01_2EBC = 0;
    G_h01_2EBE = 0;
    G_h01_2EB4 = 0L;
    G_h01_53CC = 0x140;
    G_h01_53CE = 0xc8;
    G_h01_53D8 = &G_h01_2EB4;
    G_h01_53E8 = F_h00_8AEA(0x20L);
    G_h01_53B8 = G_h01_53E8;
    G_h01_5392 = ((struct S53B8 *)G_h01_53B8)->field_4;
    F_h00_8B3E(&G_h01_53A2, &G_h01_53B4);
    F_h00_8B5E(&G_h01_53A2);
    G_h01_53E0 = G_h01_53A6;
    G_h01_53A6 = 0L;
    G_h01_2EB8 = &G_h01_2EE8;
    G_h01_53B8 = G_h01_53E8;
    F_h00_8B3E(&G_h01_53A2, &G_h01_53B4);
    F_h00_8B5E(&G_h01_53A2);
    G_h01_53E4 = G_h01_53A6;
    F_h00_8B32(&G_h01_53A2);

    G_h01_46CA = G_h01_5384->field_c;
    G_h01_46CA->field_4 = (long)&G_h01_2EC0;
    G_h01_46CA->field_18 = 0xff;
    G_h01_46CA->field_19 = 0x1f;
    G_h01_46CA->field_1a = 2;
    G_h01_46CA->field_1b = 1;
    G_h01_46CA->field_1c = 0;
    G_h01_46CA->field_22 = -1;

    G_h01_5396 = "topaz.font";
    G_h01_539A = 8;
    G_h01_539C = 0;
    G_h01_539D = 0;
    G_h01_46F8 = F_h00_8B6A(&G_h01_5396);
    if (!G_h01_46F8)
        F_h04_27FE("InitAV:\tcannot open font");
    F_h00_8BB8(G_h01_46CA, G_h01_46F8);
    F_h00_8BA8(G_h01_46CA, 0L);
    F_h00_8B88(G_h01_46CA, 0x1fL);
    G_h01_5370 = (long)((char *)G_h01_46CA + 0x19L);
    G_h01_5388 = &G_h01_2EC0;
    G_h01_538C = &G_h01_2EE8;
    G_h01_5390 = 0;
    G_h01_46D2 = ((long *)&G_h01_5388)[G_h01_5390];
    F_h00_8BC8(G_h01_46CA, 0L);
    F_h00_307C();
    F_h00_8BC8(G_h01_46CA, 0L);
    F_h00_330E();
    for (i = 0; i < 8; ++i)
        F_h00_8AD2((long)i);
    F_h00_4676();
    F_h00_50E8();
}

extern long G_h01_5422;
extern long G_h01_5426;
extern char G_h01_53F8;
extern char G_h01_53FA;
extern char G_h01_53FB;
extern char G_h01_53FC;
extern int G_h01_53FE;
extern int G_h01_5400;
extern long G_h01_5402;
extern long G_h01_5406;
extern long G_h01_540A;
extern char G_h01_540E;
extern char G_h01_540F;
extern char G_h01_5410;
extern int G_h01_5412;
extern int G_h01_5414;
extern long G_h01_5416;
extern char *G_h01_541A;
extern long G_h01_541E;
extern long G_h01_5374;
extern long G_h01_5378;

extern int F_h00_897C();
extern int F_h00_3850();
extern int F_h00_8C7E();
extern int F_h00_8C48();
extern int F_h00_8784();
extern int F_h00_8534();

F_h04_26F0(arg)
long arg;
{
    if (G_h01_5422)
        F_h00_897C(G_h01_5422, 0x3e80L);
    if (G_h01_5426)
        F_h00_897C(G_h01_5426, 0x3e80L);
    F_h00_3850(0x40f10L);
    if (G_h01_53F8)
        F_h00_8C7E();
    G_h01_53FA = 0;
    G_h01_53FB = 1;
    G_h01_53FC = 1;
    G_h01_53FE = 6;
    G_h01_5400 = 3;
    G_h01_5402 = 0;
    G_h01_5406 = arg;
    G_h01_540A = 0;
    G_h01_540E = 0;
    G_h01_540F = 1;
    G_h01_5410 = 1;
    G_h01_5412 = 6;
    G_h01_5414 = 3;
    G_h01_5416 = 0;
    G_h01_541A = "OK";
    G_h01_541E = 0;
    F_h00_8C48(0L, &G_h01_53FA, 0L, &G_h01_540E, 0L, 0L, 0x280L, 0x28L);
    F_h00_8784(G_h01_5374);
    F_h00_8784(G_h01_5378);
    F_h00_8534(0);
}

extern long G_h01_5374;
extern long G_h01_5378;
extern long G_h01_537C;
extern long G_h01_5380;
extern long G_h01_5384;
extern long G_h01_53B4;
extern long G_h01_53E0;
extern long G_h01_53E4;
extern long G_h01_53E8;
extern long G_h01_53F0;
extern long G_h01_53F4;
extern char G_h01_53F8;
extern long G_h01_5422;
extern long G_h01_5426;
extern long G_h01_542A;
extern long G_h01_46DA;
extern long G_h01_46F8;

struct InitBlock { char pad[12]; long field_c; long field_10; };
struct S3 { char pad[8]; long field_8; long field_c; };
struct S2 { char pad[4]; struct S3 *field_4; };
struct S1 { char pad[36]; struct S2 *field_24; };
struct S0 { struct S1 *field_0; };
extern struct InitBlock *G_h01_53EC;
extern struct S0 *G_h01_53DC;

extern int F_h00_4EC6();
extern int F_h00_53E6();
extern int F_h00_330E();
extern long F_h00_89D0();
extern long F_h00_3870();
extern int F_h00_8C6E();
extern int F_h00_8C86();
extern int F_h00_3930();
extern int F_h00_3850();
extern int F_h00_897C();
extern int F_h00_8A8A();
extern int F_h00_868C();
extern int F_h00_8A9C();
extern int F_h00_8CB6();
extern int F_h00_8CC4();
extern int F_h00_8B32();
extern int F_h00_8ABA();
extern int F_h00_8ADE();
extern int F_h00_8AC6();
extern int F_h00_8C66();
extern int F_h00_8C7E();
extern int F_h00_8784();
extern int F_h00_8534();

F_h04_27FE()
{
    int unused;

    F_h00_4EC6();
    F_h00_53E6();
    F_h00_330E();
    G_h01_5378 = F_h00_89D0("intuition.library", 0L);
    if (!G_h01_5378)
        F_h04_27FE("InitAV:\tcannot open intuition library\n");
    G_h01_53EC = F_h00_3870(&G_h01_542A, 0xe8L);
    F_h00_8C6E(G_h01_53EC, 0xe8L);
    G_h01_53EC->field_c = G_h01_53F0;
    G_h01_53EC->field_10 = G_h01_53F4;
    F_h00_8C86(G_h01_53EC, 0xe8L, 1L);
    F_h00_3930(&G_h01_542A, G_h01_53EC, 0xe8L);
    F_h00_3850(0x40f10L);
    if (G_h01_53F8) {
        if (G_h01_5422)
            F_h00_897C(G_h01_5422, 0x3e80L);
        if (G_h01_5426)
            F_h00_897C(G_h01_5426, 0x3e80L);
    } else {
        F_h00_8A8A(G_h01_53DC->field_0->field_24->field_4->field_8, 0x3e80L, 0L);
        F_h00_8A8A(G_h01_53DC->field_0->field_24->field_4->field_c, 0x3e80L, 0L);
    }
    F_h00_868C(G_h01_46DA);
    F_h00_8A9C(G_h01_46F8);
    F_h00_8CB6(G_h01_5380, G_h01_5384);
    F_h00_8CC4(G_h01_5380);
    F_h00_8B32(G_h01_53DC);
    F_h00_8ABA(G_h01_53E8);
    F_h00_8ADE(&G_h01_53B4);
    F_h00_8AC6(G_h01_53E0);
    F_h00_8AC6(G_h01_53E4);
    F_h00_8C66();
    F_h00_8C7E();
    F_h00_8784(G_h01_537C);
    F_h00_8784(G_h01_5378);
    F_h00_8784(G_h01_5374);
    F_h00_8534(0);
}

