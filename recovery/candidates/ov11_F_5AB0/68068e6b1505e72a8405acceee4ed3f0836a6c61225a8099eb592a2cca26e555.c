/* Direct reconstruction candidate for ov11_F_5AB0. */
extern int G_h01_94BA;
extern int G_h01_94BC;
extern int G_h01_8B1C[41][4];

recovered(direction, kind, result)
int direction;
int kind;
int *result;
{
    int found;
    int row;
    int column;

    found = 0;
    row = G_h01_94BA;
    if (direction == 1)
        row++;
    else if (direction == 0)
        row--;
    if (row < 0 || row > 40)
        return found;
    if (direction != 0) {
        if (direction == 1) {
            if (kind == 2) {
                column = G_h01_94BC - 1;
                if (column >= 0)
                    if (G_h01_8B1C[row][column]) {
                        *result = column;
                        found = 1;
                    }
            } else if (kind == 3) {
                column = G_h01_94BC + 1;
                if (column < 3)
                    if (G_h01_8B1C[row][column]) {
                        *result = column;
                        found = 1;
                    }
            }
        } else if (direction == 2) {
            if (G_h01_94BC > 0) {
                if (G_h01_8B1C[row][G_h01_94BC - 1]) {
                    *result = G_h01_94BC - 1;
                    found = 1;
                }
            }
        }
    }
    return found;
}
