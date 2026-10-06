; Copyright (C) 1985 by Manx Software Systems, Inc.
; :ts=8
	public	_SysBase

	public	__ReplyMsg
__ReplyMsg
	move.l	4(sp),a1
	move.l	_SysBase,a6
	jmp	-378(a6)

