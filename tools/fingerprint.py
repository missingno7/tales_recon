"""Systematic source corpus and searchable historical code-generation matrix."""
import argparse
import json
from pathlib import Path
from difflib import SequenceMatcher
from compiler_oracle import compile_many,PROFILES,ROOT
from common import require,write_json,sha256
from function_compare import decode_all
from recovery_state import evidence

CORPUS={
 'char_return':'char recovered(a) char a; { char value; value=a; return value; }',
 'unsigned_char_return':'unsigned char recovered(a) char a; { char value; value=a; return value; }',
 'unsigned_char_assignment':'struct item { char pad[13]; unsigned char value; }; extern struct item input[1]; extern struct item output[1]; recovered() { output->value=input->value+0; }',
 'unsigned_char_assignment_plain':'struct item { char pad[13]; unsigned char value; }; extern struct item input[1]; extern struct item output[1]; recovered() { output->value=input->value; }',
 'unsigned_byte_pointer_assignment':'struct item { char pad[12]; int value; }; extern unsigned char output; recovered(p) struct item *p; { output=((unsigned char *)&p->value)[1]; }',
 'unsigned_byte_pointer_promoted':'struct item { char pad[12]; int value; }; extern unsigned char output; recovered(p) struct item *p; { output=((unsigned char *)&p->value)[1]+0; }',
 'unsigned_high_byte_mask':'struct item { char pad[12]; int value; }; extern unsigned char output; recovered(p) struct item *p; { output=(p->value>>8)&255; }',
 'int_from_char_return':'int recovered(a) char a; { char value; value=a; return value; }',
 'unsigned_int_from_char_return':'unsigned int recovered(a) char a; { char value; value=a; return value; }',
 'long_from_char_return':'long recovered(a) char a; { char value; value=a; return value; }',
 'char_expression_fallthrough':'recovered(a) char a; { char value; value=a; value; }',
 'typed_char_expression_fallthrough':'char recovered(a) char a; { char value; value=a; value; }',
 'typed_unsigned_char_expression_fallthrough':'unsigned char recovered(a) char a; { char value; value=a; value; }',
 'int_expression_fallthrough':'recovered(a) int a; { int value; value=a; value; }',
 'literal_string':'char *recovered() { return "oracle"; }',
 'literal_argument':'extern int sink(); recovered() { return sink("oracle"); }',
 'adjacent_calls':'extern int first(); extern int second(); recovered(a) int a; { first(a); return second(a); }',
 'forward_local_calls':'int forward_public(); static int forward_static(); recovered(a) int a; { forward_public(a); return forward_static(a); } forward_public(a) int a; { return a+1; } static forward_static(a) int a; { return a-1; }',
 'char_struct_index':'struct item { long a,b,c; }; extern struct item table[36]; long recovered(i) char i; { return table[i].b; }',
 'int_add':'int recovered(a,b) int a,b; { return a+b; }',
 'word_add':'short recovered(a,b) short a,b; { return a+b; }',
 'long_arithmetic':'long recovered(a,b) long a,b; { return (a-b)*3; }',
 'long_high_word_shift':'recovered(v) long v; { return (v>>16)%3; }',
 'long_high_word_pointer':'recovered(v) long v; { return ((unsigned *)&v)[0]%3; }',
 'long_high_word_call_modulo':'extern long value(); recovered() { return (unsigned)value()%3; }',
 'unsigned_arithmetic':'unsigned recovered(a,b) unsigned a,b; { return (a>>2)+(b&15); }',
 'signed_compare':'recovered(a,b) int a,b; { if(a<b) return -1; else return 1; }',
 'unsigned_compare':'recovered(a,b) unsigned a,b; { return a<b; }',
 'boolean_nested_return':'int recovered(a,b) int a; long b; { if(a>0) { if((long)a>b) return 1; } return 0; }',
 'boolean_early_return':'int recovered(a,b) int a; long b; { if(a<=0) return 0; return (long)a>b; }',
 'boolean_expression_return':'recovered(a,b) int a; long b; { return (long)a>b; }',
 'char_arguments':'recovered(a,b) char a,b; { return a+b; }',
 'void_return':'void recovered(a) int *a; { *a=7; }',
 'register_loop':'recovered(a,n) int *a,n; { register int i,s; s=0; for(i=0;i<n;i++) s+=a[i]; return s; }',
 'local_loop':'recovered(a,n) int *a,n; { int i,s; s=0; for(i=0;i<n;i++) s+=a[i]; return s; }',
 'while_loop':'recovered(a) int a; { while(a>10) a-=3; return a; }',
 'switch_dense':'recovered(a) int a; { switch(a) { case 0:return 3; case 1:return 8; case 2:return 11; case 3:return 17; case 4:return 22; default:return -1; } }',
 'switch_sparse':'recovered(a) int a; { switch(a) { case 2:return 3; case 20:return 8; case 200:return 11; default:return -1; } }',
 'pointer_arithmetic':'long *recovered(p,n) long *p; int n; { return p+n; }',
 'struct_fields':'struct item { char a,b; int n; long v; }; long recovered(p) struct item *p; { return p->v+p->n+p->a; }',
 'array_index':'recovered(p,n) int *p,n; { return p[n]+p[n+1]; }',
 'global_access':'extern int counter; recovered(n) int n; { counter+=n; return counter; }',
 'static_data':'recovered(n) int n; { static int values[3]={3,7,11}; return values[n]; }',
 'static_bss':'recovered(n) int n; { static int count; count+=n; return count; }',
 'function_pointer':'recovered(fn,n) int (*fn)(); int n; { return (*fn)(n); }',
 'library_strlen':'recovered(p) char *p; { return strlen(p); }',
 'varargs_stack_walk':'recovered(n,a) int n,a; { int *p,s; p=&a; s=0; while(n--) s+=*p++; return s; }',
 'nested_if':'recovered(a,b) int a,b; { if(a) { if(b) return a+b; return a; } return b; }',
 'movem_pressure':'long recovered(p,n) long *p; int n; { register long a,b,c,d; a=p[0]; b=p[1]; c=p[2]; d=p[3]; while(n--) { a+=b; b+=c; c+=d; d+=a; } return a+b+c+d; }'}


