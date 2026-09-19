extern int G_h01_8B1C;

recovered(a, n) int *a, n; {
    int i, s;
    s = 0;
    for (i = 0; i < n; i++) {
        s += a[i];
    }
    return s;
}
