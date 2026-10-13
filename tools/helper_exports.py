"""Overlay export control for resident calls to pinned runtime arithmetic helpers.

The original Manx link gave the long-arithmetic helpers (``.mulu``, ``.divs``,
``.mods``, ``.modu``, ``.divu``) A4 jump-table slots because overlays call
them, and the linker then routes every separately compiled caller, resident
ones included, through those slots.  An isolated resident candidate links
its own c.lib copies with no overlay reference, so the same source calls them
PC-relative.  Measured in Aztec 3.6a: an overlay object that also calls the
helpers, referenced from the root harness, turns the resident candidate's
``jsr .mods`` into ``jsr d16(a4)`` and changes nothing else.

The control is harness code in its own overlay node and is never claimed.
It applies only to a source registered here with the helpers its original
reaches through A4 slots, derived from function evidence (A4 jump-stub
callees) and the complete pinned runtime-arithmetic contributions; the
harness hash binds it into the cache identity.  ``compiler_oracle`` stays
unchanged (several proof identities hash that file), so the control wraps
its ``harness`` and ``overlay_proxies`` for registered sources only; every
other harness and proxy list is returned unchanged.
"""
import json

from analysis_support import ROOT
from common import require

EVIDENCE = 'evidence/experiments/runtime-arithmetic.json'
CONTROL = 'helper_export_control'
# Helper -> statement that makes Aztec C call exactly that helper.
STATEMENTS = {'.mulu': 'a = a * b;', '.divs': 'a = a / b;', '.mods': 'a = a % b;',
              '.divu': 'c = c / d;', '.modu': 'c = c % d;',
              # m.lib FFP operators (float locals f, g and int k).
              '.Fadd': 'f = f + g;', '.Fsub': 'f = f - g;', '.Fmul': 'f = f * g;', '.Fdiv': 'f = f / g;',
              '.Fneg': 'f = -f;', '.Fcmp': 'if (f < g) k = 1;', '.Ftst': 'if (f) k = 2;',
              '.Ffix': 'k = f;', '.Fflt': 'f = k;'}
MEMBERS = 'evidence/experiments/runtime-members.json'
# m.lib's FFP operator stubs each jmp to the following amiga_ffp member, so a
# stub's bytes depend on how many stubs the link pulls after it.  The original
# resident holds the complete group; a caller of any stub links all of them.
FFP = ('.Fadd', '.Fcmp', '.Fneg', '.Ftst', '.Ffix', '.Fsub', '.Fdiv', '.Fflt', '.Fmul')
_routes = {}
_installed = False


def helper_entries():
    """Original resident offset -> helper name, from complete pinned contributions."""
    evidence = json.loads((ROOT / EVIDENCE).read_text())
    require(evidence.get('status') == 'COMPLETE_RUNTIME_CODE_MATCH', 'runtime arithmetic evidence is not complete')
    contributions = list(evidence['contributions'])
    if (ROOT / MEMBERS).is_file():
        members = json.loads((ROOT / MEMBERS).read_text())
        require(members.get('status') == 'COMPLETE_RUNTIME_CODE_MATCH', 'runtime member evidence is not complete')
        contributions += [c for c in members['contributions'] if {e['name'] for e in c['entries']} == set(FFP)]
    entries = {}
    for item in contributions:
        require(item['original']['hunk'] == 0, 'runtime helper outside resident CODE')
        for entry in item['entries']:
            offset = item['original']['offset'] + entry['offset']
            require(entries.get(offset, entry['name']) == entry['name'], 'runtime helper identity disagrees across profiles')
            entries[offset] = entry['name']
    return entries


def original_helpers(functions, entries=None):
    """Helpers the original functions call through A4 jump-table stubs (sorted names).

    Resident callers need every called helper routed through a slot.  Overlay
    callers already reach resident helpers through slots, so they need only
    the complete FFP group (stub bytes depend on the linked group).
    """
    entries = helper_entries() if entries is None else entries
    names = set()
    for f in functions:
        for callee in f.get('direct_callees', ()):
            if callee.get('basis') == 'A4_RELOCATED_JMP_STUB' and callee.get('hunk') == 0 and callee.get('offset') in entries:
                name = entries[callee['offset']]
                if name in FFP:
                    names.update(FFP)
                elif f.get('node') == 'resident':
                    names.add(name)
    return tuple(sorted(names))


def control_source(helpers):
    require(helpers and all(h in STATEMENTS for h in helpers), 'unknown runtime helper export')
    body = '\n'.join('    ' + STATEMENTS[h] for h in sorted(helpers))
    floats = '    float f, g;\n    int k;\n\n' if any(h in FFP for h in helpers) else ''
    return (CONTROL + '(a,b,c,d)\nlong a,b;\nunsigned long c,d;\n{\n' + floats + body + '\n    return 0;\n}\n')


def register(source, helpers):
    """Route ``source`` (an exact resident candidate text) through helper slots."""
    helpers = tuple(sorted(helpers))
    if not helpers:
        return
    install()
    require(_routes.get(source, helpers) == helpers, 'one source registered with different helper routes')
    _routes[source] = helpers


def routed(source):
    return _routes.get(source)


def install():
    """Wrap the oracle's harness/proxy builders once; unregistered sources are unchanged."""
    global _installed
    if _installed:
        return
    import sys
    import compiler_oracle
    base_harness, base_proxies = compiler_oracle.harness, compiler_oracle.overlay_proxies

    def harness(source, target_node=1, *args, **kwargs):
        text = base_harness(source, target_node, *args, **kwargs)
        helpers = _routes.get(source)
        if helpers and target_node == 0:
            text += ('/* Runtime helper export control (harness only). */\nextern int ' + CONTROL + '();\n'
                     'int (*helper_export_reference)() = ' + CONTROL + ';\n')
        elif helpers and any(h in FFP for h in helpers):
            # Overlay callers already reach resident helpers through slots; a
            # root control only makes the link pull the complete FFP group.
            text += '/* Runtime helper link control (harness only). */\n' + control_source(helpers)
        return text

    def overlay_proxies(source, target_node):
        proxies = base_proxies(source, target_node)
        helpers = _routes.get(source) if target_node == 0 else None
        if helpers:
            require(all(p['name'] != CONTROL for p in proxies), 'helper export control name collides')
            proxies = proxies + [dict(name=CONTROL, hunk=3, node=1, source=control_source(helpers))]
        return proxies

    compiler_oracle.harness, compiler_oracle.overlay_proxies = harness, overlay_proxies
    for name in ('queued_oracle', 'mixed_profile_oracle', 'resident_mixed'):
        module = sys.modules.get(name)
        if module is not None:
            if getattr(module, 'overlay_proxies', None) is base_proxies:
                module.overlay_proxies = overlay_proxies
            if getattr(module, 'harness', None) is base_harness:
                module.harness = harness
    _installed = True
