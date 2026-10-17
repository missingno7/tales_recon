"""Compatibility hook for pinned amitools/vamos 0.8.1.

Aztec 3.6a calls OpenLibrary("environment"). This name is missing from
amitools' config, and this compile only requires the normal unresolved-library
result (NULL).
"""
from amitools.vamos.libmgr.cfg import LibMgrCfg

_original_get_cfg = LibMgrCfg.get_cfg


def _get_cfg(self, names, allow_default=True):
    if names == "environment":
        return self.get_lib_default()
    return _original_get_cfg(self, names, allow_default)


LibMgrCfg.get_cfg = _get_cfg
