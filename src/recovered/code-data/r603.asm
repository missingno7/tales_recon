; Typed envelope DATA only. Historical source/TU/owner UNKNOWN.
E6_PTR macro
	dc.l \1
	endm
E6_INITIAL macro
	dc.b \1
	endm
E6_DELTA macro
	dc.b \1
	endm
E6_TARGET macro
	dc.b \1
	endm
E6_DELAY macro
	dc.b \1
	endm
E6_ZERO macro
	dc.b 0
	endm
	cseg
	public _r603_begin
	public _r603_end
	public _audio6_e_6126
	public _audio6_e_6132
	public _audio6_e_6136
	public _audio6_e_613D
_r603_begin:
_audio6_e_6126:
	E6_DELTA -1
	E6_TARGET 8
	E6_ZERO
	E6_ZERO
_audio6_e_6132:
	E6_DELTA -5
	E6_TARGET 0
_audio6_e_6136:
	E6_INITIAL 0
	E6_DELTA 40
	E6_TARGET 216
	E6_DELTA -1
	E6_TARGET 128
	E6_ZERO
	E6_ZERO
_audio6_e_613D:
	E6_DELTA -49
	E6_TARGET 0
_r603_end:
	end
