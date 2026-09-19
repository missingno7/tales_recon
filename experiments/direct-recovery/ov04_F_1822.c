/* Direct reconstruction candidate for ov04_F_1822. */
extern long G_h01_46CE;
extern long G_h01_46D2;
extern int F_h00_8A46();
extern int F_h00_307C();
extern int F_h00_4376();
extern int F_h00_86A8();

recovered()
{
    int inset;

    inset = 80;
    do {
        F_h00_8A46(G_h01_46CE, (long)inset, (long)inset,
            G_h01_46D2, (long)inset, (long)inset,
            (long)(320 - inset - inset), (long)(200 - inset - inset),
            (long)192, (long)255, 0L);
        F_h00_307C();
        F_h00_4376();
        F_h00_86A8(2L);
        inset -= 8;
    } while (inset >= 0);
}
