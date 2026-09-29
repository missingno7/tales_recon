struct InitRecord { char prefix[0x2c]; int value2c; int value2e; int value30; int value32; };
extern struct InitRecord G_h01_8BEC[1];
extern int G_h01_94B4;
extern int G_h01_94D6;
extern int G_h01_37EE;
extern int G_h01_37F0;
extern int F_h11_5C42();
extern int F_h11_41F6();

recovered(index)
int index;
{
    struct InitRecord *record;

    record=&G_h01_8BEC[index];
    record->value30=1;
    G_h01_94B4=0;
    G_h01_94D6=0;
    G_h01_37F0=0;
    G_h01_37EE=0;
    F_h11_5C42(index,3);
    F_h11_41F6(24,&record->prefix[0x12],1,record->value2c,record->value2e);
}
