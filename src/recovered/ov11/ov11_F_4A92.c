extern long G_h01_A460;
extern int free_bitmap();

int recovered() {
    return free_bitmap(G_h01_A460);
}
