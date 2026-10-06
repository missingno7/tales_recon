; Copyright (C) 1985 by Manx Software Systems, Inc.
; :ts=8
	public	_DOSBase

	public	__Close
__Close
	move.l	4(sp),d1
	move.l	_DOSBase,a6
	jmp	-36(a6)

