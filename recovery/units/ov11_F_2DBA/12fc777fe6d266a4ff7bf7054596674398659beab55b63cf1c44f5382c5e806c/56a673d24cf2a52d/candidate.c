struct MotionRecord {
    char pad0[2];
    char motion[28];
    short v30;
    short v32;
    short pad34;
    short v36;
    short v38;
    short v40;
    short v42;
    short state;
    char remainder[18];
};

extern struct MotionRecord G_h01_9FCE[1];
extern int F_h11_4610();

recovered(n)
int n;
{
    struct MotionRecord *record;

    record = &G_h01_9FCE[n];
    if (record->state != 14)
        F_h11_4610(record->motion);
    record->v38 = record->v36;
    record->v42 = record->v40;
    record->v40 = record->v32;
    record->v36 = record->v30;
}
