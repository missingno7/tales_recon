extern int integer_within_inclusive_range();
recovered(a,b,c,d,e,f) int a,b,c,d,e,f; { return integer_within_inclusive_range(a,c,e) && integer_within_inclusive_range(b,d,f); }
