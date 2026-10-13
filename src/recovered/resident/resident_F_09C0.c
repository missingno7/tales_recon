/* Decimal value draw; names describe observed behavior only. */
extern int F_h00_35DC();

recovered(x, y, value, style, color, flag)
int x;
int y;
long value;
char style;
char color;
int flag;
{
    char digits[11];
    int count;

    digits[10] = 0;
    count = 10;
    do {
        digits[--count] = (value % 10L) + 48;
    } while ((value = value / 10L) > 0L);
    if (flag) {
        x -= (10 - count) << 3;
    }
    F_h00_35DC(x, y, &digits[count], style, color);
}
