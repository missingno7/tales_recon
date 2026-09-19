extern int G_hNN_OFFSET;
extern void F_hNN_OFFSET();

int recovered(a, b) int a, b; {
    int result = 0;
    if (a) {
        result = (a >> 2) + (b & 15);
        F_hNN_OFFSET();
    }
    if (b) {
        result = (b >> 2) + (a & 15);
        F_hNN_OFFSET();
    }
    return result;
}