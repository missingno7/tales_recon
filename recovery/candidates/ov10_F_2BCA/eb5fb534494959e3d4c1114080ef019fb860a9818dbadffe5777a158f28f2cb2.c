extern int G_hNN_OFFSET;

void F_hNN_OFFSET(int);

int recovered(int a, int b) {
    int result1 = 0;
    int result2 = 0;

    if (a) {
        result1 = (a >> 2) + (b & 15);
        F_hNN_OFFSET(result1);
    }

    if (b) {
        result2 = (b >> 2) + (a & 15);
        F_hNN_OFFSET(result2);
    }

    return result1 + result2;
}