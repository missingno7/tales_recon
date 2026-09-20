"""Measure ordinary source-object ordering for the ov11 reciprocal-call cluster.

The compact layout experiment defines F_h11_4696 after F_h11_5C42, so Manx
relaxes that forward call to BSR.B.  This experiment places the real callee in
an earlier ordinary C object, keeps the later F_h11_66FE definition after the
caller, and compares only the bounded F_h11_5C42 contribution.  It is a
non-promoting linker-mechanism receipt.
"""
import argparse
from difflib import SequenceMatcher
import json

from analysis_support import ROOT, decoder, game, instruction
from common import require, sha256, write_json
from compiler_oracle import compile_many


SOURCE = ROOT / 'experiments/direct-recovery/ov11_cycle_cluster-v2.c'
TARGET = dict(id='ov11_F_5C42', start=0x5c42, end=0x5cea,
              symbol='_F_h11_5C42')


def source_objects(source):
    """Split existing experimental C only at complete function definitions."""
    first = source.index('F_h11_4610(')
    # Match definitions, not the preamble's compatible extern declarations.
    f4696 = source.index('\nF_h11_4696(') + 1
    f66fe = source.index('\nF_h11_66FE(') + 1
    preamble = source[:first]
    return [
        dict(label='earlier', source='extern int G_h01_8A3E;\n' + source[f4696:f66fe]),
        dict(label='cluster', source=preamble + source[first:f4696]),
        dict(label='later', source=source[f66fe:]),
    ]


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
    if expected['mnemonic'] == 'jsr' and 'pc' in expected['operands']:
        if actual['mnemonic'].startswith('bsr'):
            return 'FORWARD_CALL_RELAXATION'
        if 'pc' in actual['operands']:
            return 'PC_RELATIVE_LAYOUT_DISPLACEMENT'
        return 'EXTERNAL_CALL_BINDING'
    if 'a4' in expected['operands'] or 'a4' in actual['operands']:
        return 'A4_GLOBAL_LAYOUT'
    if expected['mnemonic'].startswith('b') and actual['mnemonic'].startswith('b'):
        return 'PC_RELATIVE_LAYOUT_DISPLACEMENT'
    return 'OTHER_CODEGEN_DIFFERENCE'


def build():
    source = SOURCE.read_text()
    objects = source_objects(source)
    combined = '\n'.join(x['source'] for x in objects)
    compiled = compile_many([dict(source=combined, objects=objects, profile='aztec36',
                                  target_node=9, entry_function='recovered',
                                  local_functions=('F_h11_4696', 'F_h11_66FE'))])[0]
    require(compiled['status'] == 'COMPILED', 'object-order experiment did not compile')
    symbols = {x['name']: x['offset'] for x in compiled['contribution']['symbols']}
    require(TARGET['symbol'] in symbols, 'missing target symbol')
    actual_all = bytes.fromhex(compiled['contribution']['code_hex'])
    start = symbols[TARGET['symbol']]
    actual = actual_all[start:start + TARGET['end'] - TARGET['start']]
    blob, model, _ = game()
    hunk = next(x for x in model['hunks'] if x['number'] == 11)
    expected = blob[hunk['content_offset'] + TARGET['start']:
                    hunk['content_offset'] + TARGET['end']]
    left, right = decoded(expected), decoded(actual)
    require(len(left) == len(right), 'target instruction count differs')
    differences = [dict(offset=a['offset'], kind=difference_kind(a, b),
                        expected=a, actual=b)
                   for a, b in zip(left, right) if a['raw'] != b['raw']]
    return dict(
        schema_version=1, kind='ov11_cycle_object_order_codegen_experiment',
        game_sha256=sha256(blob),
        source=dict(path=SOURCE.relative_to(ROOT).as_posix(), sha256=sha256(source.encode())),
        objects=[dict(label=x['label'], source_sha256=sha256(x['source'].encode())) for x in objects],
        compiler=dict(profile='aztec36', cache_key=compiled['cache_key'],
                      cache_hit=compiled['cache_hit'], identity=compiled['identity']),
        target=dict(**TARGET, expected_length=len(expected), actual_length=len(actual),
                    expected_sha256=sha256(expected), actual_sha256=sha256(actual),
                    mnemonic_similarity=SequenceMatcher(
                        None, [x['mnemonic'] for x in left], [x['mnemonic'] for x in right]).ratio(),
                    instruction_differences=differences),
        status='CODEGEN_SIMILAR_LAYOUT_ONLY', promotion_eligible=False,
        policy=('This receipt tests ordinary source-object ordering only. It must not update the function census, '
                'recovery ledger, source ownership, or recovered bytes.'))


if __name__ == '__main__':
    argparse.ArgumentParser(description=__doc__).parse_args()
    report = build()
    write_json(ROOT / 'evidence/experiments/linker-cycle-object-order.json', report)
    print(json.dumps(dict(status=report['status'], expected=report['target']['expected_length'],
                          actual=report['target']['actual_length'],
                          mechanisms=sorted({x['kind'] for x in report['target']['instruction_differences']}))))
