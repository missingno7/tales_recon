"""Validation-only complete executable accounting; never a reconstruction build.

Source-produced specimens are bound to accepted receipts. Only independently
proved address fields are normalized in the comparison representation. Every
other byte comes from explicitly labelled RAW_ORACLE_DEBT. This representation
cannot grant overlay, natural layout, or executable reconstruction proof.
"""
import argparse
import json
import re
import sys
from pathlib import Path
from collections import Counter

from analysis_support import ROOT, game
from common import FormatError, require, sha256, write_json
from hunk import parse, manx_overlay
from recovery_evidence import load_promotions,load_terminal_padding
from repo_paths import canonical_path
from library_a4 import load_library_a4

CATEGORIES = ('RECOVERED_C', 'RECOVERED_ASM', 'COMPILER_OWNED_DATA',
              'PINNED_RUNTIME', 'CLASSIFIED_PADDING', 'RAW_ORACLE_DEBT')
SPECIMENS = 'evidence/contributions/compiled.json'


def normalize(f, actual, comparison, a4_bias):
    """Rebase accepted reference fields, deriving values from site identities.

    No opcode, ordinary operand, literal, padding, or unknown byte is copied
    from the executable. This operates on a validation buffer only.
    """
    code = comparison.get('code_comparison', comparison)
    require(code['verdict']=='EQUAL' and code['relocation_equal'], 'unaccepted comparison')
    result = bytearray(actual)
    require(sha256(actual[:f['size']])==code['actual_sha256'], 'compiled specimen changed: '+f['id'])
    touched=set()
    for binding in code.get('relocation_proof', []):
        off=binding['offset'];kind=binding['kind'];identity=binding['identity']
        if kind=='HUNK_RELOCATION':
            rel=next((r for r in f['relocations'] if r['relative_offset']==off),None)
            require(rel and (identity['hunk'],identity['offset'])==(rel['target_hunk'],rel['addend_raw']),
                    'relocation identity differs')
            width=rel['width'];value=identity['offset']
        elif kind=='PC_RELATIVE_CALL_SYMBOL':
            width=binding['width'];field=1 if width==1 else 2
            site=f['start']+off-field
            call=next((c for c in f['direct_callees'] if c['site']==site),None)
            require(call and (identity['hunk'],identity['offset'])==(call['hunk'],call['offset']),
                    'PC call identity differs')
            value=call['offset']-(site+2)
            require(-(1<<(width*8-1))<=value<(1<<(width*8-1)), 'PC reference width changed')
        elif kind=='A4_D16_SYMBOL':
            width=2
            ins=next((i for i in f['instructions'] if i['offset']-f['start']<=off<
                      i['offset']-f['start']+i['size']),None)
            require(ins is not None and binding['expected']==[identity['hunk'],identity['offset']],
                    'A4 reference identity differs')
            fields=re.findall(r'(-?)\$([0-9a-f]+)\(a4\)',ins['operands'],re.I)
            require(len(fields) in (1,2),'ambiguous A4 field: '+f['id']+' '+ins['operands'])
            index=0
            if len(fields)==2:
                require(ins['mnemonic'].startswith('move') and ins['size']==6,'unsupported dual A4 instruction')
                index=(off-(ins['offset']-f['start'])-2)//2
                require(index in (0,1),'invalid dual A4 field')
            sign,number=fields[index];value=int(number,16)*(-1 if sign else 1)
            refs=[r for r in f['referenced_data'] if r['kind']=='A4_RELATIVE' and
                  r['instruction_offset']==ins['offset']]
            if refs:require(any(r['offset']==a4_bias+value for r in refs),'A4 site disagrees with static evidence')
        else:
            raise FormatError('unsupported normalization kind: '+kind)
        require(0<=off and off+width<=f['size'], 'normalization outside proven CODE')
        sites=set(range(off,off+width));require(not sites&touched,'overlapping reference fields');touched|=sites
        result[off:off+width]=(value & ((1<<(width*8))-1)).to_bytes(width,'big')
    require(sha256(result[:f['size']])==f['sha256']==code['normalized_sha256'],
            'reconstructed contribution mismatch: '+f['id'])
    if len(result)>f['size']:
        owned=comparison.get('owned_code_data')
        require(owned and sha256(result[f['size']:])==owned['actual_tail_sha256'], 'unproven compiler tail')
    return bytes(result)


