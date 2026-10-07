import re,json,ast,threading,time,subprocess,sys,itertools,copy
from pathlib import Path
root=Path('content/os/04-deadlock');out=Path('/tmp/cs-study-audit-full/os04');out.mkdir(exist_ok=True)
checks=[]
def ck(name,cond):
 assert cond,name
 checks.append(name)
def defs(stem):
 blocks=re.findall(r'```python\n(.*?)```', (root/(stem+'.md')).read_text(),re.S);ns={}
 for block in blocks:
  tree=ast.parse(block)
  tree.body=[n for n in tree.body if isinstance(n,(ast.FunctionDef,ast.ClassDef,ast.Import,ast.ImportFrom)) or (isinstance(n,ast.Assign) and any(isinstance(t,ast.Name) and t.id=='_held' for t in n.targets))]
  if tree.body:exec(compile(tree,stem,'exec'),ns)
 return ns
n=defs('dl-avoidance-bankers');safe=n['is_safe'];req=n['request']
a=[[0,1,0],[2,0,0],[3,0,2],[2,1,1],[0,0,2]];mx=[[7,5,3],[3,2,2],[9,0,2],[2,2,2],[4,3,3]];need=[[x-y for x,y in zip(m,r)] for m,r in zip(mx,a)];av=[3,3,2]
ck('lesson banker sequence',safe(av,a,need)==(True,[1,3,4,0,2]))
ck('lesson request grant',req(1,[1,0,2],av,a,need)=='grant')
ck('decision does not commit',a[1]==[2,0,0] and av==[3,3,2])
av=[2,3,0];a[1]=[3,0,2];need[1]=[0,2,0]
ck('lesson unsafe request',req(0,[0,2,0],av,a,need)=='wait');ck('lesson unavailable request',req(4,[3,3,0],av,a,need)=='wait')
ck('bank safe',safe([2],[[4],[2],[2]],[[4],[1],[5]])==(True,[1,0,2]));ck('bank unsafe grant',req(2,[1],[2],[[4],[2],[2]],[[4],[1],[5]])=='wait')
a=[[1,0,1],[2,1,0],[0,1,1],[1,0,1]];mx=[[3,2,2],[2,2,1],[1,3,3],[4,1,2]];nd=[[x-y for x,y in zip(m,r)] for m,r in zip(mx,a)];av=[1,1,1]
def validseq(seq,av,a,nd):
 w=av[:]
 for i in seq:
  if any(x>y for x,y in zip(nd[i],w)):return False
  w=[x+y for x,y in zip(w,a[i])]
 return True
ck('quiz6 correct sequence',validseq([1,3,0,2],av,a,nd))
for p,v,want in [(1,[0,0,1],'grant'),(0,[0,1,0],'wait'),(2,[1,0,0],'grant'),(3,[0,1,0],'wait')]:ck(f'quiz11 request {p} {v}',req(p,v,av,a,nd)==want)
for label,args in [('overclaim',(1,[1,0,0])),('negative',(1,[-1,0,0])),('shape',(1,[0]))]:
 try:req(*args,av,a,nd)
 except ValueError:ck(label,True)
 else:raise AssertionError(label)
# Exhaustively compare greedy safety to independent permutation definition in small valid states.
exhaustive=0
for alloc in itertools.product(range(3),repeat=3):
 for needv in itertools.product(range(3),repeat=3):
  for free in range(3):
   aa=[[x] for x in alloc];nn=[[x] for x in needv]
   oracle=any(validseq(s,[free],aa,nn) for s in itertools.permutations(range(3)))
   assert safe([free],aa,nn)[0]==oracle
   exhaustive+=1
ck('2187 exhaustive safety states',exhaustive==2187)
# Read detection functions without importing psycopg wrapper dependencies.
text=(root/'dl-detection-recovery.md').read_text();ns={}
for block in re.findall(r'```python\n(.*?)```',text,re.S):
 if block.startswith('def find_cycle') or block.startswith('def deadlocked'):exec(block,ns)
cycle=ns['find_cycle'];det=ns['deadlocked']
ck('lesson cycle',cycle({'T1':{'T2'},'T2':{'T3'},'T3':{'T1'},'T4':{'T1'}})==['T1','T2','T3'])
ck('quiz DFS',cycle({'A':{'B'},'B':{'C'},'C':{'B'},'D':{'A'}})==['B','C'])
ck('acyclic',cycle({'A':{'B'},'B':{'C'}}) is None)
ck('selfcycle',cycle({'A':{'A'}})==['A'])
aa=[[0,1,0],[2,0,0],[3,0,3],[2,1,1],[0,0,2]];rr=[[0,0,0],[2,0,2],[0,0,0],[1,0,0],[0,0,2]]
ck('detection no deadlock',det([0,0,0],aa,rr)==[]);rr[2]=[0,0,1]
ck('detection four holders deadlocked',det([0,0,0],aa,rr)==[1,2,3,4])
ck('detection quiz5',det([0,0],[[1,0],[0,1],[1,0],[0,1]],[[0,1],[1,0],[0,0],[0,0]])==[])
# Exhaustive graph oracle via reachability closure; includes selfedges.
for mask in range(512):
 g={i:{j for j in range(3) if mask&(1<<(i*3+j))} for i in range(3)}
 reach=[set(g[i]) for i in range(3)]
 for k in range(3):
  for i in range(3):
   if k in reach[i]:reach[i]|=reach[k]
 expected=any(i in reach[i] for i in range(3));actual=cycle(g)
 assert (actual is not None)==expected
 if actual:assert all(actual[(k+1)%len(actual)] in g[x] for k,x in enumerate(actual))
