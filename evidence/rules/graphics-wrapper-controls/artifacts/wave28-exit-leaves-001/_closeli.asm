; Copyright (C) 1985 by Manx Software Systems, Inc.
; :ts=8
	public	_SysBase

	public	__CloseLibrary
__CloseLibrary
	move.l	4(sp),a1
	move.l	_SysBase,a6
	jmp	-414(a6)

