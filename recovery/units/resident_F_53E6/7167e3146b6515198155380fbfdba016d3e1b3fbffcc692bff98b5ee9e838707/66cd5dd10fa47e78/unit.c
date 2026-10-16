/* Candidate v1 for resident_F_4F40: spin while the first longword equals the
   second, then copy the second longword over the first. */
extern long G_h01_B1EC;
extern long G_h01_B396;

F_h00_4F40()
{
    while (G_h01_B396 == G_h01_B1EC)
        ;
    G_h01_B396 = G_h01_B1EC;
}

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

F_h00_5392()
{
	((struct RecView *)G_h01_B288)->field_1c = 10;
	((struct RecView *)G_h01_B288)->field_28 = (long)&G_h01_B328;
	F_h00_894A(G_h01_B288);
	F_h00_8778(G_h01_B288);
	F_h00_8894(G_h01_B288);
	F_h00_8820(G_h01_B284);
}

extern int F_h00_5594();
extern int F_h00_5868();
extern int F_h00_4F40();
extern int F_h00_5392();
extern int F_h00_89EC();
extern int F_h00_868C();
extern int F_h00_4EC6();
extern long G_h01_A7CE;
extern long G_h01_A7D2;
extern long G_h01_B312;
recovered()
{
 F_h00_5594();
 F_h00_5868();
 F_h00_4F40();
 F_h00_89EC(5L,&G_h01_B312);
 F_h00_5392();
 F_h00_4EC6();
 F_h00_868C(G_h01_A7CE);
 F_h00_868C(G_h01_A7D2);
}

