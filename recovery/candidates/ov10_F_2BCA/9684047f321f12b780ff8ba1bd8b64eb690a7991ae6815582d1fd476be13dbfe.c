extern int G_h2BCA_OFFSET;
extern void F_h2BCA_OFFSET();

int recovered(a, b) int a, b; {
    int result = 0;
    if (a) {
        result = (a >> 3) - (b >> 3);
        F_h2BCA_OFFSET();
    }
    if (b) {
        result = (b >> 3) - (a >> 3);
        F_h2BCA_OFFSET();
    }
    return result;
}