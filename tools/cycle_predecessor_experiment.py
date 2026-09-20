"""Measure an ov11 physical predecessor with its unresolved local callee.

This proves normal same-source binding for a layout contributor only.  It does
not turn either contributor into an independently verified function.
"""
import argparse
from difflib import SequenceMatcher
import json

from analysis_support import ROOT, decoder, game, instruction
from common import require, sha256, write_json
from compiler_oracle import compile_many


SOURCE = ROOT/'experiments/direct-recovery/ov11_F_583A-layout-v1.c'
MEMBERS = (('ov11_F_583A', 0x583a, 0x5962), ('ov11_F_5962', 0x5962, 0x59e6))


def decoded(data):
    md = decoder()
    rows = []
    cursor = 0
    while cursor < len(data):
        row = instruction(md, data, cursor)
        require(row is not None, 'undecodable code contribution')
        rows.append(dict(offset=cursor, size=row.size, raw=bytes(row.bytes).hex(),
                         mnemonic=row.mnemonic, operands=row.op_str))
        cursor += row.size
    return rows


def difference_kind(expected, actual):
    if 'a4' in expected['operands'] or 'a4' in actual['operands']:
        return 'A4_GLOBAL_LAYOUT'
    if expected['mnemonic'].startswith('b') and actual['mnemonic'].startswith('b'):
        return 'PC_RELATIVE_LAYOUT_DISPLACEMENT'
    return 'OTHER_CODEGEN_DIFFERENCE'


def build():
    source = SOURCE.read_text()
    compiled = compile_many([dict(source=source, profile='aztec36', target_node=9,
                                   entry_function='F_h11_583A')])[0]
    require(compiled['status'] == 'COMPILED', 'cycle predecessor did not compile')
    blob, model, _ = game()
    hunk = next(x for x in model['hunks'] if x['number'] == 11)
    original = blob[hunk['content_offset']:hunk['content_offset'] + hunk['initialized_size']]
    actual = bytes.fromhex(compiled['contribution']['code_hex'])
    cursor = 0
    members = []
    for fid, start, end in MEMBERS:
        expected = original[start:end]
        piece = actual[cursor:cursor+len(expected)]
        cursor += len(expected)
        left, right = decoded(expected), decoded(piece)
        require(len(left) == len(right), 'instruction count differs: '+fid)
        differences = [dict(offset=left_item['offset'], kind=difference_kind(left_item, right_item),
                            expected=left_item, actual=right_item)
                       for left_item, right_item in zip(left, right)
                       if left_item['raw'] != right_item['raw']]
        members.append(dict(id=fid, start=start, end=end, size=len(expected),
                            expected_sha256=sha256(expected), actual_sha256=sha256(piece),
                            mnemonic_similarity=SequenceMatcher(
                                None, [x['mnemonic'] for x in left], [x['mnemonic'] for x in right]).ratio(),
                            instruction_differences=differences, promotion_eligible=False))
    require(cursor == len(actual), 'unexpected predecessor code contribution length')
    return dict(
        schema_version=1, kind='ov11_cycle_predecessor_codegen_experiment', game_sha256=sha256(blob),
        source=dict(path=SOURCE.relative_to(ROOT).as_posix(), sha256=sha256(source.encode())),
        compiler=dict(profile='aztec36', cache_key=compiled['cache_key'], cache_hit=compiled['cache_hit'],
                      identity=compiled['identity']),
        comparison=dict(expected_length=cursor, actual_length=len(actual)), members=members,
        status='CODEGEN_SIMILAR_LAYOUT_ONLY', promotion_eligible=False,
        policy=('This receipt proves only ordinary same-source call binding for a future physical layout unit. '
                'It must not update source ownership, the recovery ledger, or recovered bytes.'))


if __name__ == '__main__':
    argparse.ArgumentParser(description=__doc__).parse_args()
    report = build()
    write_json(ROOT/'evidence/experiments/linker-cycle-predecessor.json', report)
    print(json.dumps(dict(status=report['status'], expected=report['comparison']['expected_length'],
                          actual=report['comparison']['actual_length'],
                          mechanisms=sorted({d['kind'] for member in report['members']
                                             for d in member['instruction_differences']}))))
