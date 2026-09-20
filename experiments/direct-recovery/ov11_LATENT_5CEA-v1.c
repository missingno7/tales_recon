/* Latent layout candidate; not eligible for function promotion. */
struct ClusterRecord {
    char pad0[30];
    int state30;
    char tail[20];
};
extern struct ClusterRecord G_h01_8BEC[1];

recovered(index)
int index;
{
    struct ClusterRecord *record;

    record=&G_h01_8BEC[index];
    return record->state30 > 0;
}
