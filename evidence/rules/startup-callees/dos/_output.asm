; Copyright (C) 1985 by Manx Software Systems, Inc.
; :ts=8
	public	_DOSBase

	public	__Output
__Output
	move.l	_DOSBase,a6
	jmp	-60(a6)

