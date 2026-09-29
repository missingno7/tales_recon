extern int G_h01_8B1C[6][4];

F_h11_5BC4(row, column)
int *row, *column;
{
    int i, j;

    for (i = 0; i < 6; i++)
        for (j = 0; j < 3; j++)
            if (G_h01_8B1C[i][j]) {
                *row = i;
                *column = j;
                return;
            }
}
