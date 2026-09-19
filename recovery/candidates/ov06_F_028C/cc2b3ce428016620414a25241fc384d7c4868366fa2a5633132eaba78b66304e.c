/* Decimal counter animation; names describe observed behavior only. */
extern int F_h00_35DC();
extern int F_h00_307C();
extern int F_h00_86A8();

recovered(x1, x2, value1, value2, style, color)
int x1;
int x2;
long value1;
long value2;
char style;
char color;
{
    int origin1;
    int origin2;
    char digits1[11];
    char digits2[11];
    int count1;
    int count2;

    origin1 = x1;
    origin2 = x2;
    digits1[10] = 0;
    digits2[10] = 0;
    count1 = 10;
    count2 = 10;

    do {
        if (value1 > 0L || count1 == 10) {
            digits1[--count1] = (value1 % 10L) + 48;
            x1 = origin1 - ((10 - count1) << 3);
        }
        if (value2 > 0L || count2 == 10) {
            digits2[--count2] = (value2 % 10L) + 48;
            x2 = origin2 - ((10 - count2) << 3);
        }
        F_h00_35DC(x1,191,&digits1[count1],style,color);
        F_h00_35DC(x2,179,&digits2[count2],style,color);
        F_h00_307C();
        F_h00_86A8(10L);
        value1 = value1 / 10L;
        value2 = value2 / 10L;
    } while (value1 > 0L || value2 > 0L);

    F_h00_35DC(x1,191,&digits1[count1],style,color);
    F_h00_35DC(x2,179,&digits2[count2],style,color);
    F_h00_307C();
}
