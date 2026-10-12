/* resident_F_5392 candidate v1 (baseline, no parent).
   Mechanical access view: the long global G_h01_B288 addresses a record whose
   word at +0x1c is set to 10 and whose long at +0x28 receives the address of
   G_h01_B328. That pointer value is then passed to four tail routines, and
   G_h01_B284 is passed to the last one. Names are mechanical offsets. */
struct RecView { char pad0[28]; short field_1c; char pad1[10]; long field_28; };

extern long G_h01_B284;
extern long G_h01_B288;
extern long G_h01_B328;
extern int F_h00_894A();
extern int F_h00_8778();
extern int F_h00_8894();
extern int F_h00_8820();

recovered()
{
	((struct RecView *)G_h01_B288)->field_1c = 10;
	((struct RecView *)G_h01_B288)->field_28 = (long)&G_h01_B328;
	F_h00_894A(G_h01_B288);
	F_h00_8778(G_h01_B288);
	F_h00_8894(G_h01_B288);
	F_h00_8820(G_h01_B284);
}
