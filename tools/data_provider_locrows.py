"""Independent fixed-archive selector domain for resident option WORD rows."""
from names import to_mechanical
import importlib.util,json,re,sys
from pathlib import Path
from common import require,sha256
from repo_paths import canonical_path,active_files
IDS={'ov04_F_000C','ov04_F_0104','resident_F_01BA','ov09_F_0000','ov09_F_18D0'}

def evidence_paths(root):
    return ['evidence/assets.json','evidence/fixture-lock.json','formats/decode.py']+[p.relative_to(root).as_posix() for p in sorted(active_files(root/'assets','.adf'))]

def selector_rows(entries):
    rows=[]
    for i,entry in enumerate(entries):
        require(entry.kind==4,'location selector requires decoded kind4 text')
        first=entry.record_output.splitlines()[0].decode('ascii');require(re.fullmatch(r'\s*\d+\s+\d+\s+\d+\s+\d+\s*',first),'four independent location header WORD values')
        values=list(map(int,first.split()));require(all(0<=v<=65535 for v in values),'serialized WORD range')
        if values[2]&15==4:rows.append(dict(record=i,selector=values[2],argument=values[2]>>4))
    return rows


def selectors(root):
    path=canonical_path(root,'formats/decode.py');name='_tales_provider_format_decoder'
    if name not in sys.modules:
        spec=importlib.util.spec_from_file_location(name,path);module=importlib.util.module_from_spec(spec);sys.modules[name]=module;spec.loader.exec_module(module)
    module=sys.modules[name];inventory=json.loads(canonical_path(root,'evidence/assets.json').read_bytes());expected=next(x for x in inventory['files'] if x['path']=='DT1:loc.arc');found=[]
    for p in sorted(active_files(root/'assets','.adf')):
        disk=module._ofs_disk_class()(p.read_bytes());summary=disk.parse()
        for n,data in disk.files.items():
            if summary['volume']+':'+n!='DT1:loc.arc':continue
            require(len(data)==expected['size'] and sha256(data)==expected['sha256'],'location archive disagrees with locked inventory')
            asset=module.decode_indexed_asset('DT1:loc.arc',p.name,data);rows=selector_rows(asset.entries)
            found.append(dict(path='DT1:loc.arc',sha256=sha256(data),rows=rows))
    require(len(found)==1,'unique locked location archive required')
    result=found[0];require({x['argument'] for x in result['rows']}==set(range(1,7)),'changed asset argument domain requires a new row bound')
    return result

def prove(root,f,a):
    from data_provider_tables import fragments,binding,compact
    require(set(a)==IDS,'full loader/alias/dispatcher/reader transfer required')
    c=a['ov04_F_000C'][0];fragments(c,'for (i = 0; i < 35; i++) {','G_h01_4524[i].target = (char *)&G_h01_470A + (long)i * 40;','F_h04_0104();')
    c=a['ov04_F_0104'][0];fragments(c,'struct Location {','char pad[30];','int selected;','int a;','int b;','int c;','int d;','location = (struct Location *)&G_h01_470A;','location = (struct Location *)(&G_h01_470A + (long)count * 40);','&location->a, &location->b,','&location->c, &location->d);')
    # Keep the actual filename string; semantic source views strip strings so
    # they cannot manufacture other bounds/call witnesses.
    from data_providers import document
    ledger=document(root,'recovery/ledger.json');raw=to_mechanical(canonical_path(root,ledger['functions']['ov04_F_0104']['source']).read_text(encoding='ascii'));raw=re.sub(r'/\*.*?\*/|//[^\n]*','',raw,flags=re.S)
    require('G_h01_46DA = F_h00_86DC("DT1:loc.arc", 1005L);' in raw,'location archive is not independently named at its loader')
    c=a['resident_F_01BA'][0];fragments(c,'struct Point { char reserved[36]; unsigned int value; };','switch (G_h01_4524[arg].point->value & 0x000f) {','case 4:','result = F_h09_0000(G_h01_4524[arg].point->value >> 4);')
    c=a['ov09_F_0000'][0];fragments(c,'recovered(arg)','int arg;','F_h09_18D0(arg);')
    prefix=c.split('F_h09_18D0(arg);',1)[0];require(not re.search(r'\barg\s*(?:\+\+|--|[+*/-]?=(?!=))',prefix),'argument transfer changed before row reader')
    c=a['ov09_F_18D0'][0];fragments(c,'struct Row { int values[5]; };','unsigned int i;','i = 1;','G_h01_4264[i] = G_h01_12C0[n-1].values[i-1];','++i;','} while (i < 6);')
    binding(a['ov09_F_18D0'],'G_h01_12C0',0x12c0)
    domain=selectors(root)
    return dict(archive=domain,argument_domain=list(range(1,7)),row_indices=list(range(6)),word_columns=list(range(5)),row_stride=10,typed_bytes=60,capacity_claim=False,limits='fixed supplied loc.arc loader/dispatcher path; no claimed32-row capacity or historical allocation')
