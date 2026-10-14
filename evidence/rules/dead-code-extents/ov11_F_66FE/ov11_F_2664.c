extern char *G_h01_5370;
extern long G_h01_46CA;
extern int F_h00_8B88();
extern int F_h00_8B4C();
extern int F_h00_8AA8();
recovered(x,y,w,h,pen) int x,y,w,h; char pen; {
 *G_h01_5370=pen;
 F_h00_8B88(G_h01_46CA,(long)*G_h01_5370);
 F_h00_8B4C(G_h01_46CA,(long)x,(long)y);
 F_h00_8AA8(G_h01_46CA,(long)(x+w),(long)y);
 F_h00_8B88(G_h01_46CA,(long)*G_h01_5370);
 F_h00_8B4C(G_h01_46CA,(long)x,(long)(y+h));
 F_h00_8AA8(G_h01_46CA,(long)(x+w),(long)(y+h));
 F_h00_8B88(G_h01_46CA,(long)*G_h01_5370);
 F_h00_8B4C(G_h01_46CA,(long)x,(long)y);
 F_h00_8AA8(G_h01_46CA,(long)x,(long)(y+h));
 F_h00_8B88(G_h01_46CA,(long)*G_h01_5370);
 F_h00_8B4C(G_h01_46CA,(long)(x+w),(long)y);
 F_h00_8AA8(G_h01_46CA,(long)(x+w),(long)(y+h));
}
