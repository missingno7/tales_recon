/* SDK-compatible Workbench parser access views. Original filenames,
   TU membership, declared types and DATA ownership remain unknown. */
struct ProcessView {
 char unknown_before_cis[156];
 long pr_CIS, pr_COS;
 void *pr_ConsoleTask;
};
struct WBArgView { long wa_Lock; char *wa_Name; };
struct WBStartupView { char unknown_before_args[36]; struct WBArgView *sm_ArgList; };
struct DiskObjectView { char unknown_before_tooltypes[54]; char **do_ToolTypes; };
struct FileHandleView { char unknown_before_type[8]; long fh_Type; };
extern long G_h01_B3C0;
extern long F_h00_89D4();
extern long F_h00_86E0();
extern long F_h00_8C3C();
extern long F_h00_8C22();
extern int F_h00_8C30();
extern int F_h00_8784();
recovered(pp, wbm)
register struct ProcessView *pp;
struct WBStartupView *wbm;
{
 register char *cp;
 register struct DiskObjectView *dop;
 register struct FileHandleView *fhp;
 register long wind;
 if ((G_h01_B3C0 = F_h00_89D4("icon.library", 0L)) == 0)
  return;
 if ((dop = F_h00_8C3C(wbm->sm_ArgList->wa_Name)) == 0)
  goto closeit;
 if (cp = F_h00_8C22(dop->do_ToolTypes, "WINDOW")) {
  if (wind = F_h00_86E0(cp, 1005L)) {
   fhp = (struct FileHandleView *) (wind << 2);
   pp->pr_ConsoleTask = (void *) fhp->fh_Type;
   pp->pr_CIS = wind;
   pp->pr_COS = F_h00_86E0("*", 1005L);
  }
 }
 F_h00_8C30(dop);
closeit:
 F_h00_8784(G_h01_B3C0);
 G_h01_B3C0 = 0;
}