def capture(root=ROOT):
    """Freeze only compiler-produced contribution bytes, not worker environments.

    Each specimen's raw hash is already in its accepted comparison. --refresh
    additionally rereads the hash-checked compiler cache and replays today's
    exact verifier. Missing caches fail with instructions to regenerate them.
    """
    from compiler_oracle import cached
    from function_compare import compare_function
    from check_unit import compare_unit, mechanical_name
    from owned_code_data import compare_owned_code_data
    blob,model,_=game();analysis=json.loads((root/'evidence/functions/ledger.json').read_text())
    load_promotions(root,blob,model,analysis)
    ledger=json.loads((root/'recovery/ledger.json').read_text());by={f['id']:f for f in analysis['functions']}
    entries={};replayed={}
    for fid,item in sorted(ledger['functions'].items()):
        proof=json.loads(canonical_path(root,item['proof']).read_text())
        key=proof['cache_key'];compiled=cached(key)
        require(compiled is not None, 'missing compiler specimen; regenerate pinned receipt: '+fid)
        require(compiled['identity']==proof['compiler'] and compiled['contribution']['object_sha256']==proof['object_hash'],
                'compiler identity differs: '+fid)
        c=compiled['contribution'];raw=bytes.fromhex(c['code_hex']);comparison=proof['comparison']
        unit_name=comparison.get('complete_unit_receipt')
        if unit_name:
            unit_path=canonical_path(root,unit_name);unit=json.loads(unit_path.read_text())
            members=[by[m['id']] for m in unit['ordered_members']]
            if unit_name not in replayed:
                names={m['id']:'recovered' if m['id']==unit['id'] else mechanical_name(m) for m in members}
                report=compare_unit(members,names,compiled,analysis['a4']['bias'],
                                    owned_code_data=any(t['id']==unit['id'] for t in unit.get('owned_code_tails',[])),
                                    allow_gaps=bool(unit.get('original_gaps')),
                                    source_text=(unit_path.parent/'unit.c').read_text(),natural=unit.get('natural_interval'))
                require(report['verdict']=='EQUAL','canonical unit replay failed: '+unit_name)
                replayed[unit_name]=report
            cursor=0
            for m in unit['ordered_members']:
                mr=next(r for r in unit['members'] if r['id']==m['id'])
                if m['id']==fid:
                    raw=raw[cursor:cursor+mr['actual_length']];break
                cursor+=mr['actual_length']
        else:
            replay=(compare_owned_code_data(by[fid],compiled,analysis['a4']['bias']) if
                    item['state']=='FUNCTION_WITH_DATA_MATCH' else compare_function(by[fid],compiled,analysis['a4']['bias']))
            require(replay['verdict']=='EQUAL','canonical replay failed: '+fid)
        normalize(by[fid],raw,comparison,analysis['a4']['bias'])
        entries[fid]=dict(proof_sha256=item['proof_sha256'],source_sha256=item['source_sha256'],
                          cache_key=key,actual_hex=raw.hex(),actual_sha256=sha256(raw))
    # Relocation-free library specimens: retain the linked producing bytes,
    # verifying them against pinned library/object receipts, never the oracle.
    runtime=[];seen=set()
    for name in ('runtime-matches.json','runtime-arithmetic.json'):
        receipt_path=root/'evidence/experiments'/name;receipt=json.loads(receipt_path.read_text())
        jobs=[p for p in (root/'build/worker-jobs').glob('*/result.json')
              if sha256(p.read_bytes())==receipt['job_receipt_sha256']]
        require(len(jobs)==1,'missing or ambiguous runtime job receipt: '+name)
        job=json.loads(jobs[0].read_text());work=jobs[0].parent/'sys/work'
        rows=receipt.get('contributions',receipt.get('objects',[]))
        for row in rows:
            matches=[row['original']] if 'original' in row else row['matches']
            if len(matches)!=1:continue
            region=matches[0];identity=(region['hunk'],region['offset'],region['size'])
            if identity in seen:continue
            seen.add(identity)
            objs=[a for a in job['artifacts'] if a['sha256']==row['object_sha256']]
            require(len(objs)==1,'runtime producing object missing')
            obj=objs[0];require(sha256((work/obj['path']).read_bytes())==obj['sha256'],'runtime object changed')
            library=receipt.get('candidate_library_sha256',row.get('library_sha256'))
            library_paths=[root/'toolchain/installed/aztec-3.6a/SYS1/lib/c.lib',
                           root/'toolchain/installed/aztec-5.0a/Aztec2/lib/c16.lib']
            require(any(p.is_file() and sha256(p.read_bytes())==library for p in library_paths),'runtime library changed')
            candidates=[]
            for artifact in job['artifacts']:
                path=work/artifact['path']
                if artifact['path'] in (Path(obj['path']).stem,Path(obj['path']).stem+'-linked') and path.is_file():
                    require(sha256(path.read_bytes())==artifact['sha256'],'runtime link changed')
                    linked=path.read_bytes();lm=parse(linked)
                    hs=[h for h in lm['hunks'] if h['initialized_size']]
                    require(len(hs)==1 and hs[0]['type']=='CODE' and not lm['relocations'],'unsupported runtime link')
                    h=hs[0];produced=linked[h['content_offset']:h['content_offset']+region['size']]
                    if sha256(produced)==row['code_sha256']:candidates.append(produced)
            require(len(candidates)==1,'runtime linked specimen missing')
            runtime.append(dict(id='runtime_'+Path(obj['path']).stem,**region,actual_hex=candidates[0].hex(),
                                actual_sha256=row['code_sha256'],library_sha256=library,object_sha256=obj['sha256'],
                                receipt=receipt_path.relative_to(root).as_posix(),receipt_sha256=sha256(receipt_path.read_bytes())))
    return dict(schema_version=1,game_sha256=sha256(blob),functions=entries,runtime=runtime,
                policy='Compiler-produced validation specimens; acceptance authority remains recovery/ledger.json and its receipts.')


