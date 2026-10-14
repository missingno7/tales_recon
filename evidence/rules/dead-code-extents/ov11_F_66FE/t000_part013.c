extern int G_h01_8A3E;
extern int G_h01_94AE;
extern int G_h01_94B0;
extern int G_h01_94B6;
extern int G_h01_94B8;
extern int G_h01_94BE;
extern int G_h01_94C0;
extern int G_h01_94D4;
extern int G_h01_9F4C;
extern int G_h01_9FAA;
extern int G_h01_9FC0;
extern int G_h01_9FC2;
extern int G_h01_9FC4;
extern int G_h01_9FC6;
extern int G_h01_9FC8;
extern int G_h01_9FCA;
extern int G_h01_9FCC;
extern int F_h11_262E();

extern int F_h11_407C();
extern int F_h11_41F6();
extern int F_h11_4474();
extern int F_h11_4B0C();

F_h11_2272()
{
    int x;
    int y;

    switch (G_h01_9FCC) {
    case 0:
        if (G_h01_94B8 > G_h01_9F4C) {
            G_h01_9FCC = 1;
            G_h01_9FC0 = G_h01_8A3E + 318;
            G_h01_9FC2 = G_h01_94C0 + 12;
            G_h01_9FC4 = G_h01_9FC0;
            G_h01_9FC6 = G_h01_9FC2;
            G_h01_9FC8 = G_h01_9FC4;
            G_h01_9FCA = G_h01_9FC6;
            F_h11_2430(12);
            F_h11_41F6(33, &G_h01_9FAA, G_h01_9FCC,
                G_h01_9FC0, G_h01_9FC2);
        }
        break;

    case 1:
        x = (8 >> G_h01_94B0) + G_h01_94BE;
        y = G_h01_94C0 + 16;
        switch (G_h01_94AE) {
        case 19:
            y += 8;
            break;
        case 6:
            x += 16;
            y += 8;
            break;
        }

        if (F_h11_262E(x - 4, y - 6, x + 4, y + 6,
                G_h01_9FC0 + 8, G_h01_9FC2 + 8,
                G_h01_9FC0 + 18, G_h01_9FC2 + 20) &&
            G_h01_94AE != 2 && G_h01_94AE != 45) {
            if (G_h01_94B6) {
                F_h11_407C(G_h01_94D4);
                G_h01_94B6 = 0;
            }
            G_h01_94AE = 2;
            F_h11_4B0C(2);
        }

        if (G_h01_9FC0 + 32 < G_h01_8A3E) {
            G_h01_9FCC = 0;
            G_h01_94B8 = 0;
        } else {
            G_h01_9FC0 -= 4;
            F_h11_4474(33, &G_h01_9FAA);
        }
        F_h11_2430(12);
        break;
    }
}


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
extern int F_h11_4610();

F_h11_23F4()
{
    if (G_h01_9FCC) {
        G_h01_9FAA = G_h01_9FC0;
        G_h01_9FAC = G_h01_9FC2;
        F_h11_4610(&G_h01_9FAA);
    }
    G_h01_9FC8 = G_h01_9FC4;
    G_h01_9FCA = G_h01_9FC6;
    G_h01_9FC4 = G_h01_9FC0;
    G_h01_9FC6 = G_h01_9FC2;
}
extern int G_h01_9FB6;
extern int G_h01_9FC8;
extern int G_h01_9FCA;
extern int F_h11_4696();


F_h11_2430(a)
int a;
{
    G_h01_9FB6 = 2;
    if (a == 12)
        F_h11_4696(G_h01_9FC8, G_h01_9FCA, 40, 32, 33);
    F_h11_247C(12, G_h01_9FC8, G_h01_9FCA, 40, 32);
}

struct Record { int ignored; int value1; int value2; int value3; int value4; int value5; int value6; };
extern struct Record G_h01_8A66[1];
extern int F_h11_5C42();
extern int F_h11_54F8();
extern int F_h11_2E26();
extern int F_h11_66FE();
extern int F_h11_717A();

F_h11_247C(a,b,c)
int a,c;
long b;
{
    struct Record *p,*last;

    if (((int *)&b)[0]<0) ((int *)&b)[0]=0;
    p=&G_h01_8A66[((int *)&b)[0]/104];
    last=&G_h01_8A66[(((int *)&b)[0]+c)/104];
    for (;p<=last;p++) {
        if (p->ignored) F_h11_5C42(p->ignored,a);
        if (p->value1) F_h11_54F8(p->value1,a);
        if (p->value5) F_h11_2E26(p->value5,a);
        if (p->value4) F_h11_66FE(p->value4,a);
        if (p->value6) F_h11_717A(p->value6,a);
    }
}
