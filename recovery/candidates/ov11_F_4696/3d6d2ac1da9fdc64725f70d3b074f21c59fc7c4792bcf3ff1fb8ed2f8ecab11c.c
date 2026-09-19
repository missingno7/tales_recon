extern unsigned int G_h01_34EC;
extern unsigned int G_h01_8A3C;
extern unsigned int G_h01_8A3E;

recovered(a, b, c, d, e, f, g, h, i, j, k, l, m, n, o, p, q, r, s, t, u, v, w, x, y, z, aa, ab) int a, b, c, d, e, f, g, h, i, j, k, l, m, n, o, p, q, r, s, t, u, v, w, x, y, z, aa, ab;
{
    int temp;
    int *ptr;
    
    ptr = (int *)(((long)a << 16) | b);
    temp = c * 0xe;
    temp += (long)ptr + (long)temp;
    *(int *)((char *)ptr - 4) = temp;
    
    if (*(short *)((char *)G_h01_8A3C + 0xa3e) >= 2)
        goto L1;
    
    temp = d - e;
    if (temp < 0)
        goto L2;
    
    temp = f + g;
    if (temp <= 0)
        goto L3;
    
    *(short *)((char *)ptr + 8) = 0;
    goto L4;
    
L2:
    *(short *)((char *)ptr + 8) = 0;
    goto L4;
    
L3:
    *(short *)((char *)ptr + 8) = 0;
    goto L4;
    
L1:
    if (h < 0x140)
        goto L5;
    
    *(short *)((char *)ptr + 8) = 0;
    goto L6;
    
L5:
    temp = h + i;
    if (temp > 0x140)
    {
        *(short *)((char *)ptr + 12) = 0x140 - h + 8;
        goto L7;
    }
    
L6:
    *(short *)((char *)ptr + 8) = 0;
    goto L4;
    
L7:
    if (j < 0xb0)
        goto L8;
    
    *(short *)((char *)ptr + 10) = 0;
    goto L9;
    
L8:
    temp = j + k;
    if (temp > 0xb0)
    {
        *(short *)((char *)ptr + 14) = 0xb0 - j;
        goto L9;
    }
    
L9:
    if (l <= 0)
        goto L10;
    
    if (m <= 0)
        goto L11;
    
    *(short *)((char *)ptr + 14) = *(short *)((char *)ptr + 12);
    goto L12;
    
L10:
    *(short *)((char *)ptr + 10) = 0;
    goto L13;
    
L11:
    *(short *)((char *)ptr + 10) = 0;
    goto L13;
    
L12:
    *(short *)((char *)ptr + 12) = *(short *)((char *)ptr + 14);
    goto L13;
    
L13:
    *(short *)((char *)ptr + 2) = *(short *)((char *)ptr + 8);
    *(short *)((char *)ptr + 4) = *(short *)((char *)ptr + 10);
    *(short *)((char *)ptr + 6) = *(short *)((char *)ptr + 12);
    *(short *)((char *)ptr + 8) = *(short *)((char *)ptr + 14);
    *(short *)((char *)ptr + 10) = *(short *)((char *)ptr + 16);
    
L4:
    return;
}