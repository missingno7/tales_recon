/* Independent compiler fingerprint: adjacent_calls */
extern int first(); extern int second(); recovered(a) int a; { first(a); return second(a); }
