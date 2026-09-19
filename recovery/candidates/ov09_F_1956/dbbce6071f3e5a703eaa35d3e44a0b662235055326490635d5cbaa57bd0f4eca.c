extern int G_hNN_OFFSET;

void F_hNN_OFFSET(int p) {
    if (*(char*)(p + 2) == 16) {
        *(int*)(p + 8) = 1;
        *(int*)(p + 4) = 4;
    } else if (*(char*)(p + 2) == 32) {
        *(int*)(p + 8) = 1;
        *(int*)(p + 6) = 4;
    } else if (*(char*)(p + 2) == 19) {
        *(int*)(p + 8) = 1;
        *(int*)(p + 4) = 3;
    } else if (*(char*)(p + 2) == 35) {
        *(int*)(p + 8) = 1;
        *(int*)(p + 6) = 4;
    } else if (*(char*)(p + 2) == 21) {
        *(int*)(p + 8) = 1;
        *(int*)(p + 4) = 3;
    } else if (*(char*)(p + 2) == 33) {
        *(int*)(p + 8) = 1;
        *(int*)(p + 6) = 4;
    } else if (*(char*)(p + 2) == 25) {
        *(int*)(p + 8) = 1;
        *(int*)(p + 4) = 3;
    } else if (*(char*)(p + 2) == 37) {
        *(int*)(p + 8) = 1;
        *(int*)(p + 6) = 4;
    } else if (*(char*)(p + 2) == 29) {
        *(int*)(p + 8) = 1;
        *(int*)(p + 4) = 3;
    } else if (*(char*)(p + 2) == 39) {
        *(int*)(p + 8) = 1;
        *(int*)(p + 6) = 4;
    } else if (*(char*)(p + 2) == 31) {
        *(int*)(p + 8) = 1;
        *(int*)(p + 4) = 3;
    } else if (*(char*)(p + 2) == 41) {
        *(int*)(p + 8) = 1;
        *(int*)(p + 6) = 4;
    }
}
