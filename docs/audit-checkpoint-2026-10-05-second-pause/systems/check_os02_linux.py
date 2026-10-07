import os,json
checks=[]
def ck(n,v):
 assert v,n
 checks.append(n)
initial=os.sched_getaffinity(0);ordered=sorted(initial)
try:
 os.sched_setaffinity(0,{ordered[0]});ck('restrict affinity',os.sched_getaffinity(0)=={ordered[0]})
 replacement={ordered[-1]};os.sched_setaffinity(0,replacement);ck('replace not intersect mask',os.sched_getaffinity(0)==replacement)
 pid=os.fork()
 if pid==0:os._exit(0 if os.sched_getaffinity(0)==replacement else 1)
 ck('fork inherits affinity',os.waitpid(pid,0)[1]==0)
finally:os.sched_setaffinity(0,initial)
ck('restored affinity',os.sched_getaffinity(0)==initial)
ck('FIFO min',os.sched_get_priority_min(os.SCHED_FIFO)==1);ck('FIFO max',os.sched_get_priority_max(os.SCHED_FIFO)==99)
ck('RR min',os.sched_get_priority_min(os.SCHED_RR)==1);ck('RR max',os.sched_get_priority_max(os.SCHED_RR)==99)
ck('normal priority zero',os.sched_get_priority_min(os.SCHED_OTHER)==os.sched_get_priority_max(os.SCHED_OTHER)==0)
# Child only: leave parent policy unchanged, no realtime privileged busyloop.
pid=os.fork()
if pid==0:
 try:os.sched_setscheduler(0,os.SCHED_IDLE,os.sched_param(0));os._exit(0 if os.sched_getscheduler(0)==os.SCHED_IDLE else 2)
 except Exception:os._exit(3)
ck('unprivileged SCHED_IDLE policy',os.waitpid(pid,0)[1]==0)
print(json.dumps({'assertionsPassed':len(checks),'checks':checks,'kernel':os.uname().release,'architecture':os.uname().machine}))
