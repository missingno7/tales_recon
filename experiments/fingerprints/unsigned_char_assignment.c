/* Independent compiler fingerprint: unsigned_char_assignment */
struct item { char pad[13]; unsigned char value; }; extern struct item input[1]; extern struct item output[1]; recovered() { output->value=input->value+0; }
