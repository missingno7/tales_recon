/* Independent compiler fingerprint: register_loop */
recovered(a,n) int *a,n; { register int i,s; s=0; for(i=0;i<n;i++) s+=a[i]; return s; }
