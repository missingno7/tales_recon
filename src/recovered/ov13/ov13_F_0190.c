extern int F_h13_0000();
extern int F_h00_307C();
extern int play_sound();
extern int F_h00_34E0();
extern int Delay();
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
    play_sound(4);
    i=15;
    do {
        F_h00_34E0(&G_h01_511C);
        F_h00_34E0(&G_h01_5188);
        G_h01_5186=i%3;
        F_h00_34E0(&G_h01_5152);
        F_h00_307C();
        Delay(5L);
        --i;
    } while (i>=3);
    F_h00_34E0(&G_h01_511C);
    F_h00_34E0(&G_h01_5152);
    G_h01_51BC=1;
    F_h00_34E0(&G_h01_5188);
    play_sound(35);
    F_h00_307C();
    Delay(5L);
    play_sound(34);
    F_h13_0000(0,0,0);
    F_h00_34E0(&G_h01_511C);
    F_h00_34E0(&G_h01_5152);
    G_h01_51BC=1;
    F_h00_34E0(&G_h01_5188);
    F_h00_307C();
    Delay(50L);
    i=1;
    do {
        F_h13_0000(i,0,0);
        F_h00_307C();
        Delay(20L);
        ++i;
    } while (i<=3);
}
