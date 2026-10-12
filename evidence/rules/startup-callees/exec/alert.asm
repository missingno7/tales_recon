; Copyright (C) 1985 by Manx Software Systems, Inc.
; :ts=8
	public	_SysBase

	public	_Alert
_Alert
	movem.l	d7/a5,-(sp)
	movem.l	12(sp),d7/a5
	move.l	_SysBase,a6
	jsr	-108(a6)
	movem.l	(sp)+,d7/a5
	rts

