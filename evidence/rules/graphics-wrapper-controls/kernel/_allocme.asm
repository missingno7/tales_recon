; Copyright (C) 1985 by Manx Software Systems, Inc.
; :ts=8
	public	_SysBase

	public	__AllocMem
__AllocMem
	movem.l	4(sp),d0/d1
	move.l	_SysBase,a6
	jmp	-198(a6)

