/* Independent compiler fingerprint: unsigned_char_assignment_plain */
struct item { char pad[13]; unsigned char value; }; extern struct item input[1]; extern struct item output[1]; recovered() { output->value=input->value; }
