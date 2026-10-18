extern unsigned int cave_player_cell_index;
extern unsigned int cave_wandering_actor_cell_index;
recovered() { int d; d=(cave_player_cell_index>>3)-(cave_wandering_actor_cell_index>>3); return d; }
