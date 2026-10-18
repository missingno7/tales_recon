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
extern int jg_advance_scheduled_sprite_motion();

recovered()
{
    if (G_h01_9FCC) {
        G_h01_9FAA = G_h01_9FC0;
        G_h01_9FAC = G_h01_9FC2;
        jg_advance_scheduled_sprite_motion(&G_h01_9FAA);
    }
    G_h01_9FC8 = G_h01_9FC4;
    G_h01_9FCA = G_h01_9FC6;
    G_h01_9FC4 = G_h01_9FC0;
    G_h01_9FC6 = G_h01_9FC2;
}