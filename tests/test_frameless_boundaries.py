"""Synthetic fail-closed CFG controls; no corpus counts or fixture mutation."""
import copy
import json
import unittest
import audio_frame_calibration as frame
import audio_frameless_asm as asm
from common import FormatError

def ins(p,m,o='',n=2):
 return dict(offset=p,size=n,mnemonic=m,operands=o)

class BoundaryControls(unittest.TestCase):
 def test_external_branch_requires_explicit_boundary(self):
  items=[ins(0,'bne.b','$8'),ins(2,'rts')]
  with self.assertRaises(FormatError):frame.witness(items,0)
  result=frame.witness(items,0,tail_entries=[8])
  self.assertEqual(result['tail_entries'],[8])
  self.assertEqual(result['reachable_instructions'],[0,2])

 def test_fallthrough_cannot_use_a_tail_binding(self):
  items=[ins(0,'bne.b','$4'),ins(2,'rts'),ins(4,'nop')]
  with self.assertRaisesRegex(FormatError,'fallthrough'):
   frame.witness(items,0,tail_entries=[6])

 def test_unused_or_internal_tail_binding_rejects(self):
  items=[ins(0,'bne.b','$8'),ins(2,'rts')]
  for tails in ([8,10],[0,8]):
   with self.subTest(tails=tails),self.assertRaises(FormatError):
    frame.witness(items,0,tail_entries=tails)

 def test_unknown_path_and_unreachable_instruction_reject(self):
  with self.assertRaises(FormatError):
   frame.witness([ins(0,'bne.b','$8'),ins(2,'bra.b','$a')],0,tail_entries=[8])
  with self.assertRaises(FormatError):
   frame.witness([ins(0,'rts'),ins(2,'rts')],0)

 def test_framed_C_never_becomes_eligible(self):
  with self.assertRaises(FormatError):
   frame.witness([ins(0,'link.w','a5, #$0',4),ins(4,'rts')],0,include_calls=True)

 def test_subroutine_must_be_reached_by_an_actual_internal_call(self):
  items=[ins(0,'bsr.b','$4'),ins(2,'rts'),ins(4,'rts')]
  with self.assertRaises(FormatError):frame.witness(items,0)
  result=frame.witness(items,0,include_calls=True)
  self.assertEqual(result['return_sites'],[2,4])
  self.assertEqual(result['reachable_instructions'],[0,2,4])

 def test_named_vector_requires_exact_operands_and_use(self):
  items=[ins(0,'jsr','-$36(a6)',4),ins(4,'rts')]
  binding={0:dict(kind='TEST_PINNED_VECTOR',symbol='_TestCall',operands='-$36(a6)')}
  with self.assertRaises(FormatError):frame.witness(items,0)
  result=frame.witness(items,0,call_bindings=binding)
  self.assertEqual(result['call_bindings'][0]['symbol'],'_TestCall')
  self.assertEqual(result['call_bindings'][0]['site'],0)
  self.assertEqual(json.loads(json.dumps(result)),result)
  bad=copy.deepcopy(binding);bad[0]['operands']='-$3c(a6)'
  with self.assertRaises(FormatError):frame.witness(items,0,call_bindings=bad)
  bad=copy.deepcopy(binding);bad[6]=dict(binding[0])
  with self.assertRaises(FormatError):frame.witness(items,0,call_bindings=bad)

 def test_binding_cannot_override_a_direct_call(self):
  items=[ins(0,'bsr.w','$8',4),ins(4,'rts')]
  with self.assertRaises(FormatError):
   frame.witness(items,0,call_bindings={0:dict(operands='$8')})

 def test_supplied_edges_are_not_authority(self):
  items=[ins(0,'bne.b','$8'),ins(2,'rts')]
  edges=frame.cfg(items);edges[0]['target']=12
  with self.assertRaises(FormatError):frame.witness(items,0,edges,tail_entries=[8])

 def test_PC_code_address_is_bound_only_for_the_supported_form(self):
  self.assertEqual(asm.pc_target(ins(0,'lea.l','$1234(pc), a2',4)),0x1234)
  for m,o in [('move.l','$1234(pc), a2'),('lea.l','$1234.l, a2'),('lea.l','$1234(pc), d0')]:
   self.assertIsNone(asm.pc_target(ins(0,m,o,4)))

 def test_batch_membership_is_closed(self):
  for facts in ([],['unknown'],asm.FACTS+asm.TAIL_FACTS):
   with self.subTest(facts=facts),self.assertRaises(FormatError):
    asm.batch_config(dict(facts=facts))

if __name__=='__main__':unittest.main()
