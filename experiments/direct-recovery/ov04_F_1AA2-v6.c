extern long F_h00_463E();
extern int F_h00_4EC6();
extern int F_h00_0FDE();
extern int F_h00_4D04();
extern int F_h00_0640();
extern int F_h00_57D2();
extern int F_h00_2816();
extern int F_h00_134C();
extern long G_h01_46DA;

recovered(a)
int a;
{
    int value;

    if (a) {
        value=(unsigned)F_h00_463E()%3;
        F_h00_4EC6();
        F_h00_0FDE(2);
        switch (value) {
        case 0:
            F_h00_4D04(9);
            break;
        case 2:
            F_h00_4D04(17);
            break;
        case 3:
            F_h00_4D04(18);
            break;
        }
        F_h00_0640(12);
        F_h00_57D2(119);
        F_h00_0FDE(1);
        F_h00_2816(G_h01_46DA);
    } else {
        value=(F_h00_463E()&1) ? 15 : 16;
        F_h00_4EC6();
        F_h00_0FDE(2);
        F_h00_4D04(value);
        F_h00_0640(11);
        F_h00_57D2(119);
        F_h00_0FDE(1);
        F_h00_2816(G_h01_46DA);
        F_h00_134C(100);
    }
}
