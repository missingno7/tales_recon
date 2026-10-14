extern int F_h11_25D6();
F_h11_5F2A(a,b,c,d,e,f,g,h) int a,b,c,d,e,f,g,h; {
 return (F_h11_25D6(a,e,b)||F_h11_25D6(a,f,b)) &&
        (F_h11_25D6(c,g,d)||F_h11_25D6(c,h,d)) ? 1 : 0;
}
