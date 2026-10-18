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

extern struct Object jg_actor_records[16];
extern struct Controller *G_h01_9F6E;
extern int G_h01_8A3E;
extern int draw_masked_sprite();

recovered(index)
int index;
{
    struct Object *object;

    object = &jg_actor_records[index];
    if (object->active) {
        G_h01_9F6E->x = object->x - G_h01_8A3E;
        G_h01_9F6E->y = object->y;
        G_h01_9F6E->state = 0;
        if (G_h01_9F6E->x > 0)
            if (G_h01_9F6E->y < 154)
                draw_masked_sprite(G_h01_9F6E);
        object->previous_x = object->old_x;
        object->previous_y = object->old_y;
        object->old_x = G_h01_9F6E->x + G_h01_8A3E;
        object->old_y = G_h01_9F6E->y;
    }
}
