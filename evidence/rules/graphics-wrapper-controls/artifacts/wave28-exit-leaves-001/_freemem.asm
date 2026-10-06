; Copyright (C) 1985 by Manx Software Systems, Inc.
; :ts=8
	public	_SysBase

	public	__FreeMem
__FreeMem
	move.l	4(sp),a1
	move.l	8(sp),d0
	move.l	_SysBase,a6
	jmp	-210(a6)

