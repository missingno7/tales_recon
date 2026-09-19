struct MotionRecord {
    char pad[10];
    char motion;
    char remainder[29];
};

extern struct MotionRecord G_h01_A464[1];
extern int F_h11_4610();

recovered(n)
int n;
{
    struct MotionRecord *record;

    record = &G_h01_A464[n];
    F_h11_4610(&record->motion);
}
