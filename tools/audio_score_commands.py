"""Typed audio commands and Manx macro producer; no oracle reads in this module."""
import re
from common import require

# Operand widths are independently checked against the freshly decoded grammar.
SPECS={
 'COUNT':(0x80,('count',)), 'LOOP':(0x81,('target',)),
 'TRIGGER':(0x82,('identifier',)), 'JUMP':(0x84,('target',)),
 'CALL':(0x85,('target',)), 'RETURN':(0x86,()),
 'TRANSPOSE':(0x87,('delta',)), 'END':(0x88,()), 'REST':(0x89,('ticks',)),
 'PLAY_NOTE':(0x8b,('pitch','ticks')), 'PITCH_ADJUST':(0x8c,('delta',)),
 'ENVELOPE':(0x8f,('identifier',)), 'BANK':(0x90,('identifier',)),
 'RAMP':(0x91,('high','low')), 'VIBRATO':(0x95,('rate','depth')),
 'TICK_INCREMENT':(0x97,('increment',)), 'HOLD':(0xa0,('ticks',)),
 'ATTENUATION':(0xab,('value',))}
BY_OPCODE={op:name for name,(op,fields) in SPECS.items()}
LABEL=re.compile(r'_audio_c_[0-9A-F]{4}')


def integer(value,high=255):
    require(type(value) is int and 0<=value<=high,'measured value outside typed operand range')
    return value


def check(command):
    require(set(command)=={'offset','command','operands'} and type(command['offset']) is int,'typed command fields')
    name=command['command'];args=command['operands']
    require(isinstance(args,dict),'typed operand fields')
    if name=='HEADER':
        require(set(args)=={'channel','priority'},'header fields');integer(args['channel'],3);integer(args['priority'])
    elif name=='NOTE':
        require(set(args)=={'pitch','ticks'},'note fields');integer(args['pitch'],127);integer(args['ticks'])
    else:
        require(name in SPECS,'unknown or unused audio command')
        fields=SPECS[name][1];require(set(args)==set(fields),'command operand fields')
        for k in fields:
            if k=='target':require(type(args[k]) is str and LABEL.fullmatch(args[k]),'unnamed pointer operand')
            else:integer(args[k])
    return name,args


def label(offset):return '_audio_c_%04X'%offset

def header_label(offset):return '_audio_h_%04X'%offset


def macros():
    lines=['; Typed bytecode data. No original source filename or TU is claimed.',
           'SC_HEADER macro','\tdc.b \\1,\\2','\tendm',
           'SC_NOTE macro','\tdc.b \\1,\\2','\tendm']
    for name,(op,fields) in SPECS.items():
        lines+=['SC_'+name+' macro']
        if fields==('target',):lines+=['\tdc.b $%02x'%op,'\tds 0','\tdc.l \\1']
        else:lines+=['\tdc.b '+','.join(['$%02x'%op]+['\\%d'%(i+1) for i in range(len(fields))])]
        lines+=['\tendm']
    return lines


def encode(commands,proven_labels):
    """Semantic byte encoding, with symbolic pointer fields left zero.

    Cursor coordinates arise from typed commands, never from copied oracle runs.
    The six final zeros are not commands: assembler padding is checked elsewhere.
    """
    out=bytearray();bindings=[];coordinates={};definitions=[]
    for c in commands:
        name,args=check(c);p=len(out)
        symbol=header_label(c['offset']) if name=='HEADER' else label(c['offset'])
        coordinates[symbol]=p
        if symbol in proven_labels:definitions.append(dict(name=symbol,offset=p))
        if name=='HEADER':out.extend((args['channel'],args['priority']))
        elif name=='NOTE':out.extend((args['pitch'],args['ticks']))
        else:
            op,fields=SPECS[name];out.append(op)
            if fields==('target',):
                require(args['target'] in proven_labels,'pointer to an unproved stream')
                if len(out)%2:out.append(0)
                bindings.append(dict(offset=len(out),symbol=args['target'],type='HUNK_RELOC32',width=4,addend=0))
                out.extend(bytes(4))
            else:out.extend(args[k] for k in fields)
    return dict(code=bytes(out),coordinates=coordinates,definitions=definitions,fixups=bindings)


def source(member,commands,proven_labels):
    sem=encode(commands,proven_labels);prefix=member['prefix'];begin='_audio_'+prefix+'_begin';end='_audio_'+prefix+'_end'
    local=[d['name'] for d in sem['definitions']]
    external=sorted({b['symbol'] for b in sem['fixups']}-set(local))
    lines=macros()+['\tcseg']
    # One name per declaration keeps the complete symbol inventory explicit.
    lines+=['\tpublic '+n for n in [begin,end]+local+external]
    lines+=[begin+':']
    for c in commands:
        name,args=check(c);symbol=header_label(c['offset']) if name=='HEADER' else label(c['offset'])
        if symbol in proven_labels:lines.append(symbol+':')
        fields=('channel','priority') if name=='HEADER' else ('pitch','ticks') if name=='NOTE' else SPECS[name][1]
        lines.append('\tSC_'+name+(' '+','.join(str(args[k]) for k in fields) if fields else ''))
    return ('\n'.join(lines+[end+':','\tend',''])).encode('ascii')
