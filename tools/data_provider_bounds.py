"""Closed independent bounds recipes for batch 0002, no DATA-derived extents."""
from names import to_mechanical
import re
from common import require,sha256
from repo_paths import canonical_path
from data_providers import WIDTHS,struct_layout,definition_size

ENTRY=[dict(name=n,type=t,offset=o) for n,t,o in [('kind','unsigned char',0),('active','unsigned char',1),('pos','int',2),('t','int',4)]]


def compact(text):return ''.join(text.split())


def anchor(root,ledger,accepted,e):
    fid=e['function'];require(fid in accepted and fid in ledger['functions'],'bounds consumer is not canonical')
    item=ledger['functions'][fid];raw=to_mechanical(canonical_path(root,item['source']).read_bytes());proofraw=canonical_path(root,item['proof']).read_bytes()
    require(sha256(raw)==item['source_sha256']==e['source_sha256'] and sha256(proofraw)==item['proof_sha256']==e['proof_sha256'],'stale independent bounds anchor')
    import json
    return raw.decode('ascii'),json.loads(proofraw)


def bases(fact,d,f,proof):
    off=fact['original']['start']+d['offset'];want=dict(symbol='_'+d['symbol'],hunk=1,offset=off,addend=0)
    matched=[b for b in proof['comparison']['relocation_proof'] if b.get('identity')==want and b.get('kind') in ('A4_D16_SYMBOL','HUNK_RELOCATION')]
    require(matched and [f['start']+b['offset']-2 for b in matched]==d['evidence']['bases'],'incomplete/moved aggregate base bindings')
    ins={i['offset']:i for i in f['instructions']}
    for site in d['evidence']['bases']:
        b=ins[site];require(b['mnemonic']=='lea.l','aggregate base is not decoded LEA')
        if b['size']==4:require(b['raw']=='41ec'+(off-32766).to_bytes(2,'big',signed=True).hex(),'A4 base differs')
        else:
            require(b['size']==6 and b['raw']=='41f9'+off.to_bytes(4,'big').hex(),'absolute base differs')
            require(any(r['source_offset']==site+2 and r['target_hunk']==1 and r['addend_raw']==off and r['width']==4 for r in f['relocations']),'absolute base lacks RELOC32')
    return ins


def mutations(c,name):
    return [compact(x) for x in re.findall(r'\b'+re.escape(name)+r'\s*(?:(?:\+\+|--)\s*;|(?:\+=|-=|&=|=(?!=))[^;]+;)',c)]


def state16(root,analysis,ledger,accepted,e,types):
    anchors={a['function']:anchor(root,ledger,accepted,a)[0] for a in e['anchors']}
    expected={'ov05_F_0000','ov05_F_1860','ov05_F_30EE','ov05_F_318E','ov05_F_3A9E'}
    require(set(anchors)==expected,'complete state writer/helper anchors required')
    name='G_h01_5E40';g=next(g for g in types['globals'] if g['data_hunk_offset']==0x5E40)
    writes=[a for a in g['accesses'] if a['direction'] in ('WRITE','READ_WRITE')]
    writers={a['function'] for a in writes}
    require(writers==expected-{'ov05_F_3A9E'} and not g['address_taken'],'unknown state writer/address escape')
    # Close the A4 miner blind spot and overlapping byte/long stores.
    for f in analysis['functions']:
        require(not any(r['target_hunk']==1 and 0x5E3D<=r['addend_raw']<0x5E42 for r in f.get('relocations',[])),'absolute state alias requires independent analysis')
    for other in types['globals']:
        o=other['data_hunk_offset']
        for a in other['accesses']:
            w=a['width_bytes'] or 0
            if o!=0x5E40 and o<0x5E42 and o+w>0x5E40:
                require(a['direction'] not in ('WRITE','READ_WRITE') and a['mnemonic'].startswith(('move.','cmp','tst')),'overlapping state write/unknown alias')
    body=compact(anchors['ov05_F_3A9E'])
    require(body=='recovered(a)inta;{if(a>0&&a<4)--a;elseif(a==0)a=15;elseif(a>13&&a<=15)--a;elseif(a>=5&&a<=10)++a;returna;}','unreviewed state helper transfer')
    helper=lambda a:a-1 if 0<a<4 else 15 if a==0 else a-1 if 13<a<=15 else a+1 if 5<=a<=10 else a
    require(all(0<=helper(a)<=15 for a in range(16)),'helper escapes state domain')
    zero=compact(re.split(r'\brecovered\s*\(',anchors['ov05_F_0000'],maxsplit=1)[1]);require(set(mutations(anchors['ov05_F_0000'],name))<={name+'=0;',name+'=8;'},'entry state transfer differs')
    require(zero.index(name+'=0;')<zero.index('F_h05_1860()'),'entry initialization must precede the table consumer')
    for fid,c in anchors.items():
        if fid=='ov05_F_3A9E':continue
        body=compact(c);ms=mutations(c,name)
        for m in ms:
            require(m in [name+x for x in ['=0;','=8;','=1;','=7;','=5;','=2;','=6;','++;','--;','+=16;','+=2;','=cur;','=F_h05_3A9E('+name+');','=(F_h00_463E()&1)?8:0;','=(G_h01_5E40+8)&15;','=16-G_h01_5E40;','=F_h00_463E()&15;']], 'unreviewed state mutation')
        for op,guard,fix in [('++;','>15','=0;'),('--;','<0','+=16;'),('+=2;','>15','=0;')]:
            if name+op in ms:require(body.count(name+op)==body.count(name+op+'if('+name+guard+')'+name+fix),'state wrap is not immediate/complete')
        if name+'=16-'+name+';' in ms:require('if('+name+'>8)'+name+'=16-'+name+';' in body,'reflection requires 9..15 guard')
    cur=compact(anchors['ov05_F_30EE']);require('cur='+name+';' in cur and 'cur=F_h00_463E()&15;' in cur and 'if(cur==4)cur=5;' in cur,'saved/random state transfer differs')
    # Canonical callers close entry to the state subsystem. The only consumer
    # call is from the initialized entry; helper/writer calls stay in this set.
    callee_names={'F_h05_1860','F_h05_30EE','F_h05_318E','F_h05_3A9E'}
    for fid,item in ledger['functions'].items():
        c=to_mechanical(canonical_path(root,item['source']).read_text())
        calls=[n for n in callee_names if re.search(r'(?<!extern int )(?<!extern long )\b'+n+r'\(',c)]
        if calls:require(fid in expected,'new caller requires state initialization proof')
    return dict(kind='INDUCTIVE_STATE16',domain=[0,15],initialization='ov05_F_0000 before sole F1860 call',writer_functions=sorted(writers),write_sites=[dict(function=a['function'],site=a['offset'],width=a['width_bytes']) for a in writes],helper_outputs=[helper(a) for a in range(16)],alias_5E41='READ_ONLY')


