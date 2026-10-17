struct DP_Sample { int duration; unsigned int length_words; char *sample_data; };
struct DP_Sequence { struct DP_Sample records[1]; int terminal_duration; };
struct DP_Sequence G_h01_2114 = {{{1, 0, 0}}, -32768};
