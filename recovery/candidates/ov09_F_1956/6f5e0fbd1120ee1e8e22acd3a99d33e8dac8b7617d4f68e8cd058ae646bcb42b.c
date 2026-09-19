extern int G_hNN_OFFSET;
extern void F_hNN_OFFSET(int);

int recovered(int p) {
    int result = 0;
    if (*(char*)(p + 2) == 16) {
        result += *(int*)(p + 8);
    } else if (*(char*)(p + 2) == 32) {
        result += *(int*)(p + 8);
        result += *(char*)(p + 6);
    } else if (*(char*)(p + 2) == 19) {
        result += *(int*)(p + 8);
        result += *(char*)(p + 4);
    } else if (*(char*)(p + 2) == 35) {
        result += *(int*)(p + 8);
        result += *(char*)(p + 6);
    } else if (*(char*)(p + 2) == 21) {
        result += *(int*)(p + 8);
        result += *(char*)(p + 4);
    } else if (*(char*)(p + 2) == 33) {
        result += *(int*)(p + 8);
        result += *(char*)(p + 6);
    } else if (*(char*)(p + 2) == 25) {
        result += *(int*)(p + 8);
        result += *(char*)(p + 4);
    } else if (*(char*)(p + 2) == 37) {
        result += *(int*)(p + 8);
        result += *(char*)(p + 6);
    } else if (*(char*)(p + 2) == 29) {
        result += *(int*)(p + 8);
        result += *(char*)(p + 4);
    } else if (*(char*)(p + 2) == 39) {
        result += *(int*)(p + 8);
        result += *(char*)(p + 6);
    } else if (*(char*)(p + 2) == 31) {
        result += *(int*)(p + 8);
        result += *(char*)(p + 4);
    } else if (*(char*)(p + 2) == 41) {
        result += *(int*)(p + 8);
        result += *(char*)(p + 6);
    }
    return result;
}
