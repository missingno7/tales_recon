/* Independent compiler fingerprint: unsigned_byte_pointer_promoted */
struct item { char pad[12]; int value; }; extern unsigned char output; recovered(p) struct item *p; { output=((unsigned char *)&p->value)[1]+0; }
