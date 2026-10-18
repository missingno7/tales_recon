extern unsigned int cave_player_cell_index;
extern unsigned int cave_wandering_actor_cell_index;
extern int cave_cell_words[1];
extern char G_h01_73E6[1];
extern char G_h01_7344[1];
extern char G_h01_73B0[1];
extern char G_h01_737A[1];
extern int draw_cave_actor_sprite();
recovered() {
 if (cave_player_cell_index-8==cave_wandering_actor_cell_index && ((char)cave_cell_words[cave_player_cell_index]&8))
  draw_cave_actor_sprite(G_h01_73E6,17,5);
 else if (cave_player_cell_index-1==cave_wandering_actor_cell_index && ((char)cave_cell_words[cave_player_cell_index]&1))
  draw_cave_actor_sprite(G_h01_7344,17,2);
 else if (cave_player_cell_index-8==cave_wandering_actor_cell_index) draw_cave_actor_sprite(G_h01_73B0,17,4);
 else draw_cave_actor_sprite(G_h01_737A,17,3);
}
