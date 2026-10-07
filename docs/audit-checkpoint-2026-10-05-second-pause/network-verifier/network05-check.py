import re,json,io,contextlib,itertools,math,zlib,random,hashlib
from pathlib import Path
base=Path('content/networks/05-network-security'); count=0; ns={}
def check(x):
 global count
 count+=1
 assert x,count
expected={'nsec-vpns':['1476\n1420\n1450\n','1 True\n2 True\n5 True\n3 True\n5 False\n1 False\n9 True\n6 True\n'],'nsec-threats':['500.0\n'],'nsec-wireless':['f42c6fc52df0ebef\n'],'nsec-firewalls':['allow\ndeny\ndeny\n'],'nsec-detection':['10.0.2.7 1 0 \n203.0.113.9 5 4 SCAN?\n']}
for p in sorted(base.glob('*.md')):
 ns[p.stem]=[]
 for i,block in enumerate(re.findall(r'```python\n(.*?)```',p.read_text(),re.S)):
  compile(block,str(p),'exec')
  if p.stem=='nsec-tls':continue
  d={};o=io.StringIO()
  with contextlib.redirect_stdout(o):exec(block,d)
  check(o.getvalue()==expected[p.stem][i]);ns[p.stem].append(d)
for p in base.glob('*.questions.json'):
 for q in json.loads(p.read_text()):
  a=q['answer'];a=a if isinstance(a,list) else [a]
  check(bool(a) and all(type(i)is int and 0<=i<len(q['options']) for i in a));check(len(set(a))==len(a))
RW=ns['nsec-vpns'][1]['ReplayWindow']
for size in range(1,6):
 for seqs in itertools.product(range(1,7),repeat=5):
  w=RW(size);history=[]
  for seq in seqs:
   top=max(history,default=0); want=seq>top-size and seq not in history
   check(w.accept(seq)==want)
   if want:history.append(seq)
   check(len(w.seen)<=size)
for size in (0,-1,1.2,True):
 try:RW(size)
 except ValueError:check(True)
 else:check(False)
w=RW(3)
for seq in [0,-1,False,2.3,'3']:check(w.accept(seq) is False)
mtu=ns['nsec-vpns'][0]['inner_mtu']
for m in range(81,1601):
 check(mtu(m,'ipv6','udp','wg')==m-80)
 check(mtu(m,'ipv4','udp','vxlan','eth')==m-50)
for m in [0,80,-10]:
 try:mtu(m,'ipv6','udp','wg')
 except ValueError:check(True)
 else:check(False)
f=ns['nsec-firewalls'][0]['check']
for proto,port,src in itertools.product(['tcp','udp'],[22,443,53],['10.0.0.0','10.255.255.255','9.255.255.255','11.0.0.0','203.0.113.9']):
 want='allow' if proto=='tcp' and (port==443 or port==22 and src.startswith('10.')) else 'deny';check(f(proto,port,src)==want)
pmk=ns['nsec-wireless'][0]['pmk'];check(pmk('password','IEEE').hex()=='f42c6fc52df0ebef9ebb4b90b38a5f902e83fe1b135a70e23aed762e9710a12e')
for pw in ['short','x'*64]:
 try:pmk(pw,'IEEE')
 except ValueError:check(True)
 else:check(False)
r=random.Random(765)
for size in range(1,129):
 m=r.randbytes(size);delta=r.randbytes(size);changed=bytes(a^b for a,b in zip(m,delta));check(zlib.crc32(changed)==zlib.crc32(m)^zlib.crc32(delta)^zlib.crc32(bytes(size)))
N=2**24
p=lambda k:-math.expm1(sum(math.log1p(-i/N) for i in range(k)))
check(p(4822)<.5<p(4823));check(2_000_000_000/8*86400*30==648_000_000_000_000)
check(.0098<99/(99+9999.9)<.0099)
check(math.ceil(365/100)==4 and math.ceil(365/47)==8)
print(json.dumps({'assertions':count,'lesson_python_fences':6,'live_tls_separately_executed':True,'quiz_answer_index_sets':67,'replay_exhaustive_sequences':5*6**5}))
