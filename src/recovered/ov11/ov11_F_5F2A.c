extern int integer_within_inclusive_range();
recovered(a,b,c,d,e,f,g,h) int a,b,c,d,e,f,g,h; {
 return (integer_within_inclusive_range(a,e,b)||integer_within_inclusive_range(a,f,b)) &&
        (integer_within_inclusive_range(c,g,d)||integer_within_inclusive_range(c,h,d)) ? 1 : 0;
}
