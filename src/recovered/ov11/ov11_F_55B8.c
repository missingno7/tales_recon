struct GridRecord {
    char prefix[8];
    int code;
    int state;
    char pad12[0x1c];
    int duration;
    int counter;
    int vertical;
    int horizontal;
    char tail[4];
};

extern int G_h01_37F2;
extern int G_h01_8A3E;
extern int G_h01_8A3C;
extern int jg_grid_tile_indices[41][4];
extern int jg_platform_records[1];
extern int jg_tile_reward_available_flags[1];
extern int *G_h01_9F5E;
extern int *G_h01_9FA2;
extern int jg_set_platform_record_state();
extern int draw_masked_sprite();

recovered()
{
    int row,column,base,tile,vertical,horizontal;
    struct GridRecord *object;

    if (G_h01_37F2) {
        G_h01_37F2=0;
        for (row=0;row<24;row++) {
            vertical=row*53+(!((row&1)^1)?-4:-24);
            for (column=2;column>=0;column--) {
                tile=jg_grid_tile_indices[row][column];
                if (tile) {
                    object=(struct GridRecord *)((char *)jg_platform_records+((long)tile*52));
                    if (!object->code) {
                        horizontal=column*32+48;
                        object->vertical=vertical;
                        object->horizontal=horizontal;
                    }
                }
            }
        }
    }
    base=(G_h01_8A3E-12)/53;
    base=(base<0)?0:base;
    for (row=6;row>=0;row--) {
        for (column=2;column>=0;column--) {
            tile=jg_grid_tile_indices[base+row][column];
            if (tile) {
                object=(struct GridRecord *)((char *)jg_platform_records+((long)tile*52));
                if (G_h01_8A3C) jg_set_platform_record_state(tile,2);
                if (object->duration>0 && !object->code) {
                    G_h01_9F5E[0]=object->vertical-G_h01_8A3E;
                    G_h01_9F5E[1]=object->horizontal;
                    *((char *)G_h01_9F5E+0x34)=object->prefix[7];
                    draw_masked_sprite(G_h01_9F5E);
                    object->duration--;
                    if (!object->duration) object->counter=0;
                }
            }
        }
    }
    for (row=6;row>=0;row--) {
        vertical=(row+base)*53-G_h01_8A3E;
        for (column=2;column>=0;column--) {
            tile=jg_grid_tile_indices[base+row][column];
            if (tile) {
                object=(struct GridRecord *)((char *)jg_platform_records+((long)tile*52));
                if (object->duration>0) {
                    horizontal=column*32+48;
                    if (jg_tile_reward_available_flags[tile]>0 && !object->state) {
                        G_h01_9FA2[0]=vertical+16;
                        G_h01_9FA2[1]=horizontal-13;
                        draw_masked_sprite(G_h01_9FA2);
                    }
                }
            }
        }
    }
}
