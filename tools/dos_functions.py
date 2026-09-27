"""Conservative recursive x86/16 overlay function candidates for DOS comparison.

Seeds are overlay entry zero and conventional BP-frame prologues. Prologues are
heuristic entry evidence, not ownership proof. Branches remain inside one
candidate; calls only record possible new entries. This census makes no Amiga
reconstruction claim.
"""
import argparse
import json
from pathlib import Path

from dos_capstone import capstone
from capstone import x86_const as X

from dos_structure import EXE, analyze


def decoder():
    md = capstone.Cs(capstone.CS_ARCH_X86, capstone.CS_MODE_16)
    md.detail = True
    return md


def immediate_targets(ins):
    return [op.imm for op in ins.operands if op.type == X.X86_OP_IMM]


def candidate(body, start, seeds, md):
    todo = [start]
    seen = {}
    branches = set()
    calls = []
    indirect = []
    exits = set()
    issues = []
    while todo:
        at = todo.pop()
        while 0 <= at < len(body) and at not in seen:
            if at != start and at in seeds:
                issues.append(dict(kind='OTHER_ENTRY', offset=at))
                break
            found = list(md.disasm(body[at:at+15], at, count=1))
            if not found:
                issues.append(dict(kind='UNDECODABLE', offset=at))
                break
            ins = found[0]
            seen[at] = ins
            following = at + ins.size
            name = ins.mnemonic
            if name in ('ret', 'retf', 'iret'):
                exits.add(following)
                break
            if ins.group(capstone.CS_GRP_CALL):
                targets = immediate_targets(ins)
                if len(targets) == 1 and 0 <= targets[0] < len(body):
                    calls.append(dict(site=at, kind='DIRECT_NEAR', target=targets[0]))
                elif len(targets) == 2:
                    calls.append(dict(site=at, kind='DIRECT_FAR',
                                      segment=targets[0], offset=targets[1]))
                else:
                    calls.append(dict(site=at, kind='INDIRECT'))
                    indirect.append(at)
                at = following
                continue
            if ins.group(capstone.CS_GRP_JUMP):
                targets = immediate_targets(ins)
                if len(targets) != 1 or not 0 <= targets[0] < len(body):
                    indirect.append(at)
                    issues.append(dict(kind='UNKNOWN_JUMP', offset=at))
                    break
                target = targets[0]
                branches.add(target)
                todo.append(target)
                if name == 'jmp' or name == 'ljmp':
                    break
                at = following
                continue
            at = following
        else:
            if at >= len(body):
                issues.append(dict(kind='FELL_OUT_OF_IMAGE', offset=at))
    end = max((at+ins.size for at, ins in seen.items()), default=start)
    return dict(start=start, end=end, span_bytes=end-start,
                entry_evidence='OVERLAY_ENTRY' if start == 0 else 'BP_FRAME_PATTERN',
                extent='CLOSED_CFG' if seen and exits and not issues else 'UNCERTAIN',
                decoded_instruction_count=len(seen), decoded_bytes=sum(i.size for i in seen.values()),
                mnemonics=[ins.mnemonic for _, ins in sorted(seen.items())],
                exits=sorted(exits), branches=sorted(branches), calls=calls,
                indirect_sites=sorted(set(indirect)), issues=issues,
                prologue=body[start:start+min(12, len(body)-start)].hex())


def census(data):
    _, structure = analyze(data)
    md = decoder()
    overlays = []
    for item in structure['overlays']:
        body = data[item['file_start']+item['header_bytes']:item['file_end']]
        seeds = {0}
        pos = 0
        while True:
            pos = body.find(b'\x55\x8b\xec', pos)
            if pos < 0:
                break
            seeds.add(pos)
            pos += 1
        funcs = [candidate(body, start, seeds, md) for start in sorted(seeds)]
        for f in funcs:
            f['id'] = 'dos_ov%02d_F_%04X' % (item['overlay_number'], f['start'])
        overlays.append(dict(overlay_number=item['overlay_number'],
                             load_bytes=len(body), candidate_count=len(funcs),
                             closed_cfg=sum(f['extent'] == 'CLOSED_CFG' for f in funcs),
                             candidates=funcs))
    return dict(schema_version=1, role='DOS_CANDIDATE_DISCOVERY_ONLY',
                executable_sha256=structure['executable_sha256'],
                decoder='Capstone '+capstone.__version__,
                method='entry zero plus BP-frame patterns; recursive traversal only',
                warning='Neither a prologue nor CLOSED_CFG proves source ownership or a complete translation unit.',
                overlays=overlays)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--exe', type=Path, default=EXE)
    parser.add_argument('--write', type=Path)
    args = parser.parse_args()
    result = census(args.exe.read_bytes())
    if args.write:
        args.write.parent.mkdir(parents=True, exist_ok=True)
        args.write.write_text(json.dumps(result, indent=2)+'\n')
    for item in result['overlays']:
        print('dos_ov%02d %d-byte load: %d candidates, %d closed CFG' %
              (item['overlay_number'], item['load_bytes'], item['candidate_count'],
               item['closed_cfg']))


if __name__ == '__main__':
    main()
