; Copyright (C) 1985 by Manx Software Systems, Inc.
; :ts=8
	public	_DOSBase

	public	__CurrentDir
__CurrentDir
	move.l	4(sp),d1
	move.l	_DOSBase,a6
	jmp	-126(a6)

