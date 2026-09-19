struct Point {
    char reserved[32];
    int x;
    int y;
};

struct PointRef {
    struct Point *point;
    char reserved[8];
};

extern struct PointRef G_h01_4524[36];
extern long F_h00_08FC();

long recovered(a,b)
int a,b;
{
    long distance, candidate;
    int x1, x2, y1, y2, unused0, unused1;

    if (a == b)
        return 0L;
    if (a == 35) {
        x1 = 56;
        y1 = 64;
    } else {
        x1 = G_h01_4524[a].point->x;
        y1 = G_h01_4524[a].point->y;
    }
    if (b == 35) {
        x2 = 56;
        y2 = 64;
    } else {
        x2 = G_h01_4524[b].point->x;
        y2 = G_h01_4524[b].point->y;
    }

    distance = F_h00_08FC(x1,x2,y1,y2);
    if (x1 < x2)
        candidate = F_h00_08FC(x1+272,x2,y1,y2);
    else
        candidate = F_h00_08FC(x1,x2+272,y1,y2);
    if (candidate < distance)
        distance = candidate;

    if (y1 < y2)
        candidate = F_h00_08FC(x1,x2,y1+140,y2);
    else
        candidate = F_h00_08FC(x1,x2,y1,y2+140);
    if (candidate < distance)
        distance = candidate;

    if (x1 < x2)
        x1 += 272;
    else
        x2 += 272;
    if (y1 < y2)
        y1 += 140;
    else
        y2 += 140;
    candidate = F_h00_08FC(x1,x2,y1,y2);
    if (candidate < distance)
        distance = candidate;

    distance = distance / 6606L + 1L;
    if (distance > 3L)
        distance = 3L;
    return distance;
}
