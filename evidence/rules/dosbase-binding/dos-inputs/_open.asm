; Copyright (C) 1985 by Manx Software Systems, Inc.
; :ts=8
	public	_DOSBase

	public	__Open
__Open
	movem.l	4(sp),d1/d2
	move.l	_DOSBase,a6
	jmp	-30(a6)
