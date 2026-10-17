struct DP_Sample { int duration; unsigned int length_words; char *sample_data; };
struct DP_Sequence { struct DP_Sample records[1]; int terminal_duration; };
extern struct DP_Sequence G_h01_20CC;
struct DP_Sequence * G_h01_27F4 = &G_h01_20CC;
