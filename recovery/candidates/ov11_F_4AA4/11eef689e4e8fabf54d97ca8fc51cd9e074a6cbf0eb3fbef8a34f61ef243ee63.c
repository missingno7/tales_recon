struct Destination { char pad[52]; char value; };
struct Source {
    struct Destination *destination;
    char pad0;
    char value;
    int delay;
    char pad1[4];
    int x;
    int y;
};

extern int G_h01_94BE;
extern int G_h01_94C0;
extern struct Destination *G_h01_94DA;
extern int G_h01_94DE;
extern int G_h01_94E0;
extern int G_h01_94E4;
extern struct Source *G_h01_94E8;

recovered()
{
    if (G_h01_94E4 > 0) {
        G_h01_94E4--;
        return;
    }
    G_h01_94DE++;
    if (G_h01_94DE >= G_h01_94E0)
        return;
    if (G_h01_94E8 == 0)
        return;
    G_h01_94E8++;
    G_h01_94BE += G_h01_94E8->x;
    G_h01_94C0 += G_h01_94E8->y;
    G_h01_94DA = G_h01_94E8->destination;
    G_h01_94DA->value = G_h01_94E8->value;
    G_h01_94E4 = G_h01_94E8->delay;
}
