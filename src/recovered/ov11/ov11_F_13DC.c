extern int G_h01_94C2;
extern int G_h01_94C4;
struct Object;
extern struct Object *G_h01_94CE;
extern struct Object *G_h01_9F4E;
extern struct Object *G_h01_9F52;
extern struct Object *G_h01_9F56;
extern struct Object *G_h01_9F8E;
extern int jg_queue_background_restore_rectangle();
extern int jg_set_grid_states_in_rectangle();

recovered()
{
    if (G_h01_94CE == G_h01_9F4E ||
        G_h01_94CE == G_h01_9F56) {
        jg_queue_background_restore_rectangle(G_h01_94C2, G_h01_94C4, 0x28, 0x21, 0x16);
        jg_set_grid_states_in_rectangle(G_h01_94C2, G_h01_94C4, 0x28, 0x21, 0x0a);
    } else if (G_h01_94CE == G_h01_9F52) {
        jg_queue_background_restore_rectangle(G_h01_94C2, G_h01_94C4, 0x30, 0x29, 0x16);
        jg_set_grid_states_in_rectangle(G_h01_94C2, G_h01_94C4, 0x30, 0x29, 0x0a);
    } else if (G_h01_94CE == G_h01_9F8E) {
        jg_queue_background_restore_rectangle(G_h01_94C2, G_h01_94C4, 0x58, 0x22, 0x16);
        jg_set_grid_states_in_rectangle(G_h01_94C2, G_h01_94C4, 0x58, 0x22, 0x0a);
    }
}
