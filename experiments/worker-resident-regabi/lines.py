from pathlib import Path
p=Path('toolchain/installed/aztec-3.6a/Library Source/ffp.arc')
for i,l in enumerate(p.read_text(errors='replace').splitlines(),1):
 if any(s in l for s in ['amiga_ffp:','tst.l\t_MathBase','movem.l\td0/d1/a0/a1','move.l\t4(sp),a0','jsr\t(a6,a0.l)','amiga_math:','move.w\t(sp)+,a0','move.l\t4(sp),d0','_Fadd','.Fadd:','_pow']): print(i,l)
