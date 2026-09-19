F_h11_25D6(a,b,c) int a,b,c; { return b>=a && b<=c; }


recovered(a,b,c,d,e,f) int a,b,c,d,e,f; { return F_h11_25D6(a,c,e) && F_h11_25D6(b,d,f); }

