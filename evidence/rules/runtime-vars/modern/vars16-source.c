/* Copyright (C) 1986,1987 by Manx Software Systems, Inc. */

#include <fcntl.h>
#include <workbench/startup.h>

void *SysBase, *DOSBase, *MathBase, *MathTransBase;
void *MathIeeeDoubBasBase, *MathIeeeDoubTransBase;

long _savsp, _stkbase;

int errno;
int Enable_Abort;

int _argc, _arg_len;
char **_argv, *_arg_lin;
struct WBStartup *WBenchMsg;

struct _dev *_devtab;
short _numdev = 20;

char *_detach_name = 0;			/* for DETACHED programs */
long _detach_curdir = 0;

void *_oldtrap, **_trapaddr;	/* for signal() cleanup */

