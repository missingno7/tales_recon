extern int F_h00_701A();
extern long AvailMem();
extern int shutdown_av();
extern int F_h00_8534();

recovered(code)
int code;
{
    long r;

    F_h00_701A("ERROR #%d\n", code);
    switch (code) {
    case 2000:
        F_h00_701A("LoadIT() - BitMap AllocBM failed\n");
        break;
    case 6000:
        F_h00_701A("AllocPlane() -  AllocMem() failed\n");
        break;
    case 5000:
        F_h00_701A("LoadIT() - Unknown block type\n");
        break;
    }
    r = AvailMem(2L);
    F_h00_701A("Chip Mem: %ld ($%lx)\n", r, r);
    r = AvailMem(4L);
    F_h00_701A("Fast Mem: %ld ($%lx)\n", r, r);
    shutdown_av("System Error");
    F_h00_8534();
}
