/* Direct reconstruction candidate for ov11_F_6C3A. */
struct Record {
    char pad0[4];
    int first;
    int first_old;
    int second;
    int second_old;
    int x;
    int y;
    int x2;
    int y2;
    char pad1[9];
    char state;
    char pad2[2];
};
extern struct Record G_h01_A554[16];
extern char *G_h01_5370;
extern long G_h01_46CA;
extern int G_h01_8A3E;
extern int F_h00_8B88();
extern int F_h00_8B4C();
extern int F_h00_8AA8();

recovered(index)
int index;
{
    struct Record *record;

    record = &G_h01_A554[index];
    *G_h01_5370 = record->state;
    F_h00_8B88(G_h01_46CA, (long)*G_h01_5370);
    F_h00_8B4C(G_h01_46CA, (long)(record->x - G_h01_8A3E), (long)record->y);
    F_h00_8AA8(G_h01_46CA, (long)(record->x2 - G_h01_8A3E), (long)record->y2);
    record->first_old = record->first;
    record->first = record->x2;
    record->second_old = record->second;
    record->second = record->y2;
}