def verify_definition(root,fact,d,analysis,ledger,promotions,types):
    accepted={p['id'] for p in promotions};e=d['evidence'];c,proof=anchor(root,ledger,accepted,e);f=next(f for f in analysis['functions'] if f['id']==e['function']);ins=bases(fact,d,f,proof);kind=d['bounds']['kind'];off=fact['original']['start']+d['offset'];size=definition_size(d)
    require(e['declaration'] in c.splitlines(),'typed definition declaration absent')
    details={}
    if kind=='STRUCT_ABI':
        require(d['type']=='struct Entry' and struct_layout(d)==ENTRY and size==6,'only independently complete Entry view admitted')
        body='struct Entry { '+''.join(x['type']+' '+x['name']+'; ' for x in ENTRY)+'};'
        require(body in c and e['declaration']=='extern struct Entry '+d['symbol']+';','complete canonical struct body/order required')
        require(len(e['bases'])==1,'one independently bound Entry base required')
        for a in e['field_accesses']:
            field=next(x for x in ENTRY if x['name']==a['field']);i=ins[a['site']]
            require(i['mnemonic'].endswith({1:'.b',2:'.w'}[WIDTHS[field['type']]]) and ('$%x(a0)'%field['offset']) in i['operands'],'struct field decoded offset/width differs')
            require(e['bases'][0]<a['site']<e['block_end'] and a['width']==WIDTHS[field['type']],'field outside bound Entry block/wrong width')
            sequence=f['instructions'];previous=[j for j in sequence if j['offset']<a['site'] and j['operands'].endswith(', a0')][-1]
            require(previous['mnemonic']=='movea.l' and previous['operands']=='-$e(a5), a0','field pointer is not the bound Entry local')
            stores=[j for j in sequence if e['bases'][0]<=j['offset']<a['site'] and j['operands'].endswith(', -$e(a5)')]
            require(stores and stores[-1]['offset']==e['bases'][0]+4 and not any(j['mnemonic']=='jsr' and previous['offset']<j['offset']<a['site'] for j in sequence),'Entry pointer changed/clobbered before field access')
        require({a['field'] for a in e['field_accesses']}=={'active','pos','t'},'complete used Entry field coverage required')
        details=dict(fields=ENTRY,alignment=2,padding_offsets=[],unused_typed_field='kind: complete canonical struct view; no fabricated filler')
    else:
        require(d['type']=='char' and type(d.get('count')) is int,'signed-byte aggregate type required')
        expected_decl='extern char '+d['symbol']+'['+str(1 if kind=='GUARDED_BYTE' else d['count'])+'];'
        require(e['declaration']==expected_decl,'canonical byte view differs')
        for b in e['bases']:
            reads=[i for i in f['instructions'] if b< i['offset']<=b+8 and i['mnemonic']=='move.b' and '(a0, ' in i['operands']]
            require(len(reads)==1 and ins[reads[0]['offset']+reads[0]['size']]['mnemonic']=='ext.w','signed byte indexed load/extension differs')
        if kind=='GUARDED_BYTE':
            require(d['count']==112 and 'c=(c<0x70&&c>0)?'+d['symbol']+'[c]:-1;' in compact(c),'guard-bounded 1..111 lookup required')
            b=e['bases'][0];window=[(i['mnemonic'],i['operands']) for i in f['instructions'] if b-22<=i['offset']<b]
            require(window==[('cmpi.b','#$70, -$1(a5)'),('bge.b','$501e'),('tst.b','-$1(a5)'),('ble.b','$501e'),('move.b','-$1(a5), d0'),('ext.w','d0'),('ext.l','d0')],'decoded signed lower/upper guards differ')
            details=dict(index_domain=[1,111],extent_derivation='(highest index 111 + 1) * sizeof(char); element zero belongs to the same typed array base, not filler',partial_canonical_view=1)
        elif kind=='COORDINATES':
            require(d['count']==32 and e['function']=='ov08_F_0000','coordinate table shape differs')
            ms=mutations(c,'c64');require(ms==['c64=0;','c64=8;','c64--;','c64&=0xf;','c64++;','c64&=0xf;','c64-=2;','c64&=0xf;','c64+=2;','c64&=0xf;'],'unreviewed local coordinate transfer')
            require('G_h01_6F2E=0;' in compact(c) and compact(c).count('G_h01_6F2E=4;')==1,'state-4 initialization gate differs')
            for op in ['--;','++;','-=2;','+=2;']:require('c64'+op+'c64&=0xf;' in compact(c),'coordinate update lacks immediate mask')
            require(len(e['bases'])==12 and all(0<=i<=31 for s in range(16) for i in [s*2,s*2+1,2*(15-s),2*(15-s)+1]),'complete paired/mirrored index domain required')
            writes=[i for i in f['instructions'] if i['operands'].endswith('-$64(a5)') and i['mnemonic'] not in ('cmpi.b',)]
            require([(i['mnemonic'],i['operands'].split(',')[0]) for i in writes]==[('clr.b','-$64(a5)'),('move.b','#$8'),('subq.b','#$1'),('andi.b','#$f'),('addq.b','#$1'),('andi.b','#$f'),('subq.b','#$2'),('andi.b','#$f'),('addq.b','#$2'),('andi.b','#$f')],'decoded local writes/masks differ')
            indices=[compact(x) for x in re.findall(re.escape(d['symbol'])+r'\[([^\]]+)\]',c) if not x.isdigit()]
            require(indices==['c64*2','c64*2+1']*4+['2*(15-c64)+1','2*(15-c64)','2*c64+1','2*c64'],'unreviewed coordinate index expression')
            for fid,item in ledger['functions'].items():
                text=to_mechanical(canonical_path(root,item['source']).read_text())
                for m in mutations(text,'G_h01_6F2E'):
                    match=re.fullmatch(r'G_h01_6F2E=(0x[0-9a-fA-F]+|[0-9]+);',m)
                    require(match and (int(match[1],0)!=4 or fid==f['id']),'unreviewed transition into coordinate state 4')
            details=dict(local_domain=[0,15],index_domain=[0,31],induction='entry sets state 0; only transition into state 4 follows c64=0/8; all later mutations immediately mask 15; mirrored reads preserve 0..31')
        elif kind=='STATE16':
            require(d['count']==16 and e['function']=='ov05_F_1860','state table shape differs')
            require(d['symbol']+'[G_h01_5E40]' in compact(c),'state-indexed byte lookup absent')
            details=state16(root,analysis,ledger,accepted,e,types)
        else:require(False,'unsupported independently bounded byte route')
    for g in types['globals']:
        o=g['data_hunk_offset']
        if off<=o<off+size:
            if kind=='STRUCT_ABI':
                field=next((x for x in ENTRY if x['offset']==o-off),None)
                require(field and all(w==WIDTHS[field['type']] for w in g['observed_widths_bytes']),'interior struct type conflict')
            else:require(all(w==1 for w in g['observed_widths_bytes']),'conflicting byte-array access width')
    return dict(symbol=d['symbol'],type=d['type'],bytes=size,original_offset=off,function=f['id'],bounds=kind,bases=e['bases'],details=details,evidence_route='CURRENT_CANONICAL_TYPED_VIEW_AND_DECODED_BOUND_ACCESSES',historical_extent='UNKNOWN; reconstructed complete provider only')
