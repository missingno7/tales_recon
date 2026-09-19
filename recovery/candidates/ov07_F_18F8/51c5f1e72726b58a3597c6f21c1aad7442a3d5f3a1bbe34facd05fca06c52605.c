struct Input {
    char pad[2];
    long text;
};

extern struct Input *G_h01_0012;
extern long F_h00_0976();
extern int F_h00_35DC();

recovered(unused, mode, x, y)
int unused;
int mode;
int x;
int y;
{
    int i;
    int limit;
    long unused_local;
    char data[60];
    long text;

    for (i = 0; i < 60; i++)
        data[i] = 0;
    text = G_h01_0012->text;
    text = F_h00_0976(text, data);
    text = F_h00_0976(text, data);
    if (mode == 1)
        limit = 6;
    else if (mode == 2) {
        for (i = 0; i < 6; i++)
            text = F_h00_0976(text, data);
        limit = 2;
    } else if (mode == 3) {
        for (i = 0; i < 8; i++)
            text = F_h00_0976(text, data);
        limit = 2;
    }
    for (i = 0; i < limit; i++) {
        text = F_h00_0976(text, data);
        F_h00_35DC(x, y, data, 1, 0);
        y += 10;
    }
}