def build():
    base=ROOT/'experiments/fingerprints';base.mkdir(parents=True,exist_ok=True)
    trials=[];names=[]
    for name,source in CORPUS.items():
        text='/* Independent compiler fingerprint: '+name+' */\n'+source+'\n';path=base/(name+'.c');path.write_text(text,newline='\n')
        for profile in PROFILES:trials.append(dict(source=text,profile=profile));names.append((name,path))
    results=compile_many(trials);entries=[]
    for (name,path),r in zip(names,results):
        entry=dict(name=name,source=path.relative_to(ROOT).as_posix(),source_sha256=r['identity']['source_sha256'],
                   profile=r['identity']['profile'],compiler=r['identity'],status=r['status'],cache_key=r['cache_key'],artifacts=r['artifacts'],
                   retained_directory=Path(r['directory']).relative_to(ROOT).as_posix())
        if r['status']=='COMPILED':
            c=r['contribution'];instructions,bad=decode_all(bytes.fromhex(c['code_hex']))
            entry.update(contribution=c,mnemonics=[i.mnemonic for i in instructions],decode_stop=bad,
                         assembly=(Path(r['directory'])/(r['prefix']+'.asm')).read_text())
        else:entry['guest_returncodes']=r['guest_returncodes']
        entries.append(entry)
    report=dict(schema_version=1,corpus_programs=len(CORPUS),profiles=list(PROFILES),trials=len(entries),
                compiled=sum(e['status']=='COMPILED' for e in entries),entries=entries,
                historical_toolchain_selection='UNRESOLVED; use game-function comparison receipts, not shared runtime')
    write_json(ROOT/'evidence/fingerprints/index.json',report)
    print(json.dumps({k:v for k,v in report.items() if k!='entries'}))


def check():
    """Reject a stale or incomplete generated fingerprint index."""
    report=json.loads((ROOT/'evidence/fingerprints/index.json').read_text())
    profiles=list(PROFILES);entries=report.get('entries',[])
    require(report.get('corpus_programs')==len(CORPUS),'fingerprint corpus count is stale')
    require(report.get('profiles')==profiles,'fingerprint profile set is stale')
    require(report.get('trials')==len(CORPUS)*len(profiles),'fingerprint trial count is stale')
    require(len(entries)==report['trials'],'fingerprint entries are incomplete')
    observed={(e.get('name'),e.get('profile')) for e in entries}
    expected={(name,profile) for name in CORPUS for profile in profiles}
    require(observed==expected,'fingerprint name/profile matrix is incomplete')
    require(report.get('compiled')==sum(e.get('status')=='COMPILED' for e in entries),'fingerprint compiled count is stale')
    print(json.dumps({k:report[k] for k in ('schema_version','corpus_programs','profiles','trials','compiled')}))


def main():
    ap=argparse.ArgumentParser(description=__doc__);ap.add_argument('--build',action='store_true');ap.add_argument('--check',action='store_true');ap.add_argument('--search');ap.add_argument('--function');a=ap.parse_args()
    if a.build:build();return
    if a.check:check();return
    index=json.loads((ROOT/'evidence/fingerprints/index.json').read_text());entries=index['entries']
    if a.search:entries=[e for e in entries if a.search in ' '.join(e.get('mnemonics',[])) or a.search in e['name']]
    if a.function:
        f=next(f for f in evidence()['functions'] if f['id']==a.function);m=[i['mnemonic'] for i in f['instructions']]
        entries=sorted(entries,key=lambda e:SequenceMatcher(None,m,e.get('mnemonics',[])).ratio(),reverse=True)[:12]
    for e in entries:print(json.dumps(dict(name=e['name'],profile=e['profile'],status=e['status'],code_size=e.get('contribution',{}).get('code_size'),cache_key=e['cache_key'])))

if __name__=='__main__':main()
