struct DP_Sample { int duration; unsigned int length_words; char *sample_data; };
struct DP_Sequence { struct DP_Sample records[2]; int terminal_duration; };
extern struct DP_Sequence G_h01_23CC;
struct DP_Sequence * G_h01_2868 = &G_h01_23CC;
