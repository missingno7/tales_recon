; Copyright (C) 1985 by Manx Software Systems, Inc.
; :ts=8
	public	_DOSBase

	public	__Input
__Input
	move.l	_DOSBase,a6
	jmp	-54(a6)

