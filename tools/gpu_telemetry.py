"""Best-effort GPU observations; absent measurements remain null."""
import csv
import io
import subprocess
import threading
import time


def snapshot():
    try:
        p=subprocess.run(['nvidia-smi','--query-gpu=index,name,memory.total,memory.free,memory.used,utilization.gpu',
                          '--format=csv,noheader,nounits'],capture_output=True,text=True,timeout=3)
        if p.returncode:return None
        rows=list(csv.reader(io.StringIO(p.stdout)))
        if not rows:return None
        r=[x.strip() for x in rows[0]]
        return dict(index=int(r[0]),name=r[1],total_mib=int(r[2]),free_mib=int(r[3]),used_mib=int(r[4]),
                    utilization_percent=int(r[5]),observed_unix=time.time(),scope='WHOLE_GPU_INCLUDING_DESKTOP')
    except (OSError,ValueError,subprocess.TimeoutExpired):return None


class Sampler:
    def __init__(self,interval=0.5):
        self.interval=interval;self.samples=[];self.stop_event=threading.Event()
    def __enter__(self):
        first=snapshot()
        if first:self.samples.append(first)
        self.thread=threading.Thread(target=self._run,daemon=True);self.thread.start();return self
    def _run(self):
        while not self.stop_event.wait(self.interval):
            sample=snapshot()
            if sample:self.samples.append(sample)
    def __exit__(self,*args):
        self.stop_event.set();self.thread.join(timeout=4)
        last=snapshot()
        if last:self.samples.append(last)
    def summary(self):
        return dict(start=self.samples[0] if self.samples else None,end=self.samples[-1] if self.samples else None,
                    peak_observed_used_mib=max((x['used_mib'] for x in self.samples),default=None),
                    minimum_observed_free_mib=min((x['free_mib'] for x in self.samples),default=None),
                    sample_count=len(self.samples),sample_interval_seconds=self.interval,
                    scope='WHOLE_GPU_INCLUDING_DESKTOP; sampled peak, not allocation high-water mark')
