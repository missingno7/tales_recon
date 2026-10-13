/* resident_F_0640: loads the screen asset selected by case a; cases 11-14 then also set G_h01_46D6 and call F_h00_31AA with it. i1 is unused: the original 4-byte frame places flag at -3(a5). */
extern int F_h00_8BC8();
extern int F_h00_0FDE();
extern int F_h00_2816();
extern int F_h00_330E();
extern int F_h00_291E();
extern int F_h00_8A46();
extern int F_h00_307C();
extern int F_h00_31AA();
extern int F_h00_435E();
extern long G_h01_46CA;
extern long G_h01_46CE;
extern long G_h01_46D2;
extern char *G_h01_46D6;
extern long G_h01_46DA;
extern char G_h01_1926;
extern char G_h01_1966;
extern char G_h01_19A6;

recovered(a)
int a;
{
    int i1;
    char flag;

    flag = 0;
    F_h00_8BC8(G_h01_46CA, 0L);
    F_h00_0FDE(1);
    F_h00_2816(G_h01_46DA);
    F_h00_330E();
    switch (a) {
    case 3:
        F_h00_291E(30, G_h01_46CE);
        F_h00_8A46(G_h01_46CE, 0L, 0L, G_h01_46D2, 0L, 0L, 320L, 200L, 192L, 255L, 0L);
        break;
    case 1:
    case 9:
        F_h00_291E(32, G_h01_46CE);
        F_h00_8A46(G_h01_46CE, 0L, 0L, G_h01_46D2, 0L, 0L, 320L, 200L, 192L, 255L, 0L);
        break;
    case 2:
        F_h00_291E(41, G_h01_46CE);
        F_h00_8A46(G_h01_46CE, 0L, 0L, G_h01_46D2, 0L, 0L, 320L, 200L, 192L, 255L, 0L);
        break;
    case 6:
        F_h00_291E(35, G_h01_46D2);
        break;
    case 10:
        F_h00_291E(33, G_h01_46CE);
        F_h00_8A46(G_h01_46CE, 0L, 0L, G_h01_46D2, 0L, 0L, 320L, 200L, 192L, 255L, 0L);
        break;
    case 11:
        F_h00_291E(38, G_h01_46CE);
        F_h00_8A46(G_h01_46CE, 0L, 0L, G_h01_46D2, 0L, 0L, 320L, 200L, 192L, 255L, 0L);
        F_h00_307C();
        G_h01_46D6 = &G_h01_1926;
        F_h00_31AA(&G_h01_1926);
        break;
    case 12:
        F_h00_291E(39, G_h01_46CE);
        F_h00_8A46(G_h01_46CE, 0L, 0L, G_h01_46D2, 0L, 0L, 320L, 200L, 192L, 255L, 0L);
        F_h00_307C();
        G_h01_46D6 = &G_h01_1926;
        F_h00_31AA(&G_h01_1926);
        break;
    case 13:
        F_h00_291E(36, G_h01_46CE);
        F_h00_8A46(G_h01_46CE, 0L, 0L, G_h01_46D2, 0L, 0L, 320L, 200L, 192L, 255L, 0L);
        F_h00_307C();
        G_h01_46D6 = &G_h01_1966;
        F_h00_31AA(&G_h01_1966);
        break;
    case 14:
        F_h00_291E(37, G_h01_46CE);
        F_h00_8A46(G_h01_46CE, 0L, 0L, G_h01_46D2, 0L, 0L, 320L, 200L, 192L, 255L, 0L);
        F_h00_307C();
        G_h01_46D6 = &G_h01_19A6;
        F_h00_31AA(&G_h01_19A6);
        break;
    default:
        F_h00_307C();
        break;
    }
    F_h00_435E();
}
