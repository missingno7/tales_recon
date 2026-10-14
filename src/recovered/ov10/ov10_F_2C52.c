extern unsigned int G_h01_799E;
extern unsigned int G_h01_79A0;
extern int G_h01_4356[1];
extern char G_h01_73E6[1];
extern char G_h01_7344[1];
extern char G_h01_73B0[1];
extern char G_h01_737A[1];
extern int F_h10_2634();
recovered() {
 if (G_h01_799E-8==G_h01_79A0 && ((char)G_h01_4356[G_h01_799E]&8))
  F_h10_2634(G_h01_73E6,17,5);
 else if (G_h01_799E-1==G_h01_79A0 && ((char)G_h01_4356[G_h01_799E]&1))
  F_h10_2634(G_h01_7344,17,2);
 else if (G_h01_799E-8==G_h01_79A0) F_h10_2634(G_h01_73B0,17,4);
 else F_h10_2634(G_h01_737A,17,3);
}
