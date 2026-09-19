/* Direct reconstruction candidate for ov11_F_36F8. */
struct Object {
    char pad0[46];
    int active;
    int pad1;
    int x;
    int y;
    int old_x;
    int previous_x;
    int old_y;
    int previous_y;
    char pad2[2];
};

struct Controller {
    int x;
    int y;
    char pad[48];
    char state;
};

extern struct Object G_h01_9FCE[16];
extern struct Controller *G_h01_9F6E;
extern int G_h01_8A3E;
extern int F_h00_34E0();

recovered(index)
int index;
{
    struct Object *object;

    object = &G_h01_9FCE[index];
    if (object->active) {
        G_h01_9F6E->x = object->x - G_h01_8A3E;
        G_h01_9F6E->y = object->y;
        G_h01_9F6E->state = 0;
        if (G_h01_9F6E->x > 0)
            if (G_h01_9F6E->y < 154)
                F_h00_34E0(G_h01_9F6E);
        object->previous_x = object->old_x;
        object->previous_y = object->old_y;
        object->old_x = G_h01_9F6E->x + G_h01_8A3E;
        object->old_y = G_h01_9F6E->y;
    }
}
