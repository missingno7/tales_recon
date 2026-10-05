; Copyright (C) 1986 by Manx Software Systems, Inc.
; :ts=8

	public	_SysBase

	public	__OpenLibrary
__OpenLibrary
	move.l	_SysBase,a6
	move.l	4(sp),a1
	move.l	8(sp),d0
	jmp	-552(a6)

