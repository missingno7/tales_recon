"""Strict proof for initialized static DATA owned by one C contribution.

The normal function verifier deliberately rejects candidate DATA/BSS.  This
module handles the narrower case where a curated manifest identifies one
contiguous initialized DATA contribution, and the compiler/linker naturally
places it after the independent harness DATA.  It never derives an ownership
claim from matching bytes alone and currently rejects data relocations and BSS
until their ownership can be proved separately.
"""
import copy
import json
from pathlib import Path

from analysis_support import ROOT, game
from common import FormatError, require, sha256
from function_compare import compare_function
from hunk import parse


def manifest_for(fid):
    path=ROOT/'recovery/data'/(fid+'.json')
    require(path.exists(),'no curated static-DATA ownership manifest for '+fid)
    manifest=json.loads(path.read_text())
    require(manifest.get('schema_version')==1 and manifest.get('id')==fid,
            'invalid static-DATA ownership manifest')
    return manifest,path


def object_data_size(path):
    raw=path.read_bytes()
    require(len(raw)>=22 and raw[:2] in (b'AJ',b'CJ'),'unsupported object dialect')
    return int.from_bytes(raw[14:18],'big'),int.from_bytes(raw[18:22],'big')


def linked_candidate_data(compiled,candidate_symbol=None):
    """Locate candidate initialized DATA in the natural linked root DATA hunk.

    The library can contribute root DATA before the harness.  A curated
    manifest may therefore name the candidate's linked data symbol instead of
    relying on object-order arithmetic that is not preserved by every link.
    """
    require(compiled['status']=='COMPILED','candidate did not compile')
    c=compiled['contribution'];directory=Path(compiled['directory']);prefix=compiled['prefix']
    require(prefix.startswith('t') and len(prefix)>1,'unrecognized compiler candidate prefix')
    candidate_data,candidate_bss=object_data_size(directory/(prefix+'.o'))
    harness_data,_=object_data_size(directory/('h'+prefix[1:]+'.o'))
    require(candidate_data==c['data_size'] and candidate_bss==c['bss_size'],
            'candidate object/data metadata differs')
    blob=(directory/(prefix+'.exe')).read_bytes();model=parse(blob)
    hunk=next((h for h in model['hunks'] if h['number']==1),None)
    require(hunk is not None and hunk['type']=='DATA','linked candidate has no root DATA hunk')
    start=harness_data
    if candidate_symbol:
        name='_'+candidate_symbol.lstrip('_')
        symbol=next((s for s in c['symbols'] if s['name']==name and s['hunk']==1),None)
        require(symbol is not None,'candidate static-DATA symbol is absent from linked root DATA')
        start=symbol['offset']
    require(start+candidate_data<=hunk['initialized_size'],'candidate DATA exceeds linked root DATA')
    base=hunk['content_offset']+start
    return dict(hunk=1,start=start,size=candidate_data,bss_size=candidate_bss,
                bytes=blob[base:base+candidate_data],model=model,blob=blob,
                symbol=candidate_symbol)


def static_data_proof(compiled,manifest,original,original_model):
    """Prove one manifest-declared DATA extent without consulting C source."""
    declared=manifest.get('original',{})
    for key in ('hunk','start','size','sha256'):
        require(key in declared,'static-DATA manifest lacks original '+key)
    candidate_symbol=manifest.get('candidate_symbol')
    require(isinstance(candidate_symbol,str) and candidate_symbol,
            'static-DATA manifest lacks candidate_symbol')
    require(declared['size']>0 and declared['start']>=0,'invalid static-DATA extent')
    original_hunk=next((h for h in original_model['hunks'] if h['number']==declared['hunk']),None)
    require(original_hunk is not None and original_hunk['type']=='DATA','static-DATA original is not DATA')
    require(declared['start']+declared['size']<=original_hunk['initialized_size'],
            'static-DATA original extent outside initialized DATA')
    begin=original_hunk['content_offset']+declared['start']
    expected=original[begin:begin+declared['size']]
    require(sha256(expected)==declared['sha256'],'static-DATA manifest hash differs from oracle')
    linked=linked_candidate_data(compiled,candidate_symbol)
    require(linked['size']==declared['size'],'candidate static-DATA length differs')
    require(linked['bss_size']==0,'candidate static-DATA also owns BSS')
    original_relocs=[r for r in original_model['relocations'] if r['source_hunk']==declared['hunk']
                     and r['source_offset']<declared['start']+declared['size']
                     and declared['start']<r['source_offset']+r['width']]
    actual_relocs=[r for r in linked['model']['relocations'] if r['source_hunk']==linked['hunk']
                   and r['source_offset']<linked['start']+linked['size']
                   and linked['start']<r['source_offset']+r['width']]
    require(not original_relocs and not actual_relocs,
            'static-DATA relocations require a stronger ownership proof')
    require(linked['bytes']==expected,'candidate static-DATA bytes differ')
    return dict(kind='INITIALIZED_STATIC_DATA',original=dict(declared),
                linked=dict(hunk=linked['hunk'],start=linked['start'],size=linked['size'],
                sha256=sha256(linked['bytes']),symbol=candidate_symbol),relocations=[])


def compare_owned_static_data(f,compiled,a4_bias):
    """Compare closed code plus a manifest-declared initialized DATA extent.

    Equality is intentionally intermediate: callers and module verification
    must still prove the complete natural source unit before promotion.
    """
    report=dict(verdict='BLOCKED',proof_level=None,expected_length=f['size'],actual_length=None,
                compiler=compiled['identity']['profile'],flags=compiled['identity']['flags'],
                cache_key=compiled['cache_key'],cache_hit=compiled['cache_hit'])
    if compiled['status']!='COMPILED':
        report.update(reason=compiled['status']);return report
    report['actual_length']=compiled['contribution']['code_size']
    try:
        manifest,path=manifest_for(f['id'])
        original,original_model,_=game()
        data_proof=static_data_proof(compiled,manifest,original,original_model)
        piece=copy.deepcopy(compiled)
        piece['contribution'].update(data_size=0,bss_size=0)
        code_report=compare_function(f,piece,a4_bias)
    except FormatError as exc:
        report.update(reason=str(exc));return report
    report.update(code_comparison=code_report,owned_static_data=data_proof,
                  manifest=path.relative_to(ROOT).as_posix(),manifest_sha256=sha256(path.read_bytes()))
    for key in ('mnemonic_similarity','prologue','epilogue','relocation_equal','relocation_proof',
                'relocation_issues','normalized_first_difference','first_differing_instruction'):
        if key in code_report:report[key]=code_report[key]
    if code_report['verdict']=='EQUAL':
        report.update(verdict='EQUAL',reason='FUNCTION_AND_INITIALIZED_STATIC_DATA_MATCH',
                      proof_level='FUNCTION_WITH_DATA_MATCH')
    else:
        report.update(verdict='DIFFER',reason='FUNCTION_CODE_OR_REFERENCE_DIFFERS')
    return report
