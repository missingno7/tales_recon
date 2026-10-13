"""Opt-in complete-member library routing, preserving compiler-oracle identities.

Like helper_exports, register exact trial texts and wrap only their harness
and object builders. The preprocessor routes a mechanical declaration to the
real pinned library symbol while preserving its C return/argument view.
"""
import re
from common import require, sha256, json_bytes

_routes={}
_installed=False
FIELD='runtime_library_routes'


def derive(members, source, *, game_sha256=None):
    from recovery_state import runtime_dependencies
    from analysis_support import game
    if game_sha256 is None:
        blob,_,_=game()
        game_sha256=sha256(blob)
    runtime=runtime_dependencies(dict(game_sha256=game_sha256))
    rows={}
    local={(m['hunk'],m['start']) for m in members}
    for m in members:
        for call in m.get('direct_callees',()):
            key=(call.get('hunk'),call.get('offset'))
            item=runtime.get(key,{})
            if call.get('basis')!='PC_RELATIVE' or key in local or item.get('kind')!='LIBRARY_MEMBER':continue
            symbol=item['symbol']
            # Private/register-ABI dot entries cannot be guessed into C linkage.
            if not re.fullmatch(r'_[A-Za-z][A-Za-z_0-9]*',symbol):continue
            name='F_h%02d_%04X'%key
            require(re.search(r'\bextern\s+[^;{}]*\b'+name+r'\s*\(\s*\)\s*;',source),
                    'runtime call lacks mechanical extern declaration: '+name)
            rows[name]=dict(name=name, symbol=symbol, evidence=item['evidence'], evidence_sha256=item['evidence_sha256'])
    return [rows[k] for k in sorted(rows)]


def object_source(source, routes):
    return ''.join('#define %s %s\n'%(r['name'],r['symbol'][1:]) for r in routes
                   if re.search(r'\b'+re.escape(r['name'])+r'\b',source))+source


def register(source, routes):
    if not routes:return
    require(_routes.get(source,routes)==routes,'one trial has conflicting library routes')
    _routes[source]=routes
    install()


def install():
    global _installed
    if _installed:return
    import sys
    import compiler_oracle
    base_harness,base_objects=compiler_oracle.harness,compiler_oracle.object_specs
    def harness(source,target_node=1,local_functions=(),*args,**kwargs):
        routes=_routes.get(source,())
        if not routes:return base_harness(source,target_node,local_functions,*args,**kwargs)
        text=base_harness(source,target_node,[*local_functions,*(r['name'] for r in routes)],*args,**kwargs)
        return text+'/* Library routes '+sha256(json_bytes(routes))+' */\n'
    def object_specs(trial):
        objects=base_objects(trial)
        routes=_routes.get(trial['source'],())
        return [dict(o,source=object_source(o['source'],routes)) for o in objects] if routes else objects
    compiler_oracle.harness,compiler_oracle.object_specs=harness,object_specs
    for name in ('queued_oracle','mixed_profile_oracle'):
        module=sys.modules.get(name)
        if module is not None:
            if getattr(module,'harness',None) is base_harness:module.harness=harness
            if getattr(module,'object_specs',None) is base_objects:module.object_specs=object_specs
    _installed=True


def replay(unit, source, functions, *, game_sha256=None):
    if FIELD not in unit:return
    by={f['id']:f for f in functions}
    members=[by.get(m['id'],m) for m in unit['ordered_members']]
    require(all(m.get('direct_callees') is not None for m in members),'library routes need full original call facts')
    routes=derive(members,source,game_sha256=game_sha256)
    require(routes and routes==unit[FIELD], 'library routes do not re-derive')
    register(source,routes)
