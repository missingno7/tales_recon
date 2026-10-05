/* Independent compiler fingerprint: char_struct_index */
struct item { long a,b,c; }; extern struct item table[36]; long recovered(i) char i; { return table[i].b; }
