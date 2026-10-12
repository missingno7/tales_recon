extern int G_h01_34E0;
extern int G_h01_34DC[16];
extern int G_h01_6F32;
extern long G_h01_46CE;
extern long G_h01_46D2;
extern int F_h00_8A46();
extern int F_h08_1B2A();
extern int F_h08_354E();

recovered(P)
int P;
{
    int x;

    if (G_h01_34DC[G_h01_34E0] == 5 || G_h01_34DC[G_h01_34E0] == 6 || G_h01_6F32 > 0) {
        F_h00_8A46(G_h01_46CE, 0L, 0L, G_h01_46D2, 0L, 0L, 320L, 168L, 192L, 255L, 0L);
        G_h01_6F32--;
    } else {
        F_h08_1B2A();
        F_h08_354E(P);
    }
}
