/* Direct reconstruction candidate for ov11_F_49EA. */
struct Controller { int x; int y; char pad[48]; char state; };
extern long screen_rast_port;
extern long G_h01_46CE;
extern long G_h01_46D2;
extern struct Controller *G_h01_9F5A;
extern long G_h01_A460;
extern int G_h01_A45E;
extern int G_h01_8A3E;
extern int SetRast();
extern int BltBitMap();
extern int F_h00_34E0();
extern long F_h00_3B16();

recovered()
{
    SetRast(screen_rast_port, 0L);
    BltBitMap(G_h01_46CE, 0L, 0L, G_h01_46D2,
        0L, 0L, 320L, 176L, 192L, 255L, 0L);
    G_h01_9F5A->x = 48;
    G_h01_9F5A->y = 0;
    G_h01_9F5A->state = 1;
    F_h00_34E0(G_h01_9F5A);
    G_h01_A460 = F_h00_3B16(128, 176);
    BltBitMap(G_h01_46D2, 56L, 0L, G_h01_A460,
        0L, 0L, 104L, 176L, 192L, 255L, 0L);
    G_h01_A45E = 0;
    G_h01_8A3E = 0;
}
