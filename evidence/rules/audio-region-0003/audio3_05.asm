; Typed CODE-resident audio data; historical ownership/TU UNKNOWN.
T3_HEADER macro
	dc.b \1,\2
	endm
T3_NOTE macro
	dc.b \1,\2
	endm
T3_SELECTOR macro
	dc.l \1
	endm
T3_ENVELOPE_PTR macro
	dc.l \1
	endm
T3_ENV_INITIAL macro
	dc.b \1
	endm
T3_ENV_DELTA macro
	dc.b \1
	endm
T3_ENV_TARGET macro
	dc.b \1
	endm
T3_ENV_DELAY macro
	dc.b \1
	endm
T3_ENV_ZERO macro
	dc.b 0
	endm
T3_COUNT macro
	dc.b $80,\1
	endm
T3_LOOP macro
	dc.b $81
	ds 0
	dc.l \1
	endm
T3_TRIGGER macro
	dc.b $82,\1
	endm
T3_JUMP macro
	dc.b $84
	ds 0
	dc.l \1
	endm
T3_CALL macro
	dc.b $85
	ds 0
	dc.l \1
	endm
T3_RETURN macro
	dc.b $86
	endm
T3_TRANSPOSE macro
	dc.b $87,\1
	endm
T3_END macro
	dc.b $88
	endm
T3_REST macro
	dc.b $89,\1
	endm
T3_PLAY_NOTE macro
	dc.b $8b,\1,\2
	endm
T3_PITCH_ADJUST macro
	dc.b $8c,\1
	endm
T3_ENVELOPE macro
	dc.b $8f,\1
	endm
T3_BANK macro
	dc.b $90,\1
	endm
T3_RAMP macro
	dc.b $91,\1,\2
	endm
T3_VIBRATO macro
	dc.b $95,\1,\2
	endm
T3_TICK_INCREMENT macro
	dc.b $97,\1
	endm
T3_HOLD macro
	dc.b $a0,\1
	endm
T3_ATTENUATION macro
	dc.b $ab,\1
	endm
T3_FLAGS macro
	dc.b $83,\1
	endm
T3_RAMP_OFF macro
	dc.b $92
	endm
T3_RANDOM_NOTE macro
	dc.b $99,\1
	endm
T3_CHANNEL_ATTENUATION macro
	dc.b $9e,\1
	endm
T3_SOUND_ENABLE macro
	dc.b $9f,\1
	endm
T3_MASTER_ATTENUATION macro
	dc.b $a3,\1
	endm
T3_ADD_MASTER_ATTENUATION macro
	dc.b $a4,\1
	endm
	cseg
	public _audio3_05_begin
	public _audio3_05_end
	public _audio3_c_679E
	public _audio3_h_6740
	public _audio3_h_675B
	public _audio3_h_6774
	public _audio3_h_6786
	public _audio3_h_6792
_audio3_05_begin:
_audio3_h_6740:
	T3_HEADER 0,0
	T3_ENVELOPE 10
	T3_BANK 7
	T3_ATTENUATION 224
	T3_FLAGS 255
	T3_NOTE 56,3
	T3_RAMP 252,0
	T3_HOLD 8
	T3_RAMP 0,0
	T3_HOLD 2
	T3_REST 2
	T3_NOTE 54,6
	T3_END
_audio3_h_675B:
	T3_HEADER 0,0
	T3_ENVELOPE 0
	T3_BANK 6
	T3_ATTENUATION 224
	T3_FLAGS 255
	T3_NOTE 104,8
	T3_RAMP 9,0
	T3_HOLD 6
	T3_RAMP 241,0
	T3_HOLD 9
	T3_REST 8
	T3_END
_audio3_h_6774:
	T3_HEADER 0,0
	T3_ENVELOPE 10
	T3_BANK 0
	T3_ATTENUATION 224
	T3_NOTE 36,3
	T3_REST 6
	T3_VIBRATO 1,138
	T3_NOTE 27,8
	T3_END
_audio3_h_6786:
	T3_HEADER 1,0
	T3_ENVELOPE 52
	T3_BANK 27
	T3_RAMP 7,0
	T3_NOTE 49,254
	T3_END
_audio3_h_6792:
	T3_HEADER 0,0
	T3_ENVELOPE 54
	T3_BANK 6
	T3_FLAGS 255
	T3_NOTE 112,4
	T3_COUNT 32
_audio3_c_679E:
	T3_RAMP 3,128
	T3_HOLD 4
	T3_RAMP 254,0
	T3_HOLD 4
	T3_LOOP _audio3_c_679E
	T3_END
_audio3_05_end:
	end
