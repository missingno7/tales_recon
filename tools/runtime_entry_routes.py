"""Separate exact library-entry guidance; legacy runtime ledgers stay unchanged.

Pinned provider-report digests serve advisory entry lookup, like the legacy
ledgers. Census/accounting independently replay the complete producer graph;
``audit=True`` also replays every provider when checking the guidance itself.
Guidance grants no code, source, storage, or aggregate acceptance.
"""
import json,re
from common import require,sha256,json_bytes
from repo_paths import canonical_path

INPUT='evidence/contributions/runtime-library-routes.json'
INPUT_DIGEST='2ac89d07794206820a14ca6da89af7b4d32839cc3727d1be0da8d3b94a816628'


def export(proof,path,digest):
    require(proof['status']=='COMPLETE_RUNTIME_CODE_MATCH','runtime routes need a complete proof')
    rows={}
    for c in proof['contributions']:
        ex=c['original'];size=c['size']
        require(ex['size']==size and size>0,'runtime route complete extent differs')
        for entry in c['entries']:
            require(0<=entry['offset']<size,'runtime route entry outside complete member')
            if entry.get('abi','C_STACK')!='C_STACK' or not re.fullmatch(r'_[A-Za-z_][A-Za-z_0-9]*',entry['name']):continue
            key=(ex['hunk'],ex['offset']+entry['offset'])
            require(key not in rows,'runtime route duplicate exact entry')
            rows[key]=dict(state='MATCHED_RUNTIME_CONTRIBUTION',kind='LIBRARY_MEMBER',symbol=entry['name'],
                member=c['member'],extent=dict(ex),profiles=[c['profile']],evidence=path,evidence_sha256=digest,
                source_contract='Call the exact complete pinned library entry; no interior or private register-ABI routing.')
    return rows


def load(root,game_sha256,*,document=None,original=None,audit=False):
    path=canonical_path(root,INPUT)
    if document is None:
        if not path.exists():return {}
        document=json.loads(path.read_text())
    require(sha256(json_bytes(document))==INPUT_DIGEST,'runtime route curated providers changed')
    from evidence_snapshot import memoized
    def derive():
        nonlocal original
        if audit and original is None:
            from census import advisory_image
            from analysis_support import game
            with advisory_image():original=game()[:2]
        if original is not None:require(sha256(original[0])==game_sha256,'runtime route executable differs')
        import runtime_natural_members as natural
        import runtime_tail_members as tail
        import runtime_glue_members as glue
        import runtime_stdio_ffp_members as extra
        import runtime_root_members as root_members
        verifiers={'root':root_members.verify,'natural':natural.verify,'tail':tail.verify,'glue':glue.verify,'stdio_ffp':extra.verify}
        rows={}
        for provider in document['providers']:
            raw=canonical_path(root,provider['path']).read_bytes()
            require(sha256(raw)==provider['sha256'],'runtime route retained proof changed')
            proof=json.loads(raw)
            require(proof['game_sha256']==game_sha256,'runtime route proof belongs to another executable')
            if audit:
                replay=verifiers[provider['verifier']](root,original=original)
                require(proof==json.loads(json.dumps(replay)),'runtime route proof does not rederive')
            for key,row in export(proof,provider['path'],sha256(raw)).items():
                require(key not in rows or (rows[key]['symbol']==row['symbol'] and rows[key]['extent']==row['extent']),
                        'conflicting exact runtime routes')
                rows.setdefault(key,row)
        return rows
    return memoized(root,'runtime-entry-routes',game_sha256+';'+INPUT_DIGEST+';audit='+str(audit),derive,strict=True)
