/* Independent compiler fingerprint: unsigned_byte_pointer_assignment */
struct item { char pad[12]; int value; }; extern unsigned char output; recovered(p) struct item *p; { output=((unsigned char *)&p->value)[1]; }
