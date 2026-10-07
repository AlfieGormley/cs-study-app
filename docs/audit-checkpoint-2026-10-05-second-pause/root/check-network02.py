from pathlib import Path
import re,json,io,contextlib,random,ipaddress,struct,itertools,math
B=Path('/Users/alfiegormley/Github/cs-study-app/content/networks/02-ip-routing')
rng=random.Random(902);checks=0;spaces={};outputs={};fences=0;quizfences=0

def ck(x):
 global checks
 checks+=1
 assert x,checks

def bad(f,*a):
 try:f(*a)
 except (ValueError,TypeError):ck(True)
 else:raise AssertionError((f,a))
for p in B.glob('*.md'):
 ns={};out=io.StringIO()
 for src in re.findall(r'```python\n(.*?)```',p.read_text(),re.S):
  with contextlib.redirect_stdout(out):exec(compile(src,str(p),'exec'),ns)
  fences+=1
 spaces[p.stem]=ns;outputs[p.stem]=out.getvalue()
for p in B.glob('*.questions.json'):
 for q in json.loads(p.read_text()):
  inds=q['answer'] if isinstance(q['answer'],list) else [q['answer']]
  ck(all(type(i)is int and 0<=i<len(q['options']) for i in inds))
  for field in ['prompt','workedExample']:
   for src in re.findall(r'```python\n(.*?)```',q.get(field,''),re.S):
    ns=spaces[p.name.split('.questions')[0]].copy();out=io.StringIO()
    with contextlib.redirect_stdout(out):exec(src,ns)
    outputs[q['id']]=out.getvalue();quizfences+=1
ck(outputs['ip-bgp']=='customer\n');ck(outputs['ip-dhcp']=='5\n3600\n(43200.0, 75600.0)\n')
ck(outputs['ip-dhcp-q7']=='[53, 55] [1, 3, 6]\n');ck(outputs['ip-subnetting-q10']=='error\n')
parse=spaces['ip-ipv4']['parse_ipv4'];frag=spaces['ip-ipv4']['fragment']
for size in range(20):bad(parse,b'\0'*size)
for version in range(16):
 for ihl in range(16):
  pkt=bytes([(version<<4)|ihl,0])+b'\xff\xff'+b'\0'*56
  if version!=4 or ihl<5:bad(parse,pkt)
  else:ck(parse(pkt)['ihl_bytes']==ihl*4)
for _ in range(2000):
 ihl=rng.randint(5,15);total=rng.randint(ihl*4,65535);ff=rng.randrange(65536);ttl=rng.randrange(256);proto=rng.randrange(256)
 src=rng.randbytes(4);dst=rng.randbytes(4)
 pkt=struct.pack('!BBHHHBBH4s4s',64+ihl,0,total,42,ff,ttl,proto,0,src,dst)+b'\0'*(ihl*4-20)
 p=parse(pkt);ck(p['src']==str(ipaddress.IPv4Address(src)));ck(p['dst']==str(ipaddress.IPv4Address(dst)));ck(p['offset']==(ff&8191)*8);ck(p['MF']==bool(ff&8192));ck(p['DF']==bool(ff&16384));ck(p['ttl']==ttl and p['total_len']==total)
 bad(parse,pkt[:ihl*4-1])
for a in [(-1,1500,20),(10,19,20),(10,21,20),(65516,1500,20),(10,1500,21),(10,1500,64),(10.0,1500,20),(True,1500,20)]:bad(lambda *a:list(frag(*a)),*a)
for _ in range(3000):
 h=rng.randrange(20,61,4);d=rng.randrange(65536-h);mtu=rng.randint(h+8,9000);fs=list(frag(d,mtu,h));offset=0
 for i,(off,n,mf) in enumerate(fs):
  ck(off*8==offset);ck(n+h<=mtu);ck(mf==(i<len(fs)-1));ck(not mf or n%8==0);offset+=n
 ck(offset==d)
