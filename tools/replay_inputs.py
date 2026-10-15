"""One content scan with fresh, parent-batched canonical path checks.

No stat-based content cache: every listed file is read and hashed on each scan.
Directory targets are resolved once per scan; leaf reparse points are resolved
individually. A later scan rechecks every directory and leaf target.
"""
from pathlib import Path
import os,stat
from common import require,sha256
from repo_paths import _canonical_path,resolved_root

class ContentScan:
 def __init__(self,root):
  self.root=resolved_root(root);self.parents={};self.targets={};self.values={};self.raw={}
 def canonical(self,path,*,scratch=False):
  request=(self.root/Path(path),scratch)
  if request in self.targets:return self.targets[request]
  path=Path(os.path.abspath(request[0]))
  if path==self.root:return self.root
  parent=path.parent
  # Parent caches are separate for active and explicit scratch inputs.
  cache_key=(parent,scratch)
  if cache_key not in self.parents:
   if scratch:
    resolved=parent.resolve();require(resolved.is_relative_to(self.root) and 'to_delete' not in [p.lower() for p in resolved.relative_to(self.root).parts],'candidate input escapes repository or enters quarantine')
    self.parents[cache_key]=resolved
   else:self.parents[cache_key]=_canonical_path(self.root,parent)
  target=self.parents[cache_key]/path.name
  from repo_paths import IGNORED_PARTS
  forbidden={'to_delete'} if scratch else IGNORED_PARTS
  require(not any(p.lower() in forbidden for p in target.relative_to(self.root).parts),'canonical input is outside active repository: '+str(path))
  try:info=target.lstat()
  except FileNotFoundError:
   self.targets[request]=target;return target
  if stat.S_ISLNK(info.st_mode) or getattr(info,'st_file_attributes',0)&0x400:
   target=target.resolve()
   require(target.is_relative_to(self.root),'candidate input escapes repository')
  # The parent check cannot detect a quarantined leaf directory/file name.
  relative=target.relative_to(self.root)
  require(not any(p.lower() in forbidden for p in relative.parts),'canonical input is outside active repository: '+str(path))
  self.targets[request]=target
  return target
 def read(self,path,*,scratch=False):
  target=self.canonical(path,scratch=scratch);name=str(target)
  if name not in self.values:
   try:raw=target.read_bytes()
   except FileNotFoundError:raw=None
   self.raw[name]=raw;self.values[name]=sha256(raw) if raw is not None else None
  return self.raw[name]