def account(blob, model, contributions):
    """Pure interval accounting, with strict ownership and relocation sets."""
    hunks={h['number']:h for h in model['hunks']};by_hunk={n:[] for n in hunks}
    seen=set()
    for c in contributions:
        require(c['id'] not in seen,'duplicate contribution identity');seen.add(c['id'])
        h=hunks.get(c['hunk']);require(h is not None,'contribution outside hunk topology')
        start=c['start'];payload=c['bytes'];end=start+len(payload)
        require(c['category'] in CATEGORIES[:-1] and 0<=start<end<=h['initialized_size'],
                'contribution mapped outside proven region: '+c['id'])
        require(end==c['end'],'contribution length differs from proven region')
        require(payload==blob[h['content_offset']+start:h['content_offset']+end],
                'reconstructed contribution mismatch: '+c['id'])
        expected=[{k:r[k] for k in ('source_offset','target_hunk','type','width','addend_raw')}
                  for r in model['relocations'] if r['source_hunk']==c['hunk'] and start<=r['source_offset']<end]
        require(all(r['source_offset']+r['width']<=end for r in expected),'relocation crosses contribution boundary')
        require(c.get('relocations',[])==expected,'unexpected or missing contribution relocations: '+c['id'])
        by_hunk[c['hunk']].append(c)
    ranges=[];summary={};parts=[]
    for n,h in hunks.items():
        counts=Counter({k:0 for k in CATEGORIES});cursor=0
        for c in sorted(by_hunk[n],key=lambda x:x['start']):
            require(cursor<=c['start'],'overlapping ownership in hunk '+str(n))
            if cursor<c['start']:ranges.append(dict(hunk=n,start=cursor,end=c['start'],category='RAW_ORACLE_DEBT'))
            ranges.append({k:c[k] for k in ('id','hunk','start','end','category')});cursor=c['end']
        if cursor<h['initialized_size']:ranges.append(dict(hunk=n,start=cursor,end=h['initialized_size'],category='RAW_ORACLE_DEBT'))
        for row in ranges:
            if row['hunk']==n:counts[row['category']]+=row['end']-row['start']
        require(sum(counts.values())==h['initialized_size'],'missing initialized bytes')
        summary.setdefault(h['node'],Counter({k:0 for k in CATEGORIES})).update(counts)
    # Complete file representation: structural records remain explicitly debt.
    file_ranges=[]
    for row in ranges:
        h=hunks[row['hunk']];file_ranges.append(dict(row,file_start=h['content_offset']+row['start'],file_end=h['content_offset']+row['end']))
    lookup={c['id']:c for c in contributions};cursor=0;structural=0
    for row in sorted(file_ranges,key=lambda x:x['file_start']):
        if cursor<row['file_start']:
            structural+=row['file_start']-cursor;parts.append(blob[cursor:row['file_start']])
        parts.append(lookup[row['id']]['bytes'] if row.get('id') else blob[row['file_start']:row['file_end']])
        cursor=row['file_end']
    structural+=len(blob)-cursor;parts.append(blob[cursor:]);output=b''.join(parts)
    require(output==blob,'hybrid executable mismatch')
    require(parse(output)==model,'hybrid HUNK/relocation structure differs')
    require(manx_overlay(parse(output),output)==manx_overlay(model,blob),'hybrid overlay topology differs')
    totals=Counter({k:0 for k in CATEGORIES})
    for counts in summary.values():totals.update(counts)
    totals.update(file_size=len(blob),initialized_bytes=sum(h['initialized_size'] for h in model['hunks']),
                  structural_RAW_ORACLE_DEBT=structural,
                  file_RAW_ORACLE_DEBT=totals['RAW_ORACLE_DEBT']+structural,overlap=0,unaccounted=0)
    return output,dict(schema_version=1,game_sha256=sha256(blob),output_sha256=sha256(output),
                       validation_only=True,reconstruction_proof_level=None,
                       topology=dict(hunks=len(hunks),relocations=len(model['relocations']),nodes=[n['id'] for n in model['nodes']]),
                       totals=dict(totals),by_overlay={n:dict(c,overlap=0,unexplained=0) for n,c in summary.items()},
                       ranges=ranges,zero_fill_debt=sum(h['zero_fill_size'] for h in model['hunks']),
                       policy='RAW_ORACLE_DEBT never counts as reconstructed. No natural layout or closure proof is granted.')


