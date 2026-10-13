/* Candidate v2 (v1 with the leading space of the third string restored) for ov07_F_0000: setup calls, 3+5 table-driven calls, key state machine, closing screen. */
struct Rec54 { char b[54]; };

extern char G_h01_33E2;
extern int G_h01_0A92[8];
extern char G_h01_3232;
extern char G_h01_323A;
extern char G_h01_323C;
extern char G_h01_3242;
extern char G_h01_329E;
extern int G_h01_1466;
extern char G_h01_1766[1];
extern char *G_h01_46D6;
extern long G_h01_46CE;
extern long G_h01_46D2;
extern long G_h01_46DA;
extern int F_h00_435E();
extern int F_h00_57D2();
extern int F_h00_0FDE();
extern int F_h00_291E();
extern int F_h00_8A46();
extern long F_h00_86DC();
extern int F_h00_2816();
extern int F_h00_868C();
extern int F_h00_307C();
extern int F_h00_31AA();
extern int F_h00_4376();
extern int F_h00_330E();
extern int F_h00_0640();
extern int F_h00_35DC();
extern int F_h00_134C();
extern int F_h00_3AE4();
extern int F_h00_86A8();
extern int F_h07_1424();
extern int F_h07_03CC();
extern int F_h07_04AC();
extern int F_h07_0612();

recovered()
{
    unsigned char key;
    int flag;
    int i;
    int cnt;
    int y;
    int x;
    int u0e;
    long saved;
    int u14;

    u14 = 0;
    G_h01_33E2 = 0;
    F_h00_435E();
    F_h00_57D2(0);
    F_h00_0FDE(1);
    F_h00_291E(0x14, G_h01_46CE);
    F_h00_8A46(G_h01_46CE, 0L, 0L, G_h01_46D2, 0L, 0L, 320L, 200L, 192L, 255L, 0L);
    for (i = 0; i < 3; i++)
        F_h00_291E(G_h01_0A92[i], (char *)((struct Rec54 *)&G_h01_3232 + i));
    saved = G_h01_46DA;
    F_h00_0FDE(1);
    G_h01_46DA = F_h00_86DC("DT1:invart.arc", 1005L);
    F_h00_2816(G_h01_46DA);
    for (i = 3; i < 8; i++)
        F_h00_291E(G_h01_0A92[i], (char *)((struct Rec54 *)&G_h01_3232 + i));
    F_h00_868C(G_h01_46DA);
    G_h01_46DA = saved;
    F_h00_2816(G_h01_46DA);
    F_h00_57D2(30);
    F_h07_1424(&G_h01_3232, &G_h01_329E);
    cnt = 0;
    x = 10;
    y = 10;
    F_h07_03CC();
    F_h07_04AC(y, x);
    F_h00_307C();
    G_h01_46D6 = (char *)&G_h01_1466;
    F_h00_31AA((char *)&G_h01_1466);
    flag = 0;
    while (flag == 0) {
        key = F_h00_4376();
        if (key & 0x80) {
            F_h00_57D2(36);
            if (x == 15)
                flag = 1;
            else
                flag = F_h07_0612(x, &G_h01_3232);
            F_h07_03CC();
            F_h07_04AC(y, x);
            F_h00_307C();
        } else {
            key &= 0x3f;
            switch (key) {
            case 1:
                F_h00_57D2(36);
                x--;
                x &= 15;
                cnt--;
                if (cnt < 0) {
                    y--;
                    y &= 15;
                    cnt = 0;
                }
                F_h07_03CC();
                F_h07_04AC(y, x);
                F_h00_307C();
                F_h00_86A8(10L);
                break;
            case 5:
                F_h00_57D2(36);
                x++;
                x &= 15;
                cnt++;
                if (cnt > 5) {
                    y++;
                    y &= 15;
                    cnt = 5;
                }
                F_h07_03CC();
                F_h07_04AC(y, x);
                F_h00_307C();
                F_h00_86A8(10L);
                break;
            default:
                u14 = 0;
                break;
            }
        }
    }
    F_h00_330E();
    if (G_h01_33E2) {
        F_h00_0640(1);
        F_h00_35DC(176, 60, "I'll put that", 1, 0);
        F_h00_35DC(176, 76, "order through", 1, 0);
        F_h00_35DC(176, 92, " right away,  ", 1, 0);
        F_h00_35DC(176, 108, " Mr. McDuck!", 1, 0);
        F_h00_330E();
        F_h00_307C();
        G_h01_46D6 = G_h01_1766;
        F_h00_31AA(G_h01_1766);
        if (F_h00_134C(50))
            F_h00_57D2(36);
    }
    for (i = 0; i < 8; i++)
        F_h00_3AE4((char *)((struct Rec54 *)&G_h01_3242 + i),
                   *(short *)((struct Rec54 *)&G_h01_323A + i),
                   *(short *)((struct Rec54 *)&G_h01_323C + i));
}
