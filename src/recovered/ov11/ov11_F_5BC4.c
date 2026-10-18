extern int jg_grid_tile_indices[6][4];

recovered(row, column)
int *row, *column;
{
    int i, j;

    for (i = 0; i < 6; i++)
        for (j = 0; j < 3; j++)
            if (jg_grid_tile_indices[i][j]) {
                *row = i;
                *column = j;
                return;
            }
}
