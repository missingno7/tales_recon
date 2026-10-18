struct Record { int field0,value; char tail[48]; };
extern struct Record jg_platform_records[1];
recovered(n) int n; { struct Record *p; p=&jg_platform_records[n]; return p->value; }
