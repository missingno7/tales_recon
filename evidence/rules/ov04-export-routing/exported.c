int exported(n) int n; { if (n) return exported(n-1); return 7; }
