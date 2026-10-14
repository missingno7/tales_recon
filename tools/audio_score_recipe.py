"""Independently authored symbolic score recipe; no oracle reads in this producer."""
import json
from pathlib import Path
from common import require

NOTE_NAMES = {'C':0,'Cs':1,'D':2,'Eb':3,'E':4,'F':5,'Fs':6,'G':7,'Gs':8,'A':9,'Bb':10,'B':11}


def source(recipe):
    require(recipe.get('schema_version')==1 and recipe.get('kind')=='AUDIO_SCORE_STREAM', 'unsupported score recipe')
    require(set(recipe)=={'schema_version','kind','channel','priority','attenuation','envelope','transpose','triggers','bank','tick_increment','events'}, 'unexpected score fields')
    for key in ('channel','priority','attenuation','envelope','transpose','bank','tick_increment'):
        require(type(recipe[key]) is int and 0<=recipe[key]<=255, 'invalid score parameter '+key)
    require(recipe['channel']<4, 'invalid channel')
    require(isinstance(recipe['triggers'],list) and all(type(x) is int and 0<=x<=255 for x in recipe['triggers']), 'invalid trigger identifiers')
    require(recipe['events'] and isinstance(recipe['events'],list), 'score events missing')
    lines=[
        '; Independently authored score, using the measured player command language.',
        '; No source filenames, tune names, historical object or release are claimed.',
        'STREAM macro', '\tdc.b\t\\1,\\2', '\tendm',
        'PARAM macro', '\tdc.b\t\\1,\\2', '\tendm',
        'TRIGGER macro', '\tdc.b\t$82,\\1', '\tendm',
        'NOTE macro', '\tdc.b\t\\1,\\2', '\tendm',
        'REST macro', '\tdc.b\t$89,\\1', '\tendm',
        'JUMP macro', '\tdc.b\t$84', '\tds\t0', '\tdc.l\t\\1', '\tendm',
        '\tcseg', '\tpublic\t_score_begin', '\tpublic\t_score_pattern', '\tpublic\t_score_end',
        '_score_begin:', '\tSTREAM\t%d,%d'%(recipe['channel'],recipe['priority']),
        '\tPARAM\t$ab,%d'%recipe['attenuation'], '\tPARAM\t$8f,%d'%recipe['envelope'],
        '\tPARAM\t$87,%d'%recipe['transpose']]
    lines += ['\tTRIGGER\t%d'%x for x in recipe['triggers']]
    lines += ['\tPARAM\t$90,%d'%recipe['bank'], '\tPARAM\t$97,%d'%recipe['tick_increment'], '_score_pattern:']
    for event in recipe['events']:
        require(set(event)=={'pitch','octave','ticks','rest'}, 'unexpected score event fields')
        require(event['pitch'] in NOTE_NAMES and type(event['octave']) is int and 0<=event['octave']<=7, 'invalid note')
        require(type(event['ticks']) is int and 0<event['ticks']<128 and type(event['rest']) is int and 0<event['rest']<128, 'invalid duration')
        pitch=event['octave']*16+NOTE_NAMES[event['pitch']]
        lines += ['\tNOTE\t%d,%d\t; %s octave %d'%(pitch,event['ticks'],event['pitch'],event['octave']), '\tREST\t%d'%event['rest']]
    return '\n'.join(lines+['\tJUMP\t_score_pattern','_score_end:','\tend',''])


def encoding(recipe):
    """Independent semantic check on producer output, never oracle bytes.

    Label coordinates arise from the emitted semantic events and alignment.
    This guards consistently rehashed source/receipt edits with stale outputs.
    """
    source(recipe)  # Same strict semantic grammar as the assembler source.
    code=bytearray((recipe['channel'],recipe['priority'],0xab,recipe['attenuation'],
                    0x8f,recipe['envelope'],0x87,recipe['transpose']))
    for trigger in recipe['triggers']:code.extend((0x82,trigger))
    code.extend((0x90,recipe['bank'],0x97,recipe['tick_increment']))
    pattern=len(code)
    for event in recipe['events']:
        code.extend((event['octave']*16+NOTE_NAMES[event['pitch']],event['ticks'],0x89,event['rest']))
    code.append(0x84)
    if len(code)%2:code.append(0)
    field=len(code);code.extend(pattern.to_bytes(4,'big'))
    return dict(code=bytes(code),pattern_offset=pattern,pointer_field=field)
