extern int G_h01_B1E8;
extern char *G_h01_3AB4;
extern long G_h01_46DA;
extern char G_h01_A9CA[1024];
extern long F_h00_86F6();
extern int F_h00_3674();

char
F_h00_411E()
{
    long amount;

    if (++G_h01_B1E8 >= 1024) {
        amount = F_h00_86F6(G_h01_46DA, G_h01_A9CA, 1024L);
        if (amount <= 0)
            F_h00_3674(8000);
        G_h01_B1E8 = 0;
        G_h01_3AB4 = G_h01_A9CA;
    } else
        ++G_h01_3AB4;
    return *G_h01_3AB4;
}
