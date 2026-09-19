/* Independent compiler fingerprint: struct_fields */
struct item { char a,b; int n; long v; }; long recovered(p) struct item *p; { return p->v+p->n+p->a; }
