extern int initialize_av();
extern int game_run_adventure();
extern int shutdown_av();

recovered()
{
    initialize_av();
    game_run_adventure();
    shutdown_av("");
}
