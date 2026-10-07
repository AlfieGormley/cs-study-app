import json,re,subprocess,sys,threading,queue,itertools,math
from pathlib import Path
b=Path('content/os/03-synchronisation');out=Path('/tmp/cs-study-audit-full/os03');out.mkdir(exist_ok=True);checks=[]
def ck(n,v):assert v,n;checks.append(n)
def c_run(name,src):
 p=out/(name+'.c');p.write_text(src);exe=p.with_suffix('');subprocess.run(['cc','-std=c11','-O2','-pthread',str(p),'-o',str(exe)],check=True,capture_output=True);z=subprocess.run([str(exe)],capture_output=True,text=True,timeout=30);ck(name,z.returncode==0)
head='#include <pthread.h>\n#include <stdatomic.h>\n#include <assert.h>\n#include <stdio.h>\n#include <stdlib.h>\n'
# Safe atomic counter and lock examples; UB programs intentionally not output-tested.
c_run('atomic-counter',head+'''atomic_int hits=0;
void *run(void*x){for(int i=0;i<100000;i++) atomic_fetch_add_explicit(&hits,1,memory_order_relaxed);return 0;}
int main(){pthread_t t[8];for(int i=0;i<8;i++)assert(!pthread_create(t+i,0,run,0));for(int i=0;i<8;i++)assert(!pthread_join(t[i],0));assert(hits==800000);}
''')
blocks=re.findall(r'```c\n(.*?)```',(b/'sync-locks.md').read_text(),re.S)
for name,code,lock,unlock in [('flag',next(x for x in blocks if 'atomic_flag f' in x),'spin_lock()','spin_unlock()'),('cas',next(x for x in blocks if 'atomic_int l' in x)+'\nvoid cas_unlock(){atomic_store(&l,0);}','cas_lock()','cas_unlock()'),('ticket',next(x for x in blocks if 'atomic_int next' in x),'ticket_lock()','ticket_unlock()')]:
 c_run(name,head+code+'\nint count;\nvoid *work(void*x){for(int i=0;i<10000;i++){'+lock+';count++;'+unlock+';}return 0;}\nint main(){pthread_t t[4];for(int i=0;i<4;i++)assert(!pthread_create(t+i,0,work,0));for(int i=0;i<4;i++)assert(!pthread_join(t[i],0));assert(count==40000);}')
c_run('bad-cas-model',head+'int main(){atomic_int l=1;int expected=0;assert(!atomic_compare_exchange_strong(&l,&expected,1));assert(expected==1);assert(atomic_compare_exchange_strong(&l,&expected,1));assert(l==1);}')
c_run('publication',head+'''int data; atomic_int ready=0;
void *producer(void*x){data=42;atomic_store_explicit(&ready,1,memory_order_release);return 0;}
int main(){pthread_t t;assert(!pthread_create(&t,0,producer,0));while(!atomic_load_explicit(&ready,memory_order_acquire));assert(data==42);assert(!pthread_join(t,0));}
''')
maxcode=re.findall(r'```c\n(.*?)```',(b/'sync-lock-free.md').read_text(),re.S)[0]
c_run('max-seen',head+maxcode+'\nvoid *w(void*x){for(long i=1;i<=100000;i++)record(i);return 0;}\nint main(){pthread_t a,c;assert(!pthread_create(&a,0,w,0));assert(!pthread_create(&c,0,w,0));pthread_join(a,0);pthread_join(c,0);assert(max_seen==100000);}')
# Condition-variable done predicate, both completion-before-wait and wait-before-completion.
code=next(x for x in re.findall(r'```c\n(.*?)```',(b/'sync-semaphores-condvars.md').read_text(),re.S) if 'void thr_exit' in x)
c_run('condvar',head+code+'\nvoid *child(void*x){thr_exit();return 0;}\nint main(){thr_exit();thr_join();done=0;pthread_t t;pthread_create(&t,0,child,0);thr_join();pthread_join(t,0);assert(done==1);}')
# Enumerate all SC load/store interleavings for 1..4 increments each.
from functools import lru_cache
for n in range(1,5):
 @lru_cache(None)
 def states(a,c,val,ra,rb):
  if a==2*n and c==2*n:return frozenset([val])
  z=set()
  if a<2*n:z.update(states(a+1,c,val,val,rb) if a%2==0 else states(a+1,c,ra+1,ra,rb))
  if c<2*n:z.update(states(a,c+1,val,ra,val) if c%2==0 else states(a,c+1,rb+1,ra,rb))
  return frozenset(z)
 vals=states(0,0,0,0,0);ck('SC increments '+str(n),min(vals)==(1 if n==1 else 2) and max(vals)==2*n)
