struct Item { char flag,pad; int kind; };
recovered(p) struct Item *p; { if(!p->flag)return 0; if(p->kind==16 || p->kind==32)return 4; return 3; }
