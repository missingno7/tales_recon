struct MotionRecord {
    char pad[18];
    char motion;
    char remainder[33];
};

extern struct MotionRecord G_h01_8BEC[1];
extern int F_h11_4610();

F_h11_5C1A(n)
int n;
{
    struct MotionRecord *record;

    record = &G_h01_8BEC[n];
    F_h11_4610(&record->motion);
}
