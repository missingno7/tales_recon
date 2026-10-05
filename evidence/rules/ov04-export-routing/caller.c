extern int exported();
extern int localhelper();
int entry(n) int n; { return exported(n) + localhelper(); }
