recovered(n,p) int n,*p; { char i; if(n>=35)return 0; for(i=0;i<35;i++)if(*p++==n)return 0; return 1; }
