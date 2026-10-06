/* Reconstructed CLI parser variant using SDK-compatible access views.
   Original types, filenames, TU membership and storage ownership are unknown. */
struct ProcessView { char unknown_before_cli[172]; long pr_CLI; };
struct CliView {
    long cli_Result2;
    long cli_SetName;
    long cli_CommandDir;
    long cli_ReturnCode;
    long cli_CommandName;
};
extern long F_h00_892A();
extern int F_h00_7956();
extern int F_h00_7AF0();
extern int F_h00_7A9C();
extern int F_h00_8044();
/* Copyright (C) 1986,1987 by Manx Software Systems, Inc. */

/*
 *	This routine is called from the _main() routine and is used to
 *	parse the arguments passed from the CLI to the program. It sets
 *	up an array of pointers to arguments in the global variables and
 *	and sets up G_h01_B3B8 and G_h01_B3B4 which will be passed by _main() to
 *	the main() procedure. If no arguments are ever going to be
 *	parsed, this routine may be replaced by a stub routine to reduce
 *	program size.
 *
 *	If G_h01_B3BC is non-zero, the _exit() routine will call FreeMem()
 *	with G_h01_B3BC as the memory to free and G_h01_B3BA as the size.
 *
 */


extern int G_h01_B3B8;
extern int G_h01_B3BA;
extern char **G_h01_B3B4;
extern char *G_h01_B3BC;

recovered(pp, alen, aptr)
struct ProcessView *pp;
long alen;
register char *aptr;
{
	register char *cp;
	register struct CliView *cli;
	register int c;


	cli = (struct CliView *) ((long)pp->pr_CLI << 2);
	cp = (char *)((long)cli->cli_CommandName << 2);
	G_h01_B3BA = cp[0]+alen+2;
	if ((G_h01_B3BC = (char *)F_h00_892A((long)G_h01_B3BA, 0L)) == 0)
		return;
	c = cp[0];
	F_h00_7956(G_h01_B3BC, cp+1, c);
	F_h00_7AF0(G_h01_B3BC+c, " ");
	F_h00_7A9C(G_h01_B3BC, aptr, (int)alen);
	G_h01_B3BC[c] = 0;
	for (G_h01_B3B8=1,aptr=cp=G_h01_B3BC+c+1;;G_h01_B3B8++) {
		while ((c=*cp) == ' ' || c == '\t' || c == '\f' ||
												c == '\r' || c == '\n')
			cp++;
		if (*cp < ' ')
			break;
		if (*cp == '"') {
			cp++;
			while (c = *cp++) {
				*aptr++ = c;
				if (c == '"') {
					if (*cp == '"')
						cp++;
					else {
						aptr[-1] = 0;
						break;
					}
				}
			}
		}
		else {
			while ((c=*cp++) && c != ' ' && c != '\t' && c != '\f' &&
												c != '\r' && c != '\n')
				*aptr++ = c;
			*aptr++ = 0;
		}
		if (c == 0)
			--cp;
	}
	*aptr = 0;
	if ((G_h01_B3B4 = (char **)F_h00_892A((long)(G_h01_B3B8+1)*sizeof(*G_h01_B3B4), 0L)) == 0) {
		G_h01_B3B8 = 0;
		return;
	}
	for (c=0,cp=G_h01_B3BC;c<G_h01_B3B8;c++) {
		G_h01_B3B4[c] = cp;
		cp += F_h00_8044(cp) + 1;
	}
	G_h01_B3B4[c] = 0;
}

