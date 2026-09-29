"""Curated link-compatibility of compiler profiles for per-object profile units.

Separately compiled objects may use different code-generation options only
when they link against one runtime library under one ABI.  This module is the
pure policy (no compiler, no emulator), shared by the verifier
(``check_unit``/``check_function`` through ``mixed_profile_oracle``) and the
promotion evidence check (``recovery_evidence``).

A class lists profiles whose compatibility is *established*, not inferred:

* ``aztec-3.6a-c.lib``: ``aztec36`` and ``aztec36-large-data`` (``+D``) run the
  same 3.6a cc/as/ln from SYS1 and link the same ``c.lib`` (both oracle
  identities name the same tool and library hashes; ``mixed_profile_oracle``
  re-checks that on every compile).  The game itself links both forms: the
  recovered default-profile functions and the three independent functions
  that need absolute ``+D`` resident-global addressing (docs/toolchain.json
  ``compiler_fingerprint_matrix.game_discrimination``) share one executable.

Every other profile (``aztec36-x3``, ``aztec36-long`` with ``c32.lib``, the
5.0a profiles with their own compiler and ``c16.lib``/``c.lib``) is refused in
a mixed unit until its compatibility is separately established.  Runtime ABI
compatibility is not library provenance.
"""
from common import require


# Flags must equal compiler_oracle.PROFILES (checked by the unit tests).
PROFILE_FLAGS={'aztec36':[],'aztec36-large-data':['+D']}

LINK_CLASSES={
    'aztec-3.6a-c.lib':dict(
        profiles=('aztec36','aztec36-large-data'),
        runtime='Aztec C 3.6a SYS1 c.lib (small-code default and +D large-data objects)',
        evidence=('docs/toolchain.json compiler_flags.aztec36-large-data and '
                  'compiler_fingerprint_matrix.game_discrimination: the original executable links default-profile '
                  'and +D large-data functions; identical 3.6a cc/as/ln and c.lib hashes in both oracle identities')),
}

POLICY=('Per-member profiles (opt-in, separate objects only): each canonical member compiles with the profile of its own '
        'hash-checked proof; each new member with the requested profile or a recorded --member-profile hypothesis. '
        'Profiles are mixed only inside one established link-compatibility class; the requested profile links the '
        'unit and compiles the harness. A mixed profile is a per-object option hypothesis, not source-file provenance.')


def link_class(profiles):
    """The one established class containing every profile, else FormatError."""
    profiles=sorted(set(profiles))
    require(profiles,'no compiler profile given')
    if len(profiles)==1:
        for name,item in LINK_CLASSES.items():
            if profiles[0] in item['profiles']:return name
        return 'single-profile:'+profiles[0]
    for name,item in LINK_CLASSES.items():
        if set(profiles)<=set(item['profiles']):return name
    raise_incompatible(profiles)


def raise_incompatible(profiles):
    known=', '.join('%s={%s}'%(n,','.join(i['profiles'])) for n,i in sorted(LINK_CLASSES.items()))
    require(False,'PROFILES_NOT_LINK_COMPATIBLE: %s share no established link-compatibility class '
                  '(same runtime library and ABI); established classes: %s'%(','.join(profiles),known))


def proof_profile(proof,fid):
    """The profile a canonical proof compiled ``fid`` with.

    A per-member profile unit records ``member_profiles`` in its compile
    identity; every other proof compiled all of its objects with ``profile``.
    """
    compiler=proof.get('compiler') or {}
    members=compiler.get('member_profiles')
    profile=members.get(fid) if isinstance(members,dict) and fid in members else compiler.get('profile')
    require(isinstance(profile,str) and profile,'canonical proof names no compiler profile: '+fid)
    if members is None and profile in PROFILE_FLAGS:
        require(list(compiler.get('flags') or [])==PROFILE_FLAGS[profile],'canonical proof flags disagree with its profile: '+fid)
    return profile
