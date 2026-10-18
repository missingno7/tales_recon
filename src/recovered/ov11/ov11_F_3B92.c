struct Event {
    char pad0[2];
    int value2;
    int value4;
    int kind;
    int value8;
    int value10;
    int value12;
    int value14;
    int value16;
    char pad12[2];
    int work14;
    int work16;
    int work18;
    int work1a;
    int count1c;
    int value1e;
};
struct Sprite { int x,y; char pad4[48]; char value34; };
extern int jg_get_actor_world_position();
extern int point_inside_rectangle();
extern int jg_set_event_draw_state();
extern void draw_masked_sprite();
extern struct Event jg_event_records[1];
extern struct Sprite *G_h01_9F66;
extern struct Sprite *G_h01_9F8A;
extern int G_h01_7A92;
extern int G_h01_8A3E;
extern int G_h01_A152;
extern int G_h01_A154;
extern int G_h01_A158;

recovered()
{
    int quotient;
    int base;
    int i;
    int x;
    int y;
    struct Event *event;
    int screen_x;
    int screen_y;

    quotient = G_h01_8A3E / 128;
    base = (G_h01_A158 + quotient) % G_h01_A152;
    for (i = 0; i < 4; ++i) {
        event = &jg_event_records[(base + i) % G_h01_A152];
        if (event->value4 == 1) {
            screen_x = (quotient + i - 1) * 128 + G_h01_A154;
            screen_y = event->value2;
            if (G_h01_7A92 && jg_get_actor_world_position(G_h01_7A92, &x, &y) &&
                point_inside_rectangle(screen_x, screen_y - event->value10, x, y,
                            event->value8 + screen_x, event->value10 + screen_y))
                jg_set_event_draw_state((base + i) % G_h01_A152, 7);
        if (event->count1c > 0 && event->value12 < event->value14) {
            switch (event->kind) {
            case 18:
                G_h01_9F66->value34 = ((unsigned char *)&event->value12)[1] + 0;
                G_h01_9F66->x = screen_x - G_h01_8A3E;
                G_h01_9F66->y = screen_y;
                if (G_h01_9F66->x < 320)
                    draw_masked_sprite(G_h01_9F66);
                break;
            case 17:
                G_h01_9F8A->value34 = ((unsigned char *)&event->value12)[1] + 0;
                G_h01_9F8A->x = screen_x - G_h01_8A3E;
                G_h01_9F8A->y = screen_y;
                if (G_h01_9F8A->x < 320)
                    draw_masked_sprite(G_h01_9F8A);
                break;
            }
            --event->count1c;
            if (event->count1c == 0)
                event->value1e = 0;
        }
        event->work16 = event->work14;
        event->work1a = event->work18;
        event->work14 = screen_x;
        event->work18 = screen_y;
        }
    }
}