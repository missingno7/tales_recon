struct DP_Sample { int duration; unsigned int length_words; char *sample_data; };
struct DP_Sequence { struct DP_Sample records[1]; int terminal_duration; };
extern struct DP_Sequence G_h01_2654;
struct DP_Sequence * G_h01_28CC = &G_h01_2654;
