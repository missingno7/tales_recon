/* SDK-derived access views; original filenames, TU and provider unknown. */
/* Copyright (C) 1986,1987 by Manx Software Systems, Inc. */

#define EBADF 2
#define O_STDIO 0x8000
struct DevView { long fd; short mode; };
extern struct DevView *G_h01_B3A6;
extern short G_h01_2EB0;
extern int G_h01_B3CC;
extern int F_h00_8690();

recovered(fd)
register int fd;
{
	register struct DevView *refp;
	register int i, err;

	refp = G_h01_B3A6 + fd;
	if (fd < 0 || fd >= G_h01_2EB0 || refp->fd == 0) {
		G_h01_B3CC = EBADF;
		return(-1);
	}
	if ((refp->mode & O_STDIO) == 0)
		F_h00_8690(refp->fd);
	refp->fd = 0;
	return(0);
}

