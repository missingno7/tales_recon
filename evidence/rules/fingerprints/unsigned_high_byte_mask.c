/* Independent compiler fingerprint: unsigned_high_byte_mask */
struct item { char pad[12]; int value; }; extern unsigned char output; recovered(p) struct item *p; { output=(p->value>>8)&255; }
