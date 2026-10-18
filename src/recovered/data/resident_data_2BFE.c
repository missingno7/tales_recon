struct DP_Cycle { unsigned short *words; unsigned short last; unsigned short destination; };
extern unsigned short palette_cycle_values_1[];
extern unsigned short palette_cycle_values_2[];
extern unsigned short palette_cycle_values_3[];
extern unsigned short palette_cycle_values_4[];
struct DP_Cycle palette_cycle_descriptors[5] = {{0, 0, 0}, {palette_cycle_values_1, 1, 2}, {palette_cycle_values_2, 3, 12}, {palette_cycle_values_3, 2, 2}, {palette_cycle_values_4, 3, 28}};
