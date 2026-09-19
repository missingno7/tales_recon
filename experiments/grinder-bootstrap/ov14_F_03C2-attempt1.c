extern char G_h01_452E[432];
recovered(a)
char a;
{
    int i;
    for (i=1; i<35; ++i) {
        if (i != a && G_h01_452E[i*12] == 0 && G_h01_452E[i*12+1] == 0) break;
    }
    return i;
}
