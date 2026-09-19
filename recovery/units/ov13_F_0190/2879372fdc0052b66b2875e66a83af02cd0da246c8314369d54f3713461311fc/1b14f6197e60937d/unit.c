struct UiState {
    int x0;
    int y0;
    char pad0[48];
    char text0;
    char pad1;
    int x1;
    int y1;
    char pad2[48];
    char flag0;
    char pad3;
    int x2;
    int y2;
    char pad4[48];
    char flag1;
    char pad5;
    int x3;
    int y3;
    char pad6[48];
    char flag2;
    char pad7[379];
    int x4;
    int y4;
    char pad8[48];
    char flag3;
};

extern int G_h01_1422;
extern long G_h01_46CE;
extern long G_h01_46D2;
extern struct UiState G_h01_50E6;
extern int F_h00_0FDE();
extern int F_h00_291E();
extern int F_h00_8A46();
extern int F_h00_34E0();

F_h13_0000(a,b,c)
int a,b,c;
{
    F_h00_0FDE(1);
    if (!a && c) {
        F_h00_291E(3,G_h01_46CE);
        F_h00_291E(4,&G_h01_50E6.x1);
        F_h00_291E(5,&G_h01_50E6.x4);
        F_h00_291E(6,&G_h01_50E6.x2);
        F_h00_291E(7,&G_h01_50E6.x3);
        F_h00_291E(8,&G_h01_50E6.x0);
    }
        G_h01_50E6.x4=33;
        G_h01_50E6.y4=48;
        G_h01_50E6.flag3=0;
        G_h01_50E6.x1=120;
        G_h01_50E6.y1=8;
        G_h01_50E6.flag0=a;
        G_h01_50E6.x2=136;
        G_h01_50E6.y2=32;
        G_h01_50E6.flag1=0;
        G_h01_50E6.x3=120;
        G_h01_50E6.y3=48;
        G_h01_50E6.flag2=0;
        G_h01_50E6.x0=216;
        G_h01_50E6.y0=32;
        G_h01_50E6.text0=b;
    F_h00_8A46(G_h01_46CE,0L,0L,G_h01_46D2,
        0L,0L,320L,200L,192L,255L,0L);
    F_h00_34E0(&G_h01_50E6.x0);
    F_h00_34E0(&G_h01_50E6.x1);
    if (!G_h01_1422)
        F_h00_34E0(&G_h01_50E6.x4);
    if (!a) {
        F_h00_34E0(&G_h01_50E6.x2);
        F_h00_34E0(&G_h01_50E6.x3);
    }
}

/* Direct reconstruction candidate for ov13_F_012E. */
extern int G_h01_50EE;
extern int G_h01_50F0;
extern char G_h01_50F6;
extern int G_h01_5124;
extern int G_h01_5126;
extern char G_h01_512C;
extern int G_h01_515A;
extern int G_h01_515C;
extern char G_h01_5162;
extern int G_h01_5190;
extern int G_h01_5192;
extern char G_h01_5198;
extern int G_h01_5340;
extern int G_h01_5342;
extern char G_h01_5348;
extern int F_h00_3AE4();

F_h13_012E()
{
    F_h00_3AE4(&G_h01_50F6, G_h01_50EE, G_h01_50F0);
    F_h00_3AE4(&G_h01_512C, G_h01_5124, G_h01_5126);
    F_h00_3AE4(&G_h01_5162, G_h01_515A, G_h01_515C);
    F_h00_3AE4(&G_h01_5198, G_h01_5190, G_h01_5192);
    F_h00_3AE4(&G_h01_5348, G_h01_5340, G_h01_5342);
}


extern int F_h00_307C();
extern int F_h00_57D2();
extern int F_h00_34E0();
extern int F_h00_86A8();
extern int G_h01_511C;
extern int G_h01_5152;
extern char G_h01_5186;
extern int G_h01_5188;
extern char G_h01_51BC;

recovered()
{
    int i;

    F_h13_0000(0,0,0);
    F_h00_307C();
    F_h13_0000(0,0,0);
    F_h00_57D2(4);
    i=15;
    do {
        F_h00_34E0(&G_h01_511C);
        F_h00_34E0(&G_h01_5188);
        G_h01_5186=i%3;
        F_h00_34E0(&G_h01_5152);
        F_h00_307C();
        F_h00_86A8(5L);
        --i;
    } while (i>=3);
    F_h00_34E0(&G_h01_511C);
    F_h00_34E0(&G_h01_5152);
    G_h01_51BC=1;
    F_h00_34E0(&G_h01_5188);
    F_h00_57D2(35);
    F_h00_307C();
    F_h00_86A8(5L);
    F_h00_57D2(34);
    F_h13_0000(0,0,0);
    F_h00_34E0(&G_h01_511C);
    F_h00_34E0(&G_h01_5152);
    G_h01_51BC=1;
    F_h00_34E0(&G_h01_5188);
    F_h00_307C();
    F_h00_86A8(50L);
    i=1;
    do {
        F_h13_0000(i,0,0);
        F_h00_307C();
        F_h00_86A8(20L);
        ++i;
    } while (i<=3);
}

