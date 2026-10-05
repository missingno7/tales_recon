extern int overlay_entry();
int initialized = 7;
long resident_space[3];
main() { resident_space[1] = initialized; return overlay_entry(); }
