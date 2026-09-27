int recovered(a)
int a;
{
 float x,y,z;
 x=(float)a;
 y=(float)(a+1);
 z=(x-y)*y/104.0;
 return (int)z;
}
