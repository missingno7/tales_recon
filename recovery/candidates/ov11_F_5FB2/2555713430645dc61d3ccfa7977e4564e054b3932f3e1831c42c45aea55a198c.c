struct Child {
    char pad0[4];
    int kind;
    char pad1[2];
    int value;
};
struct State {
    char pad0[34];
    struct Child *child;
    char pad1[6];
    int value;
    char pad2[6];
};
extern struct State G_h01_8BEC[];
extern int G_h01_94B0;
extern int G_h01_94BE;
extern int G_h01_94C0;
extern int G_h01_37EE;
extern int G_h01_37F0;
extern long F_h00_8D1E();
extern long F_h00_8D0A();
extern long F_h00_8D28();
extern long F_h00_8D14();
extern int F_h00_8D00();
#pragma regcall(F_h00_8D1E(d0))
#pragma regcall(F_h00_8D0A(d0,d1))
#pragma regcall(F_h00_8D28(d0,d1))
#pragma regcall(F_h00_8D14(d1))
#pragma regcall(F_h00_8D00())

recovered(a)
int a;
{
    struct State *p;
    int x,y;

    p=G_h01_8BEC+a;
    F_h00_8D0A(F_h00_8D1E(G_h01_94C0),F_h00_8D1E(p->value));
    F_h00_8D28(F_h00_8D1E(G_h01_94C0),F_h00_8D1E(p->child->value));
    F_h00_8D14(0xd0000047L);
    x=F_h00_8D00();
    y=0;
    if (p->child->kind==2)
        if ((8 >> G_h01_94B0)+G_h01_94BE-G_h01_37F0-p->value>45) {
            x+=5;
            y=-5;
        }
    G_h01_94C0+=x-G_h01_37EE;
    G_h01_94BE+=y-G_h01_37F0;
    G_h01_37EE=x;
    G_h01_37F0=y;
}
