extern int G_h01_3844[40];

recovered(flag, index)
int flag, index;
{
    int i;

    if (flag) {
        i = 0;
        while (i < 40) {
            G_h01_3844[i] = i * 53 - 2;
            i++;
        }
        if (i >= 40)
            goto done;
    }
done:
    return G_h01_3844[index];
}
