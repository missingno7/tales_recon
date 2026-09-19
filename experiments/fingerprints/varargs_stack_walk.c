/* Independent compiler fingerprint: varargs_stack_walk */
recovered(n,a) int n,a; { int *p,s; p=&a; s=0; while(n--) s+=*p++; return s; }