# SC store-buffering outcomes independently enumerate legal total orders.
results=set()
for order in itertools.permutations('ABCD'):
 if order.index('A')>order.index('B') or order.index('C')>order.index('D'):continue
 x=y=0;r1=r2=None
 for op in order:
  if op=='A':x=1
  elif op=='B':r1=y
  elif op=='C':y=1
  else:r2=x
 results.add((r1,r2))
ck('SC excludes both-zero',results=={(0,1),(1,0),(1,1)})
ck('Amdahl16',math.isclose(1/(.1+.9/16),6.4));ck('Amdahlhalf',math.isclose(1/(.05+.95/16),64/7));ck('queuepayload',(50000-20000)*3600*200==21600000000);ck('Littlelaw',5000*.002==10);ck('tagyears',584<2**64/10**9/(365.25*24*3600)<585)
# Python API contracts and actual corrected snapshot implementation.
s=threading.Semaphore(0);s.release();s.release();ck('remembered semaphore',[s.acquire(False) for _ in range(3)]==[True,True,False])
s=threading.BoundedSemaphore(1)
try:s.release();raise AssertionError('missing error')
except ValueError:ck('bounded overrelease',True)
cv=threading.Condition()
try:cv.notify();raise AssertionError('missing lock error')
except RuntimeError:ck('notify requires lock',True)
ck('true wait_for can return before ownership check',cv.wait_for(lambda:True) is True)
try:cv.wait_for(lambda:False,timeout=.001);raise AssertionError('missing wait lockerror')
except RuntimeError:ck('false wait_for checks lock',True)
code=re.findall(r'```python\n(.*?)```',(b/'sync-lock-free.md').read_text(),re.S)[0];ns={};exec(code,ns);old=ns['get_config']();ns['set_timeout'](99);ck('immutable snapshot',old['timeout']==10 and ns['get_config']()['timeout']==99)
# Actual sleeping barber sketch with finite work and deliberately slow scheduling.
code=re.findall(r'```python\n(.*?)```',(b/'sync-classic-problems.md').read_text(),re.S)[1];ns={};exec(code,ns);served=[];stop=threading.Event()
def cut():served.append(1)
ns['cut_hair']=cut;barber=threading.Thread(target=ns['barber'],daemon=True);barber.start()
clients=[threading.Thread(target=ns['customer']) for _ in range(25)]
for t in clients:t.start()
for t in clients:t.join(3)
ck('barber clients finish',all(not t.is_alive() for t in clients));ck('barber seat invariant',0<=ns['free_seats']<=3);ck('barber makes progress',len(served)>0)
# Nonrecursive Lock example actually hangs, isolated and killed.
qs=json.loads((b/'sync-locks.questions.json').read_text());code=re.search(r'```python\n(.*?)```',next(x for x in qs if x['id'].endswith('q12'))['prompt'],re.S).group(1);p=out/'selfdeadlock.py';p.write_text(code)
try:subprocess.run([sys.executable,str(p)],timeout=1,capture_output=True);raise AssertionError('missing deadlock')
except subprocess.TimeoutExpired:ck('self deadlock',True)
count=0
for p in b.glob('*.questions.json'):
 for q in json.loads(p.read_text()):
  a=q['answer'] if isinstance(q['answer'],list) else [q['answer']];assert all(0<=i<len(q['options']) for i in a);count+=1
ck('all answer indices',count==68)
(out/'results.json').write_text(json.dumps({'assertionsPassed':len(checks),'checks':checks,'compiledCPrograms':8,'scope':'Native Darwin arm64 runtime; SC toy enumeration, not hardware weak-memory proof; no UB output claims.'},indent=2));print(len(checks),'checks passed',count,'questions')
