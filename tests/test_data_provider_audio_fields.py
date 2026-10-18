"""Audio DATA receipts depend on current semantic facts, not model file bytes."""
import copy
import json
from pathlib import Path
import sys
from unittest.mock import patch

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / 'tools'))
from common import FormatError, sha256
import data_provider_audio_fields as audio


def fixture(route):
    if route == 'AUDIO_CHANNEL_FIELD':
        field, at, ty = 'stream', 0x3404, 'unsigned char *'
        fid, operand = audio.CHANNEL[field]
        selector = 'moveq #$3,d7; lsl.l #$2,d0; lea _G_h01_29FA,a0; movea.l 0(a0,d0.l),a0; dbra d7,_recon_h00_58CA'
        anchors = {fid: (operand, {}, None), 'resident_driver_58BC': (selector, {}, None)}
    elif route == 'AUDIO_IRQ_FIELD':
        field, at, ty = 'countdown', 0x2b4e, 'int'
        anchors = {'resident_frameless_55D6': ('subq.w #$1,_G_h01_2B4E', {}, None),
                   'resident_driver_58BC': ('moveq #$3,d7; dbra d7,_recon_h00_58CA', {}, None),
                   'resident_asm_59A4': ('move.w d7,d3; lsl.w #3,d3; lea _G_h01_2B4E,a2; adda.w d3,a2; move.l a4,4(a2)', {}, None)}
    elif route == 'AUDIO_GLOBAL_CELL':
        field = 'master_attenuation'
        at, ty, fid, operand = audio.GLOBALS[field]
        anchors = {fid: (operand, {}, None)}
    else:
        field, at, ty = 'period', 0x29de, 'unsigned short'
        anchors = {'resident_driver_57E4': ('clr.w $12(a1)', {}, None),
                   'resident_asm_59A4': ('clr.l d1; move.b d0,d1; and.b #$f,d1; add.b $12(a0),d1; cmp.b #$b,d1; ble _L59C6; sub.b #$c,d1; lsl.w #1,d1; lea _G_h01_29DE,a2; move.w 0(a2,d1.w),d1; move.w d1,6(a3)', {}, None)}
    size = audio.WIDTHS[ty]
    symbol = 'G_h01_%04X' % at
    model = dict(schema_version=1, structs={'GameAudioChannel': dict(size=None, fields=[dict(name='stream', offset=4, type='unsigned char *', evidence='independent field witness')])},
                 globals={symbol: dict(type=ty, extent=size, basis='CURATED', evidence='independent scalar witness')})
    fact = dict(schema_version=1, kind='BOUNDED_DATA_TABLE', id='resident_data_%04X' % at,
                source='src/recovered/data/resident_data_%04X.c' % at, original=dict(hunk=1, start=at, size=size),
                definitions=[dict(symbol=symbol, type=ty, offset=0, dimensions=[], initializer=None if ty.endswith('*') else 0, bounds=dict(kind=route, bytes=size))],
                route=route, selector_index=0, field=field, data_model_sha256=sha256(json.dumps(model).encode()),
                anchors={fid: dict(source_sha256='a'*64, proof_sha256='b'*64) for fid in anchors},
                object_sections=dict(CODE=0, DATA=(size+1)&~1, BSS=0, COMMON=0),
                historical_owner='UNKNOWN', historical_tu='UNKNOWN', original_filename=None, producer={})
    return fact, model, anchors


def verify(root, fact, model, anchors):
    path = root / 'recovery/data_model.json'
    path.parent.mkdir(exist_ok=True)
    path.write_text(json.dumps(model), newline='\n')
    with patch.object(audio, 'anchors', return_value=anchors), patch.object(audio, 'pointer_target', return_value=0x3400), patch('game_image.game', return_value=(b'', {}, None)):
        return audio.typed_evidence(root, fact, {}, {}, [])


@pytest.mark.parametrize('route', sorted(audio.ROUTES))
def test_model_diagnostic_edits_do_not_change_receipt(tmp_path, route):
    fact, model, anchors = fixture(route)
    before = verify(tmp_path, fact, model, anchors)
    changed = copy.deepcopy(model)
    changed['structs']['GameAudioChannel']['fields'][0]['evidence'] = 'reworded field witness'
    for row in changed['globals'].values():
        row['evidence'] = 'different declaration grouping and counts'
    changed['globals']['G_h01_4000'] = dict(type='long', extent=4, basis='CURATED', evidence='unrelated fact')
    changed['globals'] = dict(reversed(list(changed['globals'].items())))
    changed = dict(reversed(list(changed.items())))
    assert verify(tmp_path, fact, changed, anchors) == before
    assert before[0]['data_model_sha256'] == fact['data_model_sha256']


@pytest.mark.parametrize('key,value', [('type','char *'), ('type','unsigned char[4]'), ('offset',6), ('name','other_field')])
def test_changed_channel_field_refuses(tmp_path, key, value):
    fact, model, anchors = fixture('AUDIO_CHANNEL_FIELD')
    model['structs']['GameAudioChannel']['fields'][0][key] = value
    with pytest.raises((FormatError, StopIteration)):
        verify(tmp_path, fact, model, anchors)


@pytest.mark.parametrize('route', ['AUDIO_IRQ_FIELD','AUDIO_GLOBAL_CELL'])
@pytest.mark.parametrize('change', ['type','extent','identity'])
def test_changed_scalar_interpretation_refuses(tmp_path, route, change):
    fact, model, anchors = fixture(route)
    symbol = fact['definitions'][0]['symbol']
    if change == 'identity':
        model['globals']['G_h01_4000'] = model['globals'].pop(symbol)
    else:
        model['globals'][symbol][change] = 'unsigned int' if change == 'type' else 4
    with pytest.raises((FormatError, KeyError)):
        verify(tmp_path, fact, model, anchors)


def test_independent_asm_scalar_needs_no_invented_model_entry(tmp_path):
    fact, model, _ = fixture('AUDIO_GLOBAL_CELL')
    field = 'noise_word'
    at, ty, fid, operand = audio.GLOBALS[field]
    fact.update(field=field, id='resident_data_%04X'%at, source='src/recovered/data/resident_data_%04X.c'%at,
                original=dict(hunk=1,start=at,size=2), anchors={fid:fact['anchors'][next(iter(fact['anchors']))]})
    fact['definitions'][0].update(symbol='G_h01_%04X'%at, type=ty, bounds=dict(kind='AUDIO_GLOBAL_CELL',bytes=2))
    fact['object_sections']['DATA'] = 2
    model['globals'] = {}
    anchors = {fid:(operand,{},None)}
    before = verify(tmp_path, fact, model, anchors)
    model['globals'][fact['definitions'][0]['symbol']] = dict(type=ty,extent=2)
    assert verify(tmp_path, fact, model, anchors) == before
    model['globals'][fact['definitions'][0]['symbol']]['type'] = 'int'
    with pytest.raises(FormatError):
        verify(tmp_path, fact, model, anchors)
