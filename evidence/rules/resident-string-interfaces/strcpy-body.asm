; Copyright (C) 1984 by Manx Software Systems, Inc.
; :ts=8
;
	public _strcpy_body
_strcpy_body
	move.l	4(sp),a0
	move.l	a0,d0
	move.l	8(sp),a1
.1
	move.b	(a1)+,(a0)+
	bne.s	.1
	rts
;
