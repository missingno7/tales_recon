	far data
	dseg
	public _palette_cycle_descriptors
	public _palette_cycle_callback_index
	public _palette_cycle_frame_countdown
	public _palette_cycle_word_index
	public _palette_cycle_countdown_step
	cseg
	public _recon_h00_61A0
	public _recon_h00_61B0
	public _recon_h00_61D8
	public _recon_h00_61F6
	public _end_cbcopy
_recon_h00_61A0
	move.b _palette_cycle_countdown_step,d0
	sub.b d0,_palette_cycle_frame_countdown
	bmi _recon_h00_61B0
	rts
_recon_h00_61B0
	move.b #$7f,_palette_cycle_frame_countdown
	lea.l _palette_cycle_descriptors,a2
	move.l _palette_cycle_callback_index,d0
	lsl.l #$3,d0
	adda.l d0,a2
	clr.l d0
	move.b _palette_cycle_word_index,d0
	subq.l #$1,d0
	bpl _recon_h00_61D8
	move.w $4(a2),d0
_recon_h00_61D8
	move.b d0,_palette_cycle_word_index
	lsl.w #$1,d0
	movea.l (a2),a0
	and.l #$ff,d0
	adda.l d0,a0
	move.w $6(a2),d0
	lsl.l #$2,d0
	adda.l d0,a1
	move.w $4(a2),d7
_recon_h00_61F6
	move.w (a0)+,(a1)+
	addq.l #$2,a1
	dbra d7,_recon_h00_61F6
	rts
_end_cbcopy
	dseg
	end
