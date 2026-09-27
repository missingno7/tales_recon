/* Isolated ABI/layout probe only; these are mechanical hunk-offset aliases. */
struct Descriptor {
    long object;
    char unknown_04;
    char field_05;
    int field_06;
    char unknown_08[4];
    int field_0c;
    int field_0e;
};
extern int G_h01_94DE;
extern int G_h01_94E0;
extern int G_h01_94E2;
extern int G_h01_94E4;
extern int G_h01_94E6;
extern struct Descriptor *G_h01_94E8;
extern struct Descriptor G_h01_94EC[110];
recovered()
{
    G_h01_94DE = 0;
    G_h01_94E0 = 5;
    G_h01_94E8 = &G_h01_94EC[10];
}