def build(root=ROOT):
    blob,model,_=game();analysis=json.loads((root/'evidence/functions/ledger.json').read_text())
    promoted=load_promotions(root,blob,model,analysis);by={f['id']:f for f in analysis['functions']}
    specimens=json.loads(canonical_path(root,SPECIMENS).read_text());require(specimens['game_sha256']==sha256(blob),'specimens belong to another oracle')
    ledger=json.loads((root/'recovery/ledger.json').read_text());contributions=[]
    require(set(specimens['functions'])==set(ledger['functions']),'compiled specimens do not name precisely canonical source')
    for p in promoted:
        fid=p['id'];item=ledger['functions'][fid];s=specimens['functions'][fid]
        require(s['proof_sha256']==item['proof_sha256'] and s['source_sha256']==item['source_sha256'],'specimen proof binding changed')
        proof=json.loads(canonical_path(root,item['proof']).read_text());actual=bytes.fromhex(s['actual_hex'])
        raw=normalize(by[fid],actual,proof['comparison'],analysis['a4']['bias'])
        rels=[{k:r[k] for k in ('source_offset','target_hunk','type','width','addend_raw')}
              for r in model['relocations'] if r['source_hunk']==p['hunk'] and p['start']<=r['source_offset']<p['end']]
        # load_promotions and normalize check each source relocation against
        # independently resolved identities before this accounting projection.
        contributions.append(dict(id=fid,hunk=p['hunk'],start=p['start'],end=p['end'],category='RECOVERED_C',bytes=raw[:p['size']],relocations=rels))
        if len(raw)>p['size']:
            contributions.append(dict(id=fid+'_tail',hunk=p['hunk'],start=p['end'],end=p['start']+len(raw),category='COMPILER_OWNED_DATA',bytes=raw[p['size']:]))
    for s in specimens['runtime']:
        receipt_bytes=canonical_path(root,s['receipt']).read_bytes()
        require(sha256(receipt_bytes)==s['receipt_sha256'],'runtime receipt changed')
        receipt=json.loads(receipt_bytes)
        require(receipt['game_sha256']==sha256(blob),'runtime receipt belongs to another oracle')
        matches=[]
        for row in receipt.get('objects',[]):
            if row['object_sha256']==s['object_sha256'] and row['code_sha256']==s['actual_sha256']:
                if receipt['candidate_library_sha256']==s['library_sha256']:
                    matches.extend(row['matches'])
        for row in receipt.get('contributions',[]):
            if (row['object_sha256']==s['object_sha256'] and row['code_sha256']==s['actual_sha256']
                    and row['library_sha256']==s['library_sha256']):matches.append(row['original'])
        require(dict(hunk=s['hunk'],offset=s['offset'],size=s['size']) in matches,
                'runtime specimen region/identity is not independently proved')
        raw=bytes.fromhex(s['actual_hex']);require(sha256(raw)==s['actual_sha256'],'runtime specimen changed')
        contributions.append(dict(id=s['id'],hunk=s['hunk'],start=s['offset'],end=s['offset']+s['size'],bytes=raw,category='PINNED_RUNTIME'))
    contributions.extend(load_terminal_padding(root,blob,model,analysis,promoted,ledger))
    contributions.extend(load_library_a4(root,blob,model,analysis,promoted,ledger))
    return account(blob,model,contributions)


