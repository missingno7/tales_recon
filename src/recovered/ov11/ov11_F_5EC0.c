struct InitRecord { char prefix[0x2c]; int value2c; int value2e; int value30; int value32; };
extern struct InitRecord jg_platform_records[1];
extern int G_h01_94B4;
extern int G_h01_94D6;
extern int G_h01_37EE;
extern int G_h01_37F0;
extern int jg_set_platform_render_state();
extern int jg_start_animation_sequence();

recovered(index)
int index;
{
    struct InitRecord *record;

    record=&jg_platform_records[index];
    record->value30=1;
    G_h01_94B4=0;
    G_h01_94D6=0;
    G_h01_37F0=0;
    G_h01_37EE=0;
    jg_set_platform_render_state(index,3);
    jg_start_animation_sequence(24,&record->prefix[0x12],1,record->value2c,record->value2e);
}
