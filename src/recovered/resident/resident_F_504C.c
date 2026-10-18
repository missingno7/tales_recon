extern int drain_input_key_queue();
recovered()
{
 int value;
 for(;;) {
  if(value=drain_input_key_queue()) break;
 }
 return value;
}
