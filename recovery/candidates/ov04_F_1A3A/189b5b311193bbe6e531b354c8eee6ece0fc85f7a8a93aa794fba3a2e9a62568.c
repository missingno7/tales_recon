/* Direct reconstruction candidate for ov04_F_1A3A. */
extern long G_h01_46CA;
extern int F_h00_8BC8();
extern int F_h00_4EC6();
extern int F_h00_0FDE();
extern int F_h00_4D04();
extern int F_h00_0640();
extern int F_h00_57D2();
extern int F_h00_435E();
extern int F_h00_134C();
extern int F_h00_307C();

recovered(choice)
int choice;
{
    F_h00_8BC8(G_h01_46CA, 0L);
    F_h00_4EC6();
    F_h00_0FDE(2);
    F_h00_4D04(30);
    if (choice) F_h00_0640(13);
    else F_h00_0640(14);
    F_h00_57D2(119);
    F_h00_435E();
    F_h00_134C(100);
    F_h00_4EC6();
    F_h00_307C();
}
