"""Canonical proof admission registry, validation memo and accounting adapters.

Validators retain their existing checks. Publishers retain their transaction and
regression boundaries. Accounting categories never imply interchangeability of
proof classes; in particular behavioral C never satisfies an exact-C predicate.
"""
from dataclasses import dataclass, field
import importlib
import json
import inspect
from pathlib import Path
from types import FunctionType

from common import json_bytes, require, sha256
from validation_memo import scope, scoped, validated, digest


def exact_comparison(report):
    return report.get('verdict') == 'EQUAL'


def accepted_unit(report, exact_members=(), *, require_inexact=False):
    """A whole exact unit or specifically named exact members of a mixed unit.

    Callers still prove extents, unclaimed bytes, source bindings and every
    behavioral member's separately recorded claim. This predicate grants none
    of those obligations and never upgrades a behavioral member to exact C.
    """
    if exact_comparison(report):
        return True
    return (report.get('verdict') == 'ACCEPTED_WITH_BEHAVIORAL' and
            (not require_inexact or report.get('exact_unit') is False) and
            set(exact_members) <= set(report.get('accepted_exact_members', ())))


@dataclass
class Context:
    blob: bytes
    model: dict
    analysis: dict
    ledger: dict
    rows: dict = field(default_factory=dict)

    def __post_init__(self):
        # Attempts/queue state has no admission authority. All canonical maps
        # remain explicit inputs, including cross-class source dependencies.
        from recovery_state import canonical_state
        self.identity = digest(dict(blob=sha256(self.blob), model=self.model,
                                              analysis=self.analysis,
                                              ledger=canonical_state(self.ledger)))

    @property
    def promoted(self):
        return self.rows['functions']


def _load(root, ctx, module, function, ledger, only=None):
    method = getattr(importlib.import_module(module), function)
    if module == 'data_providers':
        return method(root, ctx.blob, ctx.model, ctx.analysis, ledger, ctx.promoted, only=only)
    if module in ('resident_mixed',):
        return method(root, ctx.blob, ctx.model, ctx.analysis, ctx.promoted, ledger)
    return method(root, ctx.blob, ctx.model, ctx.analysis, ledger)


@dataclass(frozen=True)
class ProofClass:
    name: str
    ledger_map: str
    categories: tuple
    validator: tuple
    projector: tuple
    publisher: str

    def validate(self, root, ctx):
        module, function = self.validator
        if self.name == 'functions':
            method=getattr(importlib.import_module(module),function)
            return method(root, ctx.blob, ctx.model, ctx.analysis)
        if self.name == 'dead_code':
            import dead_code_extents as dead
            if dead.refreshing_analysis() or not (root / dead.ADMISSIONS).exists():
                return []
            from dead_code_promotion import records
            identifiers = list(records(root))
        elif self.name == 'mixed':
            # Include staged rows as before: neither an unaccepted fact nor its
            # CFG diagnostic acquires accounting authority through the registry.
            from resident_mixed import FACT
            from startup_recovery import FACT as startup_fact
            identifiers = [json.loads((root / p).read_bytes())['id']
                           for p in (FACT, startup_fact) if (root / p).exists()]
        else:
            if self.name == 'data':
                from dead_code_extents import refreshing_analysis
                if refreshing_analysis():
                    return []
            identifiers = sorted(ctx.ledger.get(self.ledger_map, {}))
        if not identifiers:
            return _load(root,ctx,module,function,ctx.ledger)
        result = []
        for ident in identifiers:
            def replay():
                # Mixed/complete C validators deliberately validate their
                # complete admission set, including staged diagnostic rows.
                if self.name == 'data':
                    # Full ledger: provider evidence may read a neighbour's fact.
                    return _load(root, ctx, module, function, ctx.ledger, only=ident)
                ledger = ctx.ledger if self.name in ('mixed', 'dead_code') else dict(
                    ctx.ledger, **{self.ledger_map: {ident: ctx.ledger[self.ledger_map][ident]}})
                rows = _load(root, ctx, module, function, ledger)
                return [r for r in rows if r['id']==ident] if self.name in ('mixed','dead_code') else rows
            method=getattr(importlib.import_module(module),function)
            # Opaque callables and closures have mutable state outside the
            # declared inputs. Only source-backed functions (including trusted
            # wrappers whose bodies are in the tools closure) can use the memo.
            original=inspect.unwrap(method) if isinstance(method,FunctionType) else None
            folder=Path(__file__).resolve().parent
            source_backed=(isinstance(original,FunctionType) and not original.__closure__ and
                           Path(method.__code__.co_filename).resolve().is_relative_to(folder) and
                           Path(original.__code__.co_filename).resolve().is_relative_to(folder))
            if source_backed:
                result.extend(validated(root, self.name, ident, ctx.identity, module, replay))
            else:
                result.extend(replay())
        # Preserve the historical provider ordering (initial two ASM facts
        # precede the driver/callback/frameless/glue groups).
        if self.name == 'asm':
            import reconstructed_asm as initial
            import audio_driver_asm as driver
            import audio_callback_asm as callback
            import audio_frameless_asm as frameless
            import glue_library_asm as glue
            order = [*initial.SPECS, *driver.BATCH2_SPECS, *callback.SPECS,
                     *frameless.SPECS, *glue.SPECS]
            result.sort(key=lambda r: order.index(r['id']))
        if self.name == 'code_data':
            import code_data_providers as base
            import audio_score_measured as measured
            import audio_region_provider as region
            import audio_stateful_provider as stateful
            order={'MEASURED_TYPED_AUDIO_SCORE':1,region.KIND:2,stateful.KIND:3}
            result.sort(key=lambda r:order.get(r.get('kind'),0))
        if self.name in ('data','code_data'):
            occupied=set()
            if self.name=='data':
                from data_providers import contributions
                spans=contributions(result)
            else:
                spans=[dict(hunk=r['original']['hunk'],start=p['original_start'],end=p['original_end'])
                       for r in result for p in r.get('parts',[dict(original_start=r['original']['start'],original_end=r['original']['end'])])]
            for span in spans:
                points={(span['hunk'],p) for p in range(span['start'],span['end'])}
                require(not points & occupied,'overlapping canonical providers')
                occupied.update(points)
        return result

    def contributions(self, root, ctx, rows):
        module, function = self.projector
        if module == 'acceptance':
            return globals()[function](root, ctx, rows)
        method = getattr(importlib.import_module(module), function)
        if module == 'data_providers':
            return method(rows)
        if module in ('resident_mixed', 'dead_code_promotion'):
            return method(root, ctx.blob, ctx.model, ctx.analysis, ctx.promoted, ctx.ledger, rows=rows)
        return method(root, rows)


