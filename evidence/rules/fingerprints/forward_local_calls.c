/* Independent compiler fingerprint: forward_local_calls */
int forward_public(); static int forward_static(); recovered(a) int a; { forward_public(a); return forward_static(a); } forward_public(a) int a; { return a+1; } static forward_static(a) int a; { return a-1; }
