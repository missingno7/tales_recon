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
	public _audio3_07_begin
	public _audio3_07_end
	public _audio3_c_6917
	public _audio3_h_68EC
	public _audio3_h_68FA
	public _audio3_h_6908
	public _audio3_h_6927
	public _audio3_h_6950
	public _audio3_h_695C
	public _audio3_h_696D
	public _audio3_h_6985
	public _audio3_h_699F
	public _audio3_h_69B6
_audio3_07_begin:
_audio3_h_68EC:
	T3_HEADER 1,0
	T3_ENVELOPE 24
	T3_BANK 26
	T3_NOTE 34,4
	T3_RAMP 1,160
	T3_HOLD 46
	T3_END
_audio3_h_68FA:
	T3_HEADER 1,0
	T3_ENVELOPE 24
	T3_BANK 26
	T3_NOTE 32,4
	T3_RAMP 254,160
	T3_HOLD 46
	T3_END
_audio3_h_6908:
	T3_HEADER 1,0
	T3_ENVELOPE 42
	T3_BANK 26
	T3_NOTE 48,2
	T3_RAMP 28,0
	T3_HOLD 6
	T3_COUNT 4
_audio3_c_6917:
	T3_RAMP 230,0
	T3_HOLD 4
	T3_RAMP 14,0
	T3_HOLD 4
	T3_LOOP _audio3_c_6917
	T3_END
_audio3_h_6927:
	T3_HEADER 0,0
	T3_ENVELOPE 40
	T3_BANK 56
	T3_NOTE 27,3
	T3_RAMP 249,0
	T3_HOLD 16
	T3_RAMP_OFF
	T3_HOLD 32
	T3_END
_audio3_h_6950:
	T3_HEADER 0,0
	T3_ENVELOPE 38
	T3_BANK 24
	T3_VIBRATO 12,182
	T3_NOTE 43,104
	T3_END
_audio3_h_695C:
	T3_HEADER 1,0
	T3_ENVELOPE 36
	T3_BANK 56
	T3_NOTE 3,5
	T3_RAMP 246,0
	T3_HOLD 50
	T3_RAMP_OFF
	T3_HOLD 32
	T3_END
_audio3_h_696D:
	T3_HEADER 0,0
	T3_ATTENUATION 48
	T3_ENVELOPE 34
	T3_BANK 56
	T3_NOTE 18,5
	T3_RAMP 32,0
	T3_HOLD 10
	T3_RAMP 241,0
	T3_HOLD 24
	T3_RAMP_OFF
	T3_HOLD 16
	T3_END
_audio3_h_6985:
	T3_HEADER 0,0
	T3_ENVELOPE 0
	T3_BANK 54
	T3_PITCH_ADJUST 0
	T3_RAMP 111,255
	T3_NOTE 32,10
	T3_CHANNEL_ATTENUATION 80
	T3_NOTE 32,6
	T3_CHANNEL_ATTENUATION 144
	T3_NOTE 32,8
	T3_CHANNEL_ATTENUATION 208
	T3_NOTE 32,8
	T3_END
_audio3_h_699F:
	T3_HEADER 0,0
	T3_ENVELOPE 32
	T3_BANK 53
	T3_TRANSPOSE 0
	T3_NOTE 16,10
	T3_CHANNEL_ATTENUATION 80
	T3_NOTE 16,10
	T3_CHANNEL_ATTENUATION 160
	T3_NOTE 16,10
	T3_CHANNEL_ATTENUATION 176
	T3_NOTE 16,10
	T3_END
_audio3_h_69B6:
	T3_HEADER 0,0
	T3_ENVELOPE 2
	T3_BANK 50
	T3_TRANSPOSE 0
	T3_NOTE 16,8
	T3_CHANNEL_ATTENUATION 32
	T3_NOTE 16,8
	T3_CHANNEL_ATTENUATION 80
	T3_NOTE 16,8
	T3_CHANNEL_ATTENUATION 112
	T3_NOTE 16,8
	T3_END
_audio3_07_end:
	end
