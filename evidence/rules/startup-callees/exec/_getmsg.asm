; Copyright (C) 1985 by Manx Software Systems, Inc.
; :ts=8
	public	_SysBase

	public	__GetMsg
__GetMsg
	move.l	4(sp),a0
	move.l	_SysBase,a6
	jmp	-372(a6)

