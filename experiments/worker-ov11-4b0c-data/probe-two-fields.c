/* Isolated field-offset probe; no recovered object content or ownership claimed. */
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
extern struct Descriptor *G_h01_94E8;
extern struct Descriptor G_h01_94EC[110];
recovered()
{
    G_h01_94E8 = &G_h01_94EC[10];
    G_h01_94DE = G_h01_94E8->field_05;
    G_h01_94E0 = G_h01_94E8->field_06;
    G_h01_94E2 = G_h01_94E8->field_0c;
    G_h01_94E4 = G_h01_94E8->field_0e;
}
