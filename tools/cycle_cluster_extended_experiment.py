"""Measure the ov11 cycle cluster with its two forward callees in one source unit.

This is a source-layout experiment.  It explains how the historical compiler
selects shorter local calls in a compact unit; it is never a function-match
receipt and cannot promote any source ownership.
"""
import argparse
from difflib import SequenceMatcher
import json

from analysis_support import ROOT, decoder, game, instruction
from common import require, sha256, write_json
from compiler_oracle import compile_many


SOURCE = ROOT / 'experiments/direct-recovery/ov11_cycle_cluster-v2.c'
# The compact unit shortens the forward F5C42 -> F4696 call from JSR.d16(PC)
# to BSR.b.  Every other source contribution retains its original size.
MEMBERS = (
    ('ov11_F_4610', 0x4610, 0x4696, 134),
    ('ov11_F_5962', 0x5962, 0x59e6, 132),
    ('ov11_LATENT_59E6', 0x59e6, 0x5a12, 44),
    ('ov11_F_5A12', 0x5a12, 0x5a62, 80),
    ('ov11_F_5A62', 0x5a62, 0x5ab0, 78),
    ('ov11_F_5AB0', 0x5ab0, 0x5bc4, 276),
    ('ov11_F_5BC4', 0x5bc4, 0x5c1a, 86),
    ('ov11_F_5C1A', 0x5c1a, 0x5c42, 40),
    ('ov11_F_5C42', 0x5c42, 0x5cea, 166),
    ('ov11_LATENT_5CEA', 0x5cea, 0x5d14, 42),
    ('ov11_F_4696', 0x4696, 0x4790, 250),
    ('ov11_F_66FE', 0x66fe, 0x673e, 64),
)


def decoded(data):
    md = decoder()
    result = []
    cursor = 0
    while cursor < len(data):
        row = instruction(md, data, cursor)
        require(row is not None, 'undecodable code contribution')
        result.append(dict(offset=cursor, size=row.size, raw=bytes(row.bytes).hex(),
                           mnemonic=row.mnemonic, operands=row.op_str))
        cursor += row.size
    return result


def mechanism(expected, actual):
    if expected['mnemonic'] == 'jsr' and 'pc' in expected['operands']:
        if actual['mnemonic'].startswith('bsr'):
            return 'COMPACT_FORWARD_CALL_ENCODING'
        if 'pc' in actual['operands']:
            return 'PC_RELATIVE_LAYOUT_DISPLACEMENT'
        return 'FORWARD_EXTERNAL_CALL_BINDING'
    if (expected['mnemonic'].startswith('b') and actual['mnemonic'].startswith('b')):
        return 'PC_RELATIVE_LAYOUT_DISPLACEMENT'
    if 'a4' in expected['operands'] or 'a4' in actual['operands']:
        return 'A4_GLOBAL_LAYOUT'
    return 'OTHER_CODEGEN_DIFFERENCE'


def build():
    source = SOURCE.read_text()
    compiled = compile_many([dict(source=source, profile='aztec36', target_node=9)])[0]
    require(compiled['status'] == 'COMPILED', 'extended cycle cluster did not compile')
    blob, model, _ = game()
    hunk = next(x for x in model['hunks'] if x['number'] == 11)
    original = blob[hunk['content_offset']:hunk['content_offset'] + hunk['initialized_size']]
    actual = bytes.fromhex(compiled['contribution']['code_hex'])
    cursor = 0
    members = []
    for fid, start, end, actual_size in MEMBERS:
        expected = original[start:end]
        piece = actual[cursor:cursor + actual_size]
        cursor += actual_size
        left, right = decoded(expected), decoded(piece)
        require(len(left) == len(right), 'instruction count differs: ' + fid)
        differences = []
        for expected_instruction, actual_instruction in zip(left, right):
            if expected_instruction['raw'] != actual_instruction['raw']:
                differences.append(dict(offset=expected_instruction['offset'],
                                        kind=mechanism(expected_instruction, actual_instruction),
                                        expected=expected_instruction, actual=actual_instruction))
        members.append(dict(
            id=fid, start=start, end=end, expected_size=len(expected), actual_size=len(piece),
            size_delta=len(piece)-len(expected), expected_sha256=sha256(expected),
            actual_sha256=sha256(piece),
            mnemonic_similarity=SequenceMatcher(
                None, [x['mnemonic'] for x in left], [x['mnemonic'] for x in right]).ratio(),
            instruction_differences=differences, promotion_eligible=False))
    require(cursor == len(actual), 'unexpected extended cluster code contribution length')
    return dict(
        schema_version=1, kind='ov11_cycle_cluster_extended_codegen_experiment',
        game_sha256=sha256(blob),
        source=dict(path=SOURCE.relative_to(ROOT).as_posix(), sha256=sha256(source.encode())),
        compiler=dict(profile='aztec36', cache_key=compiled['cache_key'], cache_hit=compiled['cache_hit'],
                      identity=compiled['identity']),
        comparison=dict(expected_length=sum(end-start for _, start, end, _ in MEMBERS),
                        actual_length=len(actual),
                        size_delta=len(actual)-sum(end-start for _, start, end, _ in MEMBERS)),
        members=members, status='CODEGEN_SIMILAR_LAYOUT_ONLY', promotion_eligible=False,
        policy=('This receipt maps normal source-layout behavior only. It must not update the function census, '
                'recovery ledger, source ownership, or recovered bytes.'))


if __name__ == '__main__':
    argparse.ArgumentParser(description=__doc__).parse_args()
    report = build()
    write_json(ROOT/'evidence/experiments/linker-cycle-cluster-extended.json', report)
    print(json.dumps(dict(status=report['status'], expected=report['comparison']['expected_length'],
                          actual=report['comparison']['actual_length'],
                          mechanisms=sorted({d['kind'] for member in report['members']
                                             for d in member['instruction_differences']}))))