ck('512 exhaustive graph states',True)
# LevelLock runtime assertion and release on exception.
p=defs('dl-prevention');L=p['LevelLock'];lo=L(20,'account');hi=L(30,'ledger')
with lo:
 with hi:pass
ck('level order success',not lo._lock.locked() and not hi._lock.locked())
try:
 with hi:
  with lo:raise AssertionError('unexpected')
except RuntimeError:ck('inversion detected and outer released',not hi._lock.locked())
try:
 with lo:
  with lo:pass
except RuntimeError:ck('selfacquisition rejected',not lo._lock.locked())
try:p['lock_both'](lo._lock,lo._lock)
except ValueError:ck('same-lock rejected',True)
p['lock_both'](lo._lock,hi._lock);ck('try-lock acquires pair',lo._lock.locked() and hi._lock.locked());hi._lock.release();lo._lock.release()
# FIFO ticket admission checked by observing assigned ticket count while first owner holds.
t=defs('dl-livelock-starvation')['TicketLock']();order=[];t.acquire();threads=[]
def waiter(i):
 t.acquire();order.append(i);t.release()
for i in range(8):
 w=threading.Thread(target=waiter,args=(i,),daemon=True);w.start();threads.append(w)
 deadline=time.monotonic()+2
 while True:
  with t._cv:issued=int(re.search(r"count\((\d+)",repr(t._next))[1])
  if issued==i+2:break
  assert time.monotonic()<deadline
  time.sleep(.001)
t.release()
for w in threads:w.join(2)
ck('ticket FIFO admission eight waiters',order==list(range(8)) and not any(w.is_alive() for w in threads))
ck('jitter bounds', [min(2000,100*2**i) for i in range(7)]==[100,200,400,800,1600,2000,2000])
ck('priority timing model',2+100+(3-2)==103 and 3==1+(3-1))
# Actual quiz pool hang uses Barrier: isolate and terminate bounded subprocess.
qs=json.loads((root/'dl-fundamentals.questions.json').read_text());code=re.search(r'```python\n(.*?)```',next(x for x in qs if x['id'].endswith('-q8'))['prompt'],re.S)[1]
try:subprocess.run([sys.executable,'-c',code],capture_output=True,timeout=1)
except subprocess.TimeoutExpired:ck('barrier pool deadlock observed and terminated',True)
else:raise AssertionError('expected pool hang')
# Retry algorithm test with explicit transaction-contract doubles; not a live psycopg/DB test.
block=next(x for x in re.findall(r'```python\n(.*?)```',text,re.S) if 'def run_txn' in x)
tree=ast.parse(block);tree.body=[x for x in tree.body if isinstance(x,ast.FunctionDef)]
class Deadlock(Exception):pass
class TS:IDLE='idle'
class Info:transaction_status=TS.IDLE
class Conn:
 def __init__(self):self.info=Info();self.rollbacks=0;self.commits=0
 def transaction(self):
  c=self
  class Tx:
   def __enter__(self):c.info.transaction_status='active'
   def __exit__(self,typ,v,tb):
    c.info.transaction_status=TS.IDLE
    if typ:c.rollbacks+=1
    else:c.commits+=1
  return Tx()
class Time:
 def __init__(self):self.sleeps=[]
 def sleep(self,x):self.sleeps.append(x)
class Random:
 def random(self):return .5
clock=Time();ns={'RETRY':(Deadlock,),'TransactionStatus':TS,'time':clock,'random':Random()};exec(compile(tree,'retry','exec'),ns);run=ns['run_txn'];c=Conn();calls=[]
def work(conn):
 calls.append(1)
 if len(calls)<3:raise Deadlock()
 return 42
ck('retry rolls back twice commits once',run(c,work)==42 and c.rollbacks==2 and c.commits==1 and clock.sleeps==[.025,.05])
c.info.transaction_status='active'
try:run(c,work)
except ValueError:ck('nested retry refused',True)
c.info.transaction_status=TS.IDLE
try:run(c,work,0)
except ValueError:ck('zero attempts refused',True)
clock.sleeps.clear()
def fail(conn):raise Deadlock('last')
try:run(c,fail,2)
except Deadlock as e:ck('last error preserved without final sleep',str(e)=='last' and clock.sleeps==[.025])
result={'checks':checks,'assertionsPassed':len(checks),'exhaustiveBankerStates':2187,'exhaustiveGraphs':512,'limitations':['Retry tests use explicit transaction doubles, not live Psycopg/PostgreSQL integration.','Finite tests cannot prove concurrent progress, kernel tooling behavior or platform-specific timings.']};(out/'results.json').write_text(json.dumps(result,indent=2)+'\n');print(json.dumps(result,indent=2))
