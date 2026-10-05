/* Independent compiler fingerprint: nested_if */
recovered(a,b) int a,b; { if(a) { if(b) return a+b; return a; } return b; }
