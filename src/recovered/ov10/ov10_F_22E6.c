struct BoardCell {
    char pad;
    unsigned char bits;
};

extern int draw_masked_sprite();
extern int G_h01_7746;
extern char difficulty_level;
extern unsigned int cave_player_cell_index;
extern unsigned int cave_finish_cell_index;
extern unsigned int cave_wandering_actor_cell_index;

recovered(p)
struct BoardCell *p;
{
    int unused;
    unsigned x,y;
    int shift;

    shift=3;
    draw_masked_sprite(&G_h01_7746);
    if (difficulty_level) {
        x=((56-(cave_player_cell_index&248))>>3)+(cave_player_cell_index&7);
        y=(cave_player_cell_index>>3)+(cave_player_cell_index&7);
        if ((((unsigned short *)(p-1))[0]&64)==64 &&
            (cave_player_cell_index&7) && (p->bits&1) ||
            (((unsigned short *)(p+1))[0]&64)==64 &&
            (cave_player_cell_index&7)!=7 && (p->bits&2) ||
            (((unsigned short *)(p-8))[0]&64)==64 &&
            cave_player_cell_index>7 && (p->bits&8) ||
            (((unsigned short *)(p+8))[0]&64)==64 &&
            cave_player_cell_index<56 && (p->bits&4))
            *G_h01_5370=12;
        else
            *G_h01_5370=3;
        draw_cave_cell_connections(x*4+115,y*4+139,p+cave_player_cell_index,1);
        BltBitMap(active_screen_bitmap,(long)G_h01_7746,(long)G_h01_7748,
            &G_h01_774E,0L,0L,(long)(G_h01_774A<<shift),(long)G_h01_774C,
            192L,255L,0L);
    }
    x=((56-(cave_player_cell_index&248))>>3)+(cave_player_cell_index&7);
    y=(cave_player_cell_index>>3)+(cave_player_cell_index&7);
    *G_h01_5370=22;
    draw_cave_cell_connections(x*4+115,y*4+139,p+cave_player_cell_index,1);
    if (difficulty_level!=2) {
        x=((56-(cave_finish_cell_index&248))>>3)+(cave_finish_cell_index&7);
        y=(cave_finish_cell_index>>3)+(cave_finish_cell_index&7);
        *G_h01_5370=14;
        draw_cave_cell_connections(x*4+115,y*4+139,p+cave_finish_cell_index,1);
    }
    x=((56-(cave_wandering_actor_cell_index&248))>>3)+(cave_wandering_actor_cell_index&7);
    y=(cave_wandering_actor_cell_index>>3)+(cave_wandering_actor_cell_index&7);
    *G_h01_5370=8;
    draw_cave_cell_connections(x*4+115,y*4+139,p+cave_wandering_actor_cell_index,0);
}