def human(report):
    lines=['# Whole-image validation accounting','',report['policy'],'',
           '| Node | C | ASM | Compiler data | Runtime | Padding | RAW_ORACLE_DEBT |',
           '| --- | ---: | ---: | ---: | ---: | ---: | ---: |']
    for node,c in report['by_overlay'].items():lines.append('| '+node+' | '+' | '.join(str(c[k]) for k in CATEGORIES)+' |')
    t=report['totals'];lines+=['',f"File: {t['file_size']:,} bytes. Initialized content: {t['initialized_bytes']:,} bytes.",
        f"File structure debt: {t['structural_RAW_ORACLE_DEBT']:,}; total file RAW_ORACLE_DEBT: {t['file_RAW_ORACLE_DEBT']:,}.",
        f"Allocation-only zero fill remains separate debt: {report['zero_fill_debt']:,} bytes.",
        'Overlap: 0. Unaccounted file bytes: 0. All 1,445 relocations and the complete HUNK/overlay topology preserved.',
        '', 'This is an oracle-assisted validation representation. It is not an independently linked executable.']
    return '\n'.join(lines)+'\n'


def closure_inventory(report, analysis, ledger, model, node='ov04'):
    """Current campaign inventory from existing authorities; never closure proof."""
    hunks={h['number'] for h in model['hunks'] if h['node']==node}
    owned={fid for fid,item in ledger['functions'].items() if item['evidence_extent']['hunk'] in hunks}
    pending=[{k:f[k] for k in ('id','start','end','size','extent_status')}
             for f in analysis['functions'] if f['hunk'] in hunks
             and f['extent_status']=='CLOSED_CFG' and f['id'] not in owned]
    return dict(schema_version=1, node=node, closure_proved=False,
                initialized_bytes=sum(h['initialized_size'] for h in model['hunks'] if h['number'] in hunks),
                recovered_functions=sorted(owned), remaining_functions=pending,
                debt_ranges=[r for r in report['ranges'] if r['hunk'] in hunks and r['category']=='RAW_ORACLE_DEBT'],
                relocation_obligations=[r for r in model['relocations'] if r['source_hunk'] in hunks])


def main():
    ap=argparse.ArgumentParser(description=__doc__);ap.add_argument('--refresh',action='store_true');ap.add_argument('--write',action='store_true');ap.add_argument('--check',action='store_true');a=ap.parse_args()
    if a.refresh:write_json(ROOT/SPECIMENS,capture())
    output,report=build();text=human(report)
    _,model,_=game()
    closure=closure_inventory(report,json.loads((ROOT/'evidence/functions/ledger.json').read_text()),
                              json.loads((ROOT/'recovery/ledger.json').read_text()),model)
    closure_path=ROOT/'evidence/closure/ov04.json'
    if a.write:
        write_json(ROOT/'evidence/hybrid/accounting.json',report)
        write_json(closure_path,closure)
        (ROOT/'docs/ACCOUNTING.md').write_text(text,encoding='ascii',newline='\n')
        dest=ROOT/'build/hybrid';dest.mkdir(parents=True,exist_ok=True);(dest/'validation-only.bin').write_bytes(output)
    if a.check:
        require(json.loads((ROOT/'evidence/hybrid/accounting.json').read_text())==report,'stale accounting report')
        require((ROOT/'docs/ACCOUNTING.md').read_text()==text,'stale human accounting report')
        require(json.loads(closure_path.read_text())==closure,'stale closure inventory')
    print(text)


if __name__=='__main__':
    try:main()
    except (FormatError,OSError,ValueError,KeyError) as e:print('BLOCKED: '+str(e),file=sys.stderr);sys.exit(1)
