struct Child { char pad0[4]; int kind; char pad1[2]; int value; };
struct State { char pad0[34]; struct Child *child; char pad1[6]; int value; char pad2[6]; };
extern struct State G_h01_8BEC[1];
extern int G_h01_94B0;
extern int G_h01_94BE;
extern int G_h01_94C0;
extern int G_h01_37EE;
extern int G_h01_37F0;

recovered(a)
int a;
{
    struct State *p;
    int x, y;
    p = G_h01_8BEC + a;
    x = ((float)G_h01_94BE - (float)p->value) * (float)p->child->value / 45.0;
    y = 0;
    if (p->child->kind == 2)
        if ((8 >> G_h01_94B0) + G_h01_94BE - G_h01_37F0 - p->value > 45) {
            x += 5;
            y = -5;
        }
    G_h01_94C0 += x - G_h01_37EE;
    G_h01_94BE += y - G_h01_37F0;
    G_h01_37EE = x;
    G_h01_37F0 = y;
}
