extern int input_key_ring_read_index;
extern int input_key_ring;
recovered()
{
 if(input_key_ring_read_index==input_key_ring) return 0;
 return 1;
}
