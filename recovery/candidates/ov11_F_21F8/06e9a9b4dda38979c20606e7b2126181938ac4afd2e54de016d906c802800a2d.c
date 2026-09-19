struct LongSlot { long value; long pad[3]; };

extern struct LongSlot G_h01_9F0C[4];
extern long G_h01_9F9E;
extern int G_h01_9F10;
extern int G_h01_9F20;
extern int G_h01_9F30;
extern int G_h01_9F40;
extern int G_h01_9F4C;
extern int G_h01_9FC0;
extern int G_h01_9FC2;
extern int G_h01_9FCC;
extern char G_h01_46E0;

recovered()
{
    int i;

    for (i = 0; i < 4; i++)
        G_h01_9F0C[i].value = G_h01_9F9E;
    G_h01_9F10 = 0;
    G_h01_9F20 = 1;
    G_h01_9F30 = 2;
    G_h01_9F40 = 1;
    G_h01_9FCC = 0;
    G_h01_9FC0 = 0;
    G_h01_9FC2 = 0;
    switch (G_h01_46E0) {
    case 0: G_h01_9F4C = 350; break;
    case 1: G_h01_9F4C = 200; break;
    case 2: G_h01_9F4C = 100; break;
    }
}
