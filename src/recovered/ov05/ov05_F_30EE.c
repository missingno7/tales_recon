extern int G_h01_5E40;
extern char G_h01_5E41;
extern char G_h01_5482;
extern int G_h01_544E;
extern int F_h05_131C();
extern int F_h00_307C();
extern unsigned int F_h00_463E();
extern int play_sound();

recovered()
{
    int i;
    int saved;
    int cur;
    int flag;

    saved = G_h01_5E40;
    cur = G_h01_5E40;
    flag = 1;
    play_sound(46);
    for (i = 0; i < 6 || flag; i++) {
        if (flag) {
            cur = F_h00_463E() & 15;
            if (cur != saved)
                flag = 0;
            if (i >= 6)
                i = 0;
        }
        G_h01_5E40 += 2;
        if (G_h01_5E40 > 15)
            G_h01_5E40 = 0;
        G_h01_5482 = G_h01_5E41;
        F_h05_131C(&G_h01_544E);
        F_h00_307C();
    }
    if (cur == 4)
        cur = 5;
    G_h01_5E40 = cur;
}
