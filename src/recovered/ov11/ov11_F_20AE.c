extern long F_h00_75D8();
extern int sscanf();
extern int report_loader_error();
extern int G_h01_7A94;
recovered(text) char *text; {
 char *line;
 line=F_h00_75D8(text,'C');
 if (sscanf(line,"C %d",&G_h01_7A94)<1) report_loader_error(44);
}
