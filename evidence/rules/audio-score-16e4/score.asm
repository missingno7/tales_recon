; Independently authored score, using the measured player command language.
; No source filenames, tune names, historical object or release are claimed.
STREAM macro
	dc.b	\1,\2
	endm
PARAM macro
	dc.b	\1,\2
	endm
TRIGGER macro
	dc.b	$82,\1
	endm
NOTE macro
	dc.b	\1,\2
	endm
REST macro
	dc.b	$89,\1
	endm
JUMP macro
	dc.b	$84
	ds	0
	dc.l	\1
	endm
	cseg
	public	_score_begin
	public	_score_pattern
	public	_score_end
_score_begin:
	STREAM	3,0
	PARAM	$ab,192
	PARAM	$8f,8
	PARAM	$87,0
	TRIGGER	136
	TRIGGER	140
	TRIGGER	141
	PARAM	$90,26
	PARAM	$97,224
_score_pattern:
	NOTE	51,4	; Eb octave 3
	REST	4
	NOTE	52,4	; E octave 3
	REST	4
	NOTE	53,4	; F octave 3
	REST	4
	NOTE	54,4	; Fs octave 3
	REST	4
	NOTE	55,4	; G octave 3
	REST	4
	NOTE	56,4	; Gs octave 3
	REST	4
	NOTE	57,4	; A octave 3
	REST	4
	NOTE	56,4	; Gs octave 3
	REST	4
	NOTE	55,4	; G octave 3
	REST	4
	NOTE	54,4	; Fs octave 3
	REST	4
	NOTE	53,4	; F octave 3
	REST	4
	NOTE	52,4	; E octave 3
	REST	4
	JUMP	_score_pattern
_score_end:
	end
