; Copyright (C) 1985 by Manx Software Systems, Inc.
; :ts=8
	public	_GfxBase

	public	_InitVPort
_InitVPort
	move.l	4(sp),a0
	move.l	_GfxBase,a6
	jmp	-204(a6)

