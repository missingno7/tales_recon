/* Direct reconstruction candidate for ov11_F_23F4. */
extern int G_h01_9FCC;
extern int G_h01_9FAA;
extern int G_h01_9FAC;
extern int G_h01_9FC0;
extern int G_h01_9FC2;
extern int G_h01_9FC4;
extern int G_h01_9FC6;
extern int G_h01_9FC8;
extern int G_h01_9FCA;
extern int F_h11_4610();

recovered()
{
    if (G_h01_9FCC) {
        G_h01_9FAA = G_h01_9FC0;
        G_h01_9FAC = G_h01_9FC2;
        F_h11_4610(&G_h01_9FAA);
    }
    G_h01_9FC8 = G_h01_9FC4;
    G_h01_9FCA = G_h01_9FC6;
    G_h01_9FC4 = G_h01_9FC0;
    G_h01_9FC6 = G_h01_9FC2;
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