def _identity_contributions(root, ctx, rows):
    return rows


def _function_contributions(root, ctx, promoted):
    from hybrid_image import SPECIMENS, normalize
    from repo_paths import canonical_path
    specimens = json.loads(canonical_path(root, SPECIMENS).read_bytes())
    require(specimens['game_sha256'] == sha256(ctx.blob), 'specimens belong to another oracle')
    require(set(specimens['functions']) == set(ctx.ledger['functions']),
            'compiled specimens do not name precisely canonical source')
    by = {f['id']: f for f in ctx.analysis['functions']}
    result = []
    for p in promoted:
        fid = p['id']; item = ctx.ledger['functions'][fid]; s = specimens['functions'][fid]
        require(s['proof_sha256'] == item['proof_sha256'] and s['source_sha256'] == item['source_sha256'],
                'specimen proof binding changed')
        proof = json.loads(canonical_path(root, item['proof']).read_text())
        raw = normalize(by[fid], bytes.fromhex(s['actual_hex']), proof['comparison'], ctx.analysis['a4']['bias'])
        rels = [{k: r[k] for k in ('source_offset', 'target_hunk', 'type', 'width', 'addend_raw')}
                for r in ctx.model['relocations'] if r['source_hunk'] == p['hunk'] and p['start'] <= r['source_offset'] < p['end']]
        result.append(dict(id=fid, hunk=p['hunk'], start=p['start'], end=p['end'], category='RECOVERED_C', bytes=raw[:p['size']], relocations=rels))
        if len(raw) > p['size']:
            result.append(dict(id=fid+'_tail', hunk=p['hunk'], start=p['end'], end=p['start']+len(raw), category='COMPILER_OWNED_DATA', bytes=raw[p['size']:]))
    return result


REGISTRY = (
    ProofClass('functions', 'functions', ('RECOVERED_C', 'COMPILER_OWNED_DATA'),
               ('census', 'load_promotions'), ('acceptance', '_function_contributions'), 'promote_batch'),
    ProofClass('dead_code', 'dead_code_functions', ('RECOVERED_C', 'COMPILER_OWNED_DATA'),
               ('dead_code_promotion', 'canonical_rows'), ('dead_code_promotion', 'accepted_contributions'), 'dead_code_promotion'),
    ProofClass('mixed', 'mixed_source_objects', ('RECOVERED_C', 'RECOVERED_ASM', 'COMPILER_OWNED_DATA'),
               ('resident_mixed', 'load_source_objects'), ('resident_mixed', 'accepted_contributions'), 'mixed'),
    ProofClass('data', 'data_providers', ('RECOVERED_DATA', 'COMPILER_OWNED_DATA'),
               ('data_providers', 'load_data_providers'), ('data_providers', 'contributions'), 'promote_data'),
    ProofClass('asm', 'reconstructed_asm', ('RECONSTRUCTED_ASM',),
               ('reconstructed_asm', 'rows'), ('reconstructed_asm', 'contributions'), 'promote_asm'),
    ProofClass('code_data', 'code_data_providers', ('TYPED_CODE_DATA',),
               ('code_data_providers', 'rows'), ('code_data_providers', 'contributions'), 'promote_code_data'),
    ProofClass('behavioral', 'behavioral_functions', ('BEHAVIORAL_C',),
               ('behavioral', 'contributions'), ('acceptance', '_identity_contributions'), 'behavioral'),
)


def proof_class(name):
    found = next((c for c in REGISTRY if name in (c.name, c.ledger_map)), None)
    require(found is not None, 'unknown proof class: ' + name)
    return found


@scoped
def validate(root, ctx):
    for entry in REGISTRY:
        ctx.rows[entry.name] = entry.validate(root, ctx)
    return ctx


def contributions(root, ctx):
    result = []
    for entry in REGISTRY:
        rows = entry.contributions(root, ctx, ctx.rows[entry.name])
        require(all(r['category'] in entry.categories for r in rows),
                'unregistered accounting category: ' + entry.name)
        result.extend(rows)
    return result
