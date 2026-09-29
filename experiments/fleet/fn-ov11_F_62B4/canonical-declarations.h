/* Declarations already used by canonical sources: candidate views, not provenance.
   Reuse them unless a hypothesis needs a different view (then that is the controlled change). */
struct ClusterRecord { char pad0[8]; int value8; int value10; char pad12[2]; int value14; int value16; char pad18[12]; int state30; int value32; char pad34[6]; int state40; int value42; int value2c; int value2e; char tail[4]; };
extern int G_h01_37EC; /* 1x; w2 */
extern int G_h01_37F2; /* 1x; w2 */
extern char G_h01_46E0; /* 8x; w1 */
extern struct ClusterRecord G_h01_8BEC[1]; /* 2x; alt int [1] x1, struct MotionRecord [1] x1, struct BRecord [1] x1 */
extern short G_h01_940C[1]; /* 1x; alt int [1] x1; tie */
extern unsigned int F_h00_463E(); /* 3x; alt int () x3, long () x3; tie */
extern int F_h11_41F6(); /* 6x */
extern int F_h11_5962(); /* 3x; alt void () x1 */
extern int F_h11_5A12(); /* 1x */
extern int F_h11_5A62(); /* 1x */
extern int F_h11_5C42(); /* 1x */
/* G_h01_37EE: no canonical view; w2 */
/* G_h01_37F0: no canonical view; w2 */
/* G_h01_8BEE: inside G_h01_8BEC+2 (struct ClusterRecord [1]) */
/* G_h01_8BF4: inside G_h01_8BEC+8 (struct ClusterRecord [1]) */
/* G_h01_8BFE: inside G_h01_8BEC+18 (struct ClusterRecord [1]) */
/* G_h01_8C18: inside G_h01_8BEC+44 (struct ClusterRecord [1]) */
/* G_h01_8C1A: inside G_h01_8BEC+46 (struct ClusterRecord [1]) */
/* G_h01_8C1C: inside G_h01_8BEC+48 (struct ClusterRecord [1]) */
