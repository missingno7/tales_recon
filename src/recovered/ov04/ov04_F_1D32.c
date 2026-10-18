extern long G_h01_46CE;
extern long G_h01_46D2;
extern char *G_h01_46D6;
extern char G_h01_1826[1];
extern char G_h01_14A6[1];

extern int play_sound();
extern int F_h00_291E();
extern int F_h00_330E();
extern int BltBitMap();
extern int F_h00_307C();
extern int F_h00_31AA();
extern int F_h04_18A6();
extern int wait_for_fire_input();
extern int F_h00_4EC6();

recovered()
{
    int unused;

    play_sound(0);
    F_h00_291E(1, G_h01_46CE);
    F_h00_330E();
    BltBitMap(G_h01_46CE, 0L, 0L, G_h01_46D2,
        0L, 0L, 320L, 200L, 192L, 255L, 0L);
    F_h00_307C();
    G_h01_46D6 = G_h01_1826;
    F_h00_31AA(G_h01_1826);
    BltBitMap(G_h01_46CE, 0L, 0L, G_h01_46D2,
        0L, 0L, 320L, 200L, 192L, 255L, 0L);
    F_h04_18A6();
    F_h00_291E(0, G_h01_46CE);
    BltBitMap(G_h01_46CE, 0L, 0L, G_h01_46D2,
        0L, 0L, 320L, 200L, 192L, 255L, 0L);
    F_h00_330E();
    F_h00_307C();
    G_h01_46D6 = G_h01_14A6;
    F_h00_31AA(G_h01_14A6);
    if (wait_for_fire_input(40))
        play_sound(36);
    play_sound(0);
    F_h00_4EC6();
}
