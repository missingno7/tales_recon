extern int G_h01_9FB6;
extern int G_h01_9FC8;
extern int G_h01_9FCA;
extern int jg_queue_background_restore_rectangle();
extern int jg_set_entity_region_state();

recovered(a)
int a;
{
    G_h01_9FB6 = 2;
    if (a == 12)
        jg_queue_background_restore_rectangle(G_h01_9FC8, G_h01_9FCA, 40, 32, 33);
    jg_set_entity_region_state(12, G_h01_9FC8, G_h01_9FCA, 40, 32);
}
