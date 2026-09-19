extern char G_h01_6F48[594];
extern char G_h01_6F4A[594];
extern char G_h01_6F50[594];
extern int F_h00_3AE4();

recovered()
{
    int i;

    i = 1;
    do {
        F_h00_3AE4(G_h01_6F50 + i * 54,
                    *(int *)(G_h01_6F48 + i * 54),
                    *(int *)(G_h01_6F4A + i * 54));
        ++i;
    } while (i < 11);
}
