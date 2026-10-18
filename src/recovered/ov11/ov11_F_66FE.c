struct Record { int padding[11],state,value; char tail[14]; };
extern struct Record jg_contact_hazard_records[36];
recovered(a,b) int a,b; { struct Record *p; p=&jg_contact_hazard_records[a]; p->state=2; if(!p->value || b==8)p->value=b; }
