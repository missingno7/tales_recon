struct ClusterRecord { char pad0[8]; int value8; int value10; char pad12[2]; int value14; int value16; char pad18[12]; int state30; int value32; char pad34[6]; int state40; int value42; int value2c; int value2e; char tail[4]; };
extern struct ClusterRecord G_h01_8BEC[1];
extern int G_h01_94B4;
extern int G_h01_94D6;
extern int G_h01_37EE;
extern int G_h01_37F0;
extern int F_h11_5C42();
extern int F_h11_41F6();

recovered(index)
int index;
{
    struct ClusterRecord *record;

    record=&G_h01_8BEC[index];
    record->state30=1;
    G_h01_94B4=0;
    G_h01_94D6=0;
    G_h01_37F0=0;
    G_h01_37EE=0;
    F_h11_5C42(index,3);
    F_h11_41F6(24,record->pad18,1,record->value2c,record->value2e);
}
