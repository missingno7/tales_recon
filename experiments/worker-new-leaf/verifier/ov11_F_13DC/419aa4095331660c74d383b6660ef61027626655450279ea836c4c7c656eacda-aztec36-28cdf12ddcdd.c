extern long G_h01_94CE;
extern long G_h01_9F4E;
extern long G_h01_9F56;
extern long G_h01_9F52;
extern long G_h01_9F8E;
extern int G_h01_9FB6;
extern int G_h01_9FCA;
extern int G_h01_9FC8;
extern int F_h11_4696();
extern int F_h11_583A();

recovered(slot)
int slot;
{
    if (slot == 12) {
        G_h01_9FB6 = 2;
        if (G_h01_94CE == G_h01_9F4E || G_h01_94CE == G_h01_9F56) {
            F_h11_4696(G_h01_9FC8, G_h01_9FCA, 40, 33, 22);
            F_h11_583A(G_h01_9FC8, G_h01_9FCA, 40, 33, 10);
        } else if (G_h01_94CE == G_h01_9F52) {
            F_h11_4696(G_h01_9FC8, G_h01_9FCA, 48, 41, 22);
            F_h11_583A(G_h01_9FC8, G_h01_9FCA, 48, 41, 10);
        } else if (G_h01_94CE == G_h01_9F8E) {
            F_h11_4696(G_h01_9FC8, G_h01_9FCA, 88, 34, 22);
            F_h11_583A(G_h01_9FC8, G_h01_9FCA, 88, 34, 10);
        }
    }
}
