recovered(i, j) char i, j; { char *p; long x; p = (char *)-34608L; x = *(p + i); if (x != j) return 0; p = (char *)-34609L; x = *(p + i); if (x != j) return 0; return 1; }
