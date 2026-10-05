; Copyright (C) 1985 by Manx Software Systems, Inc.
; :ts=8
	public	_GfxBase

	public	_InitView
_InitView
	move.l	4(sp),a1
	move.l	_GfxBase,a6
	jmp	-360(a6)

