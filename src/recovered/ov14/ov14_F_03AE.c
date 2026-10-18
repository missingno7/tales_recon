extern char rival_current_location;
extern char rival_destination_location;
recovered(a,b)
char a,b;
{
    rival_current_location = a;
    rival_destination_location = b;
}
