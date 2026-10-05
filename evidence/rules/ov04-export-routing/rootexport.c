extern int entry();
extern int exported();
int (*candidate_reference)() = entry;
int (*export_reference)() = exported;
main() { return 0; }
