	far data
	dseg
	public _graphics_library_base
	cseg
	public _F_h00_4692
_F_h00_4692
	movem.l d4-d6/a2-a6,-(sp)
	movea.l 36(sp),a0
	move.l 40(sp),d0
	move.l 44(sp),d1
	movea.l 48(sp),a1
	move.l 52(sp),d2
	move.l 56(sp),d3
	move.l 60(sp),d4
	move.l 64(sp),d5
	move.l 68(sp),d6
	movea.l 72(sp),a2
	movea.l _graphics_library_base,a6
	jsr -636(a6)
	movem.l (sp)+,d4-d6/a2-a6
	rts
	dseg
	end
