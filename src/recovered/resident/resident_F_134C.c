extern int F_h00_435E();
extern int F_h00_4376();
extern int F_h00_86A8();

recovered(n)
int n;
{
    unsigned char c;
    int i, result;

    result = 0;
    F_h00_435E();
    for (i = 0; i < n; i++) {
        c = F_h00_4376();
        if (c & 0x80) {
            result = 1;
            break;
        }
        F_h00_86A8(5L);
    }
    return result;
}
