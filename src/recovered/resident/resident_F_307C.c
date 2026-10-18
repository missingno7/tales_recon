extern unsigned char screen_bitmap_index;
extern long screen_bitmap_pair;
extern long G_h01_53E0;
extern long G_h01_53A6;
extern long G_h01_53B4;
extern long G_h01_53A2;
extern long screen_rast_port;
extern long active_screen_bitmap;
extern int WaitBOVP();
extern int LoadView();

recovered()
{
    G_h01_53A6 = ((long *)&G_h01_53E0)[screen_bitmap_index];
    screen_bitmap_index ^= 1;
    ((long *)screen_rast_port)[1] = ((long *)&screen_bitmap_pair)[screen_bitmap_index];
    active_screen_bitmap = ((long *)&screen_bitmap_pair)[screen_bitmap_index];
    WaitBOVP(&G_h01_53B4);
    LoadView(&G_h01_53A2);
}
