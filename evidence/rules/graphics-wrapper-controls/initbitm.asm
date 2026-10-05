; Copyright (C) 1985 by Manx Software Systems, Inc.
; :ts=8
	public	_GfxBase

	public	_InitBitMap
_InitBitMap
	move.l	4(sp),a0
	movem.l	8(sp),d0-d2
	move.l	_GfxBase,a6
	jmp	-390(a6)

