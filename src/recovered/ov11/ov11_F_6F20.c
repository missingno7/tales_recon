struct Record { int head[9],x,y; char tail[12]; };
extern struct Record jg_moving_object_records[1];
recovered(a,b,n) int a,b,n; { struct Record *p; int x,y;
 p=&jg_moving_object_records[n]; x=p->x/53; y=(p->y-48)>>5;
 return x==a && y==b ? 1 : 0;
}
