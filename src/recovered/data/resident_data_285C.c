struct DP_Sample { int duration; unsigned int length_words; char *sample_data; };
struct DP_Sequence { struct DP_Sample records[2]; int terminal_duration; };
extern struct DP_Sequence G_h01_236C;
extern struct DP_Sequence G_h01_238C;
extern struct DP_Sequence G_h01_23AC;
struct DP_Sample *G_h01_285C[3] = {(struct DP_Sample *)&G_h01_236C, (struct DP_Sample *)&G_h01_238C, (struct DP_Sample *)&G_h01_23AC};
