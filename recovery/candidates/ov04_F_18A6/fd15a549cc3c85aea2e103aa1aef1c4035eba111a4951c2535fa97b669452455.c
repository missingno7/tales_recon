extern char G_h01_06FE[624];

extern int F_h00_435E();
extern int F_h00_134C();
extern void F_h00_57D2();
extern int F_h00_35DC();
extern int F_h00_307C();

recovered()
{
    int i;

    F_h00_435E();
    if (F_h00_134C(20)) {
        F_h00_57D2(36);
        return;
    }
    F_h00_35DC(0, 192, "                                        ", 1, 3);
    F_h00_307C();
    F_h00_35DC(0, 192, "                                        ", 1, 3);
    i = 0;
    do {
        F_h00_35DC(64, 192, G_h01_06FE + (long)i * 26, 1, 3);
        F_h00_307C();
        if (F_h00_134C(20)) {
            F_h00_57D2(36);
        return;
        }
        ++i;
    } while (i < 24);
    F_h00_35DC(0, 192, "                                        ", 1, 3);
    F_h00_307C();
    F_h00_35DC(0, 192, "                                        ", 1, 3);
    F_h00_307C();
}
