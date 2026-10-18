	far data
	dseg
	public _audio_channel_1_block_countdown
	public _audio_channel_1_sample_block_cursor
	cseg
	public _recon_h00_5646
	public _recon_h00_565C
	public _recon_h00_568C
	public _recon_h00_56A2
	public _recon_h00_56AC
	public _end_irq1
_recon_h00_5646
	move.w $dff002,d0
	btst #$1,d0
	bne _recon_h00_565C
	move.w #$100,$dff09a
	bra _recon_h00_56A2
_recon_h00_565C
	subq.w #$1,_audio_channel_1_block_countdown
	bne _recon_h00_56A2
	movea.l _audio_channel_1_sample_block_cursor,a0
	move.w (a0)+,d0
	tst.w d0
	bmi _recon_h00_56AC
	beq _recon_h00_568C
	move.w d0,_audio_channel_1_block_countdown
	move.w (a0)+,$dff0b4
	move.l (a0)+,$dff0b0
	move.l a0,_audio_channel_1_sample_block_cursor
	bra _recon_h00_56A2
_recon_h00_568C
	move.w d0,_audio_channel_1_block_countdown
	move.w #$2,$dff096
	move.w #$100,$dff09a
_recon_h00_56A2
	move.w #$100,$dff09c
	rts
_recon_h00_56AC
	move.w #$7fff,_audio_channel_1_block_countdown
	bra _recon_h00_56A2
_end_irq1
	dseg
	end
