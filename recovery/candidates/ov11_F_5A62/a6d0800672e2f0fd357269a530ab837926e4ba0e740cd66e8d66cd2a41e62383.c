extern int G_h01_3844[40];

recovered(flag, index)
int flag, index;
{
    int i;

    if (flag) {
        for (i = 0; i < 40; i++)
            G_h01_3844[i] = i * 53 - 2;
    }
    return G_h01_3844[index];
}
