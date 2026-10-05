/* Independent compiler fingerprint: static_bss */
recovered(n) int n; { static int count; count+=n; return count; }
