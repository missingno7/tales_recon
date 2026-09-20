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
extern int F_h00_3870();
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

recovered()
{
    int unused;

    F_h00_4EC6();
    F_h00_53E6();
    F_h00_330E();
    G_h01_5378 = F_h00_89D0("intuition.library", 0L);
    if (!G_h01_5378)
        recovered("InitAV:\tcannot open intuition library\n");
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
