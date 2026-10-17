struct DP_Sample { int duration; unsigned int length_words; char *sample_data; };
struct DP_Sequence { struct DP_Sample records[2]; int terminal_duration; };
struct DP_Sequence G_h01_24EC = {{{1, 0, 0}, {1, 0, 0}}, -32768};
