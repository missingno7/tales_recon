/* DOS cross-compiler hypothesis derived from exact Amiga ov10 functions.
   Experimental source only; no DOS or Amiga promotion follows from this file. */
extern unsigned int value_a;
extern unsigned int value_b;

int bitmask_difference(void)
{
    int d;
    d = (value_a & 7) - (value_b & 7);
    return d;
}

int shifted_difference(void)
{
    int d;
    d = (value_a >> 3) - (value_b >> 3);
    return d;
}
