; Copyright (C) 1985 by Manx Software Systems, Inc.
; :ts=8
	public	_SysBase

	public	__Forbid
__Forbid
	move.l	_SysBase,a6
	jmp	-132(a6)

