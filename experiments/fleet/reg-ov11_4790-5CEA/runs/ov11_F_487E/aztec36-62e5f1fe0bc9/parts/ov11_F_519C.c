/* Direct recovery candidate for a 40-byte motion record dispatch. */
struct MotionRecord {
    char bytes[40];
};

extern struct MotionRecord G_h01_3724[1];
extern int F_h11_4610();

F_h11_519C(n)
int n;
{
    struct MotionRecord *record;

    record = &G_h01_3724[n];
    F_h11_4610(record);
}
