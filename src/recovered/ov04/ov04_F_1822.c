/* Direct reconstruction candidate for ov04_F_1822. */
extern long G_h01_46CE;
extern long G_h01_46D2;
extern int BltBitMap();
extern int F_h00_307C();
extern int poll_controller_and_keyboard_input();
extern int Delay();

recovered()
{
    int inset;

    inset = 80;
    do {
        BltBitMap(G_h01_46CE, (long)inset, (long)inset,
            G_h01_46D2, (long)inset, (long)inset,
            (long)(320 - inset - inset), (long)(200 - inset - inset),
            (long)192, (long)255, 0L);
        F_h00_307C();
        poll_controller_and_keyboard_input();
        Delay(2L);
        inset -= 8;
    } while (inset >= 0);
}
