struct Event { long next; char kind; char reserved[2]; char value; };
struct Ring { int head,tail; char quit; char bytes[128]; };
extern int Forbid();
extern int Permit();
recovered(first,ring)
long first;
struct Ring *ring;
{
 struct Event *event;
 int next;
 event=(struct Event *)first;
 do {
  if(event->kind==1) {
   Forbid();
   next=(ring->head+1)&127;
   if(ring->tail!=next) {
    ring->bytes[ring->head]=event->value;
    ring->head=next;
   }
   Permit();
  } else if(event->kind==16) ring->quit=1;
 } while(event=(struct Event *)event->next);
 return 0;
}
