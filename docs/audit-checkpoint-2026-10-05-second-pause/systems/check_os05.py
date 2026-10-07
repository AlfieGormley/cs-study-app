import re,subprocess,json,itertools,contextlib,io,math,sys
from pathlib import Path
b=Path('content/os/05-memory');out=Path('/tmp/cs-study-audit-full/os05');out.mkdir(exist_ok=True);checks=[]
def ok(n,x):
 assert x,n
 checks.append(n)
def blocks(name,lang):return re.findall(r'```'+lang+r'\n(.*?)```',(b/(name+'.md')).read_text(),re.S)
ns={}
for s in blocks('mem-page-replacement','python'):
 with contextlib.redirect_stdout(io.StringIO()):exec(s,ns)
lru=ns['lru_faults'];clock=ns['clock_victim']
def fifo(s,n):
 mem=[];f=0
 for p in s:
  if p not in mem:
   f+=1
   if len(mem)==n:mem.pop(0)
   mem.append(p)
 return f
def optimal(s,n):
 mem=set();f=0
 for i,p in enumerate(s):
  if p not in mem:
   f+=1
   if len(mem)==n:
    def nex(x):
     try:return s.index(x,i+1)
     except ValueError:return len(s)
    mem.remove(max(mem,key=nex))
   mem.add(p)
 return f
cases=[([1,2,3,1,4,1,2,5],3,(7,6,5)),([1,2,3,4,1,2,5,1,2,3,4,5],3,(9,10,7)),([1,2,3,4,1,2,5,1,2,3,4,5],4,(10,8,6)),([7,0,1,2,0,3,0,4],3,(7,6,6)),([7,0,1,2,0,3,0,4,2,3,0,3,2],3,(10,9,7)),([1,2,3,4,1,2,3,4],3,(8,8,5))]
for i,(s,n,w) in enumerate(cases):ok('replacement answer '+str(i),(fifo(s,n),lru(s,n),optimal(s,n))==w)
c=0
for tup in itertools.product(range(4),repeat=6):
 s=list(tup)
 for n in [1,2,3]:
  last={};mem=set();f=0
  for i,p in enumerate(s):
   if p not in mem:
    f+=1
    if len(mem)==n:mem.remove(min(mem,key=lambda x:last[x]))
    mem.add(p)
   last[p]=i
  assert f==lru(s,n)
  assert optimal(s,n)<=f and lru(s,n+1)<=f
  c+=1
ok('12288 exhaustive LRU/OPT stack oracle cases',c==12288)
for n in [0,-1]:
 try:lru([1],n);raise AssertionError
 except ValueError:pass
ok('invalid capacities rejected',True)
a=[1,0,1,1];ok('clock quiz',clock([3,8,5,6],a,2)==1 and a==[0,0,0,0]);a=[1]*4;ok('clock allones',clock([1,2,3,4],a,2)==2 and a==[0]*4)
s=blocks('mem-paging','python');nn={}
with contextlib.redirect_stdout(io.StringIO()):
 try:exec(s[0],nn)
 except MemoryError:pass
 exec(s[1],nn)
ok('translation results',nn['translate'](0x3a7c)==0x7a7c and nn['translate'](0x123)==0x5123)
ok('index split lesson',nn['split'](0x7ffd4a3b2c18)==(255,501,81,434,3096))
ok('index split quiz',nn['split'](0x4020123456)==(0,256,256,291,0x456))
ok('huge offset',0x145678+0x40000000==0x40145678)
ok('flat48bit table',2**48//4096*8==512*2**30)
ok('page table 100process footprint',100*64*2**20==6.25*2**30)
ok('buddy xor',0x6000^0x2000==0x4000 and 0x18000^0x8000==0x10000)
ok('slab packing',divmod(8192,700)==(11,492) and divmod(4096,700)==(5,596))
ok('jemalloc rounding',math.isclose(63/320,0.196875))
ok('retention toy survival',math.isclose(0.95**64,0.037524139211116,rel_tol=1e-12))
ok('record pool',10**7*32==320000000 and 10**7*20==200000000)
ok('fault model',64*2**20//4096==16384 and 16384*200==3276800)
ok('bounded pool budget',48*64*2**20==3*2**30)
ok('commit arithmetic',math.isclose(4+32*.8,29.6) and 8+64*.5==40)
ok('PSS arithmetic',40+100/4==65 and 30+240/8==60)
ok('oom score model',6/16*1000==375 and 2/16*1000+500==625)
ok('tmpfs and payload units',2336/1024==2.28125 and math.isclose(10000000/2**20,9.5367431640625))
for name in ['mem-address-spaces','mem-page-faults']:
 src=blocks(name,'c')[0];p=out/(name+'.c');p.write_text(src);exe=out/name
 subprocess.run(['clang','-Wall','-Wextra','-O0',str(p),'-o',str(exe)],check=True,capture_output=True)
 r=subprocess.run([str(exe)],check=True,capture_output=True,text=True);(out/(name+'.output')).write_text(r.stdout)
 if name=='mem-address-spaces':
  lines=r.stdout.splitlines();aa=[x.split() for x in lines];assert aa[0][1]==aa[1][1] and aa[0][2]=='2' and aa[1][2]=='1'
 else:assert int(r.stdout.split()[0])>0
 ok('compiled host '+name,True)
tr=blocks('mem-in-practice','python')[0];nn={}
with contextlib.redirect_stdout(io.StringIO()):exec(tr,nn)
ok('tracemalloc retained payload',len(nn['cache'])==1000 and sum(map(len,nn['cache']))==10000000)
x=next(i for i in json.load(open('content/diagram-overrides.json')) if i['id']=='virtual-memory-regions')
ok('override source and semantic labels','four-level' in x['title'] and 'normally unmapped' in str(x['diagram']) and 'lower canonical limit' in str(x['diagram']) and x['source'] in (b/'mem-address-spaces.md').read_text())
(out/'results.json').write_text(json.dumps({'checkGroupsPassed':len(checks),'checks':checks,'exhaustiveCases':c,'environment':sys.version},indent=2));print(len(checks),'check groups passed;',c,'exhaustive cases')
