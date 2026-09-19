/* Independent compiler fingerprint: movem_pressure */
long recovered(p,n) long *p; int n; { register long a,b,c,d; a=p[0]; b=p[1]; c=p[2]; d=p[3]; while(n--) { a+=b; b+=c; c+=d; d+=a; } return a+b+c+d; }
