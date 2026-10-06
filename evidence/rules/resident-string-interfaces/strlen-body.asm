; Copyright (C) 1984 by Manx Software Systems, Inc.
; :ts=8
;
	public _strlen_body
_strlen_body
	move.l	4(sp),a0
	move.l	a0,d0
.1
	tst.b	(a0)+
	bne.s	.1
	sub.l	d0,a0
	move.l	a0,d0
	sub.l	#1,d0
	rts
;
