; Copyright (C) 1985 by Manx Software Systems, Inc.
; :ts=8
	public	_SysBase

	public	__WaitPort
__WaitPort
	move.l	4(sp),a0
	move.l	_SysBase,a6
	jmp	-384(a6)

