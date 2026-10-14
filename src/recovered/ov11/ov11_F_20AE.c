extern long F_h00_75D8();
extern int F_h00_704E();
extern int F_h00_3674();
extern int G_h01_7A94;
recovered(text) char *text; {
 char *line;
 line=F_h00_75D8(text,'C');
 if (F_h00_704E(line,"C %d",&G_h01_7A94)<1) F_h00_3674(44);
}
