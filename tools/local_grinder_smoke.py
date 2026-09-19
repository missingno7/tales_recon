"""Live-model calibration and cache replay; never counts previously owned bytes anew."""
import argparse
import json
from pathlib import Path
import time
import uuid
from common import require,sha256,write_json
from recovery_state import ROOT,facts,recovery
from local_model_proposer import propose
from check_function import check_many


def run(ids):
    before=recovery()['functions'];started=time.time();requests=[];proposals=[]
    for fid in ids:
        require(fid in before,'calibration requires an already verified function')
        package=facts(fid)
        # No previous solution or mismatch for this target is given to the model.
        package['previous_attempts']=[];package['previous_sources']={}
        result=propose(package);replay=propose(package)
        require(replay['proposer_cache_hit'] and replay['source']==result['source'],'model replay did not reuse result')
        path=ROOT/'recovery/candidates'/fid/(sha256(result['source'].encode())+'.c')
        path.parent.mkdir(parents=True,exist_ok=True);path.write_text(result['source'],encoding='ascii',newline='\n')
        requests.append(dict(id=fid,source=str(path),profiles=['aztec36'],proposer_receipt=result['proposer_receipt']))
        proposals.append(dict(id=fid,receipt=result['proposer_receipt'],model_metrics=result['local_model_metrics'],
                              response_cache_replay_hit=True))
    first=check_many(requests,False)
    first_oracle=json.loads((ROOT/'build/compiler-last-run.json').read_text())
    second=check_many(requests,False)
    replay_oracle=json.loads((ROOT/'build/compiler-last-run.json').read_text())
    require(all(r['cache_hit'] for r in second),'historical compile replay missed cache')
    require(replay_oracle['worker_invocations']==0,'compile replay launched a worker')
    require(before==recovery()['functions'],'calibration changed canonical source ownership')
    report=dict(schema_version=1,kind='LIVE_LOCAL_CALIBRATION_NOT_NEW_RECOVERY',
        source_of_candidates='Resident local model; no fixture proposer, target source or previous target attempts supplied',
        proposals=proposals,comparisons=[{k:r.get(k) for k in ('id','verdict','expected_length','actual_length','cache_hit','source_sha256','proposer')} for r in first],
        first_oracle=first_oracle,replay_oracle=replay_oracle,canonical_ownership_unchanged=True,
        newly_recovered_functions=0,newly_recovered_bytes=0,elapsed_seconds=time.time()-started)
    path=ROOT/'recovery/calibrations'/(uuid.uuid4().hex+'.json');write_json(path,report)
    first_receipt=ROOT/'evidence/experiments/local-grinder-calibration.json'
    if not first_receipt.exists():write_json(first_receipt,report)
    print(json.dumps(dict(report=str(path),results=report['comparisons'],newly_recovered_bytes=0),indent=2))


if __name__=='__main__':
    ap=argparse.ArgumentParser(description=__doc__)
    ap.add_argument('--ids',nargs='+',default=['ov14_F_03AE','ov04_F_00E6','ov11_F_4A92'])
    run(ap.parse_args().ids)
