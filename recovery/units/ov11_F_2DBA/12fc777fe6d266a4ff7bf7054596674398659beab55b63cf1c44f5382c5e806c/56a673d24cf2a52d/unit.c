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

/* Direct reconstruction candidate for ov11_F_4610. */
struct Target {
    int x;
    int y;
    char pad[48];
    char state;
};

struct Holder {
    struct Target *target;
    char pad0;
    char state;
    char pad1[6];
    int x;
    int y;
};

struct Motion {
    int x;
    int y;
    char pad[8];
    int remaining;
    int active;
    struct Holder *holder;
};

extern int G_h01_8A3E;
extern int F_h00_34E0();

F_h11_4610(motion)
struct Motion *motion;
{
    struct Holder *holder;
    struct Target *target;

    holder = motion->holder;
    target = holder->target;
    if (motion->remaining > 0) {
        target->x = motion->x + holder->x - G_h01_8A3E;
        target->y = motion->y + holder->y;
        target->state = holder->state;
        F_h00_34E0(target);
        motion->remaining--;
        if (motion->remaining == 0)
            motion->active = 0;
    }
}

