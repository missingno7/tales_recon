extern long G_h01_5422;
extern long G_h01_5426;
extern char G_h01_53F8;
extern char G_h01_53FA;
extern char G_h01_53FB;
extern char G_h01_53FC;
extern int G_h01_53FE;
extern int G_h01_5400;
extern long G_h01_5402;
extern long G_h01_5406;
extern long G_h01_540A;
extern char G_h01_540E;
extern char G_h01_540F;
extern char G_h01_5410;
extern int G_h01_5412;
extern int G_h01_5414;
extern long G_h01_5416;
extern char *G_h01_541A;
extern long G_h01_541E;
extern long G_h01_5374;
extern long G_h01_5378;

extern int F_h00_897C();
extern int F_h00_3850();
extern int F_h00_8C7E();
extern int F_h00_8C48();
extern int F_h00_8784();
extern int F_h00_8534();

recovered(arg)
long arg;
{
    if (G_h01_5422)
        F_h00_897C(G_h01_5422, 0x3e80);
    if (G_h01_5426)
        F_h00_897C(G_h01_5426, 0x3e80);
    F_h00_3850(0x40f10L);
    if (G_h01_53F8)
        F_h00_8C7E();
    G_h01_53FA = 0;
    G_h01_53FB = 1;
    G_h01_53FC = 1;
    G_h01_53FE = 6;
    G_h01_5400 = 3;
    G_h01_5402 = 0;
    G_h01_5406 = arg;
    G_h01_540A = 0;
    G_h01_540E = 0;
    G_h01_540F = 1;
    G_h01_5410 = 1;
    G_h01_5412 = 6;
    G_h01_5414 = 3;
    G_h01_5416 = 0;
    G_h01_541A = "OK";
    G_h01_541E = 0;
    F_h00_8C48(0, &G_h01_53FA, 0, &G_h01_540E, 0, 0, 0x280, 0x28);
    F_h00_8784(G_h01_5374);
    F_h00_8784(G_h01_5378);
    F_h00_8534(0);
}
