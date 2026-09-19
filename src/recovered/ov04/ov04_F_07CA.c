/* Direct recovery candidate for ov04_F_07CA. */
extern long G_h01_46CE;
extern long G_h01_46D2;
extern int G_h01_511C; extern int G_h01_511E; extern char G_h01_5150;
extern int G_h01_5124; extern int G_h01_5126; extern char G_h01_512C;
extern int G_h01_5338; extern int G_h01_533A; extern char G_h01_536C;
extern int G_h01_5340; extern int G_h01_5342; extern char G_h01_5348;
extern int G_h01_5152; extern int G_h01_5154; extern char G_h01_5186;
extern int G_h01_515A; extern int G_h01_515C; extern char G_h01_5162;
extern int G_h01_5188; extern int G_h01_518A; extern char G_h01_51BC;
extern int G_h01_5190; extern int G_h01_5192; extern char G_h01_5198;
extern int F_h00_0FDE();
extern int F_h00_291E();
extern int F_h00_8A46();
extern int F_h00_34E0();
extern int F_h00_3AE4();

recovered()
{
    F_h00_0FDE(1);
    F_h00_291E(3, G_h01_46CE);
    F_h00_8A46(G_h01_46CE, 0L, 0L, G_h01_46D2,
        0L, 0L, 320L, 200L, 192L, 255L, 0L);

    F_h00_291E(4, &G_h01_511C);
    G_h01_511C = 120;
    G_h01_511E = 8;
    G_h01_5150 = 0;
    F_h00_34E0(&G_h01_511C);
    F_h00_3AE4(&G_h01_512C, G_h01_5124, G_h01_5126);

    F_h00_291E(5, &G_h01_5338);
    G_h01_5338 = 32;
    G_h01_533A = 48;
    G_h01_536C = 0;
    F_h00_34E0(&G_h01_5338);
    F_h00_3AE4(&G_h01_5348, G_h01_5340, G_h01_5342);

    F_h00_291E(6, &G_h01_5152);
    G_h01_5152 = 136;
    G_h01_5154 = 32;
    G_h01_5186 = 0;
    F_h00_34E0(&G_h01_5152);
    F_h00_3AE4(&G_h01_5162, G_h01_515A, G_h01_515C);

    F_h00_291E(7, &G_h01_5188);
    G_h01_5188 = 120;
    G_h01_518A = 48;
    G_h01_51BC = 0;
    F_h00_34E0(&G_h01_5188);
    F_h00_3AE4(&G_h01_5198, G_h01_5190, G_h01_5192);

    F_h00_8A46(G_h01_46D2, 0L, 0L, G_h01_46CE,
        0L, 0L, 320L, 200L, 192L, 255L, 0L);
}
