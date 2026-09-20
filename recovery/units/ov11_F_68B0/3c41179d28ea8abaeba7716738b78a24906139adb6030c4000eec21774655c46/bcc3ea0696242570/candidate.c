struct Display {
    long value0;
    int value4;
    int value6;
    char padding[8];
};

struct Record {
    int input0;
    int input2;
    char padding0[28];
    int value20;
    int value22;
    int value24;
    int value26;
};

extern char G_h01_9EAC[1];
extern int G_h01_9EB0;
extern int G_h01_9EC0;
extern int G_h01_9EC2;
extern int G_h01_9ED0;
extern int G_h01_9ED2;
extern int G_h01_9EE0;
extern int G_h01_9EE2;
extern int G_h01_9EF0;
extern int G_h01_9EF2;
extern int G_h01_9F00;
extern int G_h01_9F02;
extern long G_h01_9F7E;
extern struct Record G_h01_A464[6];
extern int F_h11_41F6();

recovered()
{
    struct Record *record;
    int i;

    i = 0;
    do {
        ((struct Display *)G_h01_9EAC)[i].value0 = G_h01_9F7E;
        ++i;
    } while (i < 6);

    G_h01_9EB0 = 0;
    G_h01_9EC0 = 1;
    G_h01_9EC2 = 1;
    G_h01_9ED0 = 2;
    G_h01_9ED2 = 1;
    G_h01_9EE0 = 3;
    G_h01_9EE2 = 4;
    G_h01_9EF0 = 2;
    G_h01_9EF2 = 1;
    G_h01_9F00 = 1;
    G_h01_9F02 = 1;

    i = 1;
    do {
        record = &G_h01_A464[i];
        record->value22 = record->input0 * 53;
        record->value24 = record->input2 * 32 + 33;
        record->value20 = 20;
        record->value26 = 20;
        F_h11_41F6(8, (char *)record + 10, 20,
                    record->value22, record->value24);
        ++i;
    } while (i < 6);
}
