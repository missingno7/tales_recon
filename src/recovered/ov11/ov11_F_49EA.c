/* Direct reconstruction candidate for ov11_F_49EA. */
struct Controller { int x; int y; char pad[48]; char state; };
extern long screen_rast_port;
extern long archive_image_bitmap;
extern long active_screen_bitmap;
extern struct Controller *G_h01_9F5A;
extern long G_h01_A460;
extern int G_h01_A45E;
extern int G_h01_8A3E;
extern int SetRast();
extern int BltBitMap();
extern int draw_masked_sprite();
extern long allocate_bitmap();

recovered()
{
    SetRast(screen_rast_port, 0L);
    BltBitMap(archive_image_bitmap, 0L, 0L, active_screen_bitmap,
        0L, 0L, 320L, 176L, 192L, 255L, 0L);
    G_h01_9F5A->x = 48;
    G_h01_9F5A->y = 0;
    G_h01_9F5A->state = 1;
    draw_masked_sprite(G_h01_9F5A);
    G_h01_A460 = allocate_bitmap(128, 176);
    BltBitMap(active_screen_bitmap, 56L, 0L, G_h01_A460,
        0L, 0L, 104L, 176L, 192L, 255L, 0L);
    G_h01_A45E = 0;
    G_h01_8A3E = 0;
}