for prefix in range(33):
 for _ in range(20):
  addr=rng.getrandbits(32);net,mask,br,count=spaces['ip-subnetting']['describe'](f'{ipaddress.IPv4Address(addr)}/{prefix}')
  n=1<<(32-prefix);ck(int(net.network_address)==addr//n*n);ck(int(br)==addr//n*n+n-1);ck(count==(n if prefix>=31 else n-2))
Nat=spaces['ip-nat-ipv6']['NAPT'];nat=Nat('203.0.113.7')
for p in range(1,25537):
 public,port=nat.outbound('10.0.0.1',p);ck(port==39999+p);ck(nat.inbound(port)==('10.0.0.1',p));ck(nat.outbound('10.0.0.1',p)==(public,port))
bad(nat.outbound,'10.0.0.1',25537)
for p in (0,-1,65536,1.5,True):bad(nat.outbound,'10.0.0.2',p)
ck(nat.inbound(39999)is None)
lookup=spaces['ip-routing-basics']['lookup'];routeglobals=lookup.__globals__;old=routeglobals['routes']
for _ in range(2000):
 a=rng.getrandbits(32);expected='isp'
 for prefix,hop in [('10.0.0.0/8','core'),('10.1.0.0/16','dc1'),('10.1.2.0/24','rack7')]:
  if ipaddress.IPv4Address(a) in ipaddress.IPv4Network(prefix):expected=hop
 ck(lookup(str(ipaddress.IPv4Address(a)))==expected)
routeglobals['routes']=[];ck(lookup('10.1.2.3')is None);routeglobals['routes']=old
spf=spaces['ip-interior-routing']['spf']
for _ in range(1000):
 n=rng.randint(1,12);graph={i:[] for i in range(n)};D=[[math.inf]*n for _ in range(n)]
 for i in range(n):
  D[i][i]=0
  for j in range(n):
   if i!=j and rng.random()<.22:
    c=rng.choice([0,1,2,10,10**12]);graph[i].append((j,c));D[i][j]=c
 for k in range(n):
  for i in range(n):
   for j in range(n):D[i][j]=min(D[i][j],D[i][k]+D[k][j])
 for src in range(n):
  dist,hop=spf(graph,src)
  ck(dist=={j:d for j,d in enumerate(D[src]) if d<math.inf})
  for dst,h in hop.items():
   if dst==src:ck(h is None)
   else:ck(any(v==h and c+D[h][dst]==dist[dst] for v,c in graph[src]))
for graph,src in [({},0),({0:[(1,1)]},0),({0:[(0,-1)]},0),({0:[(0,1.5)]},0)]:bad(spf,graph,src)
a,b,c=object(),object(),object();ck(spf({a:[(b,1),(c,1)],b:[],c:[]},a)[0][c]==1)
rank=spaces['ip-bgp']['rank']
for _ in range(2000):
 rs=[dict(lp=rng.randrange(5),path=list(range(rng.randrange(5))),origin=rng.randrange(3),med=rng.randrange(8),ebgp=bool(rng.randrange(2)),igp=rng.randrange(8)) for i in range(10)]
 candidates=rs
 for key,largest in [('lp',True),('path',False),('origin',False),('med',False),('ebgp',True),('igp',False)]:
  value=lambda r:len(r[key]) if key=='path' else r[key]
  target=(max if largest else min)(value(r) for r in candidates);candidates=[r for r in candidates if value(r)==target]
 ck(min(rs,key=rank)==candidates[0])
opts=spaces['ip-dhcp']['parse_options']
for raw in [b'',b'\0',b'\x35',b'\x35\x01',b'\x35\x02\x01',b'\x35\x01\x05']:bad(opts,raw)
for _ in range(3000):
 raw=bytearray();expect={}
 for i in range(rng.randrange(20)):
  code=rng.randint(1,254);part=rng.randbytes(rng.randrange(20));raw.extend([code,len(part)]);raw.extend(part);raw.extend([0]*rng.randrange(3));expect[code]=expect.get(code,b'')+part
 raw.append(255);raw.extend(rng.randbytes(8));ck(opts(bytes(raw))==expect)
timers=spaces['ip-dhcp']['timers']
for l in [0,-1,0xffffffff,0x100000000,True,1.2]:bad(timers,l)
for l in range(1,10000):a,b=timers(l);ck(a==l/2 and b==l*7/8 and 0<a<b<l)
ck(20*19//2==190 and 18*2+1==37);ck(100*99//2==4950)
ck(ipaddress.IPv4Network('192.0.2.0/23').subnet_of(ipaddress.IPv4Network('192.0.0.0/22')))
ck(ipaddress.IPv4Network('203.0.113.0/24').subnet_of(ipaddress.IPv4Network('203.0.112.0/22')))
report={'assertions':checks,'lesson_python_fences':fences,'quiz_python_fences':quizfences,'outputs':outputs,'limitations':['No live BGP/DHCP deployment or PHY tests','Policy-routing shell fence requires separate Linux environment test']}
Path('/tmp/cs-study-audit-2026-10-04/network02-results.json').write_text(json.dumps(report,indent=2)+'\n')
print(json.dumps(report,indent=2))
