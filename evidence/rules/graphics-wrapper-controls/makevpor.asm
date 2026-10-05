; Copyright (C) 1985 by Manx Software Systems, Inc.
; :ts=8
	public	_GfxBase

	public	_MakeVPort
_MakeVPort
	movem.l	4(sp),a0/a1
	move.l	_GfxBase,a6
	jmp	-216(a6)

