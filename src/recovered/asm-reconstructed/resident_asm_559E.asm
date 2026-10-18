	far data
	public _resident_asm_559E,_resident_asm_55D6
_resident_asm_559E
	movem.l d7/a0-a1,-(sp)
	move.w #7,d7
	lea _audio_noise_random_state_byte,a0
	lea _audio_noise_random_state_word,a1
_rng_bit
	move.b 1(a1),d0
	roxl.b #4,d0
	eor.b d0,1(a1)
	move.b 1(a1),d0
	roxl.b #1,d0
	move.b (a0),d0
	roxr.b #1,d0
	move.b d0,(a0)
	roxr.w (a1)
	dbra d7,_rng_bit
	move.b (a0),d0
	movem.l (sp)+,d7/a0-a1
	rts
_resident_asm_55D6
	dseg
	public _audio_noise_random_state_byte,_audio_noise_random_state_word
	end
