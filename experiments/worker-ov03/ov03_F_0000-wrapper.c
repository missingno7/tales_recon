/*
 * Bounded source hypothesis for the 26-byte exported wrapper at ov03+0.
 * The final argument is tentatively represented as an empty string because
 * the PC-relative PEA addresses the two zero bytes at ov03+0x1a. Its boundary
 * is still not independently established as a C string.
 */
extern int F_h04_1E36();
extern int F_h03_001C();
extern int F_h04_27FE();

recovered()
{
    F_h04_1E36();
    F_h03_001C();
    F_h04_27FE("");
}
