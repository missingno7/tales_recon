extern unsigned int G_h01_00CC;
recovered(a)
     int a;
     {
     if (a >= 2)
         {
         if (a >= 4)
             {
             if (a >= 6)
                 {
                 G_h01_00CC = 0x4e;
                 }
             else
                 {
                 G_h01_00CC = 0x4f;
                 }
             }
         else
             {
             G_h01_00CC = 0x50;
             }
         }
     else
         {
         G_h01_00CC = 0x51;
         }
     return 0;
     }