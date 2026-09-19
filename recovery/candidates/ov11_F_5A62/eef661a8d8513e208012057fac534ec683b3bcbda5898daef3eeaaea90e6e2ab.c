extern int G_h01_3844[40];

recovered(flag, index)
int flag, index;
{
    int i;

    if (flag) {
        i = 0;
        do {
            G_h01_3844[i] = i * 53 - 2;
            i++;
        } while (i < 40);
    }
    return G_h01_3844[index];
}
