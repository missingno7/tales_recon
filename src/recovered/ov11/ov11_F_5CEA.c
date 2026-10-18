struct Record { int fields[15]; int value; char tail[20]; };
extern struct Record jg_platform_records[1];
recovered(n) int n; { struct Record *p; p=&jg_platform_records[n]; return p->value>0 ? 1 : 0; }
