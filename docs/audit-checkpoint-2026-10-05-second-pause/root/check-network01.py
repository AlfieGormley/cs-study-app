from pathlib import Path
import re, json, io, contextlib, random, struct, itertools, math, zlib
root=Path('content/networks/01-foundations'); ns={}; outputs={}; count=0
def check(v):
 global count
 assert v
 count+=1
def raises(fn):
 try: fn()
 except ValueError: check(True)
 else: raise AssertionError('expected ValueError')
for p in root.glob('*.md'):
 for i,code in enumerate(re.findall(r'```python\n(.*?)```',p.read_text(),re.S)):
  out=io.StringIO()
  with contextlib.redirect_stdout(out):exec(compile(code,str(p),'exec'),ns)
  outputs[p.stem+':'+str(i)]=out.getvalue()
expected={'nf-ethernet:0':'[2, 3, 4]\n[1]\n[2]\n','nf-arp-switching:0':'28\n00010800 06040001 3c22fb11\n2233c0a8 01140000 00000000\nc0a80101\n','nf-physical-layer:0':'[0, 1, 1, 0, 0, 1, 0, 1]\n','nf-performance:0':'5.26 ms\n','nf-layered-models:0':"('ff:ff:ff:ff:ff:ff', '3c:22:fb:11:22:33', '0x806')\n",'nf-error-control:0':'0xb861\nTrue\n','nf-error-control:1':'011\n','nf-error-control:2':'0xcbf43926\nTrue\n'}
check(outputs==expected)
rng=random.Random(61)
for n in range(14):raises(lambda n=n:ns['parse_eth'](bytes(n)))
for _ in range(1000):
 dst=rng.randbytes(6);src=rng.randbytes(6);eth=rng.randrange(65536);payload=rng.randbytes(rng.randrange(100))
 check(ns['parse_eth'](dst+src+eth.to_bytes(2,'big')+payload)==(dst.hex(':'),src.hex(':'),hex(eth),payload))
for n in range(11):
 for bits in itertools.product('01',repeat=n):
  text=''.join(bits);out=ns['manchester'](text)
  check(len(out)==2*n)
  check(''.join(str(out[i+1]) for i in range(0,2*n,2))==text)
  check(all(out[i]+out[i+1]==1 for i in range(0,2*n,2)))
raises(lambda:ns['manchester']('102'))
for args in [(-1,1,1),(1,0,1),(1,1,-1)]:raises(lambda args=args:ns['hop_delay'](*args))
for _ in range(1000):
 bits=rng.randrange(100000);rate=rng.randrange(1,1000000000);km=rng.random()*1000
 check(math.isclose(ns['hop_delay'](bits,rate,km),bits/rate+km/200000))
mac=bytes.fromhex('001122334455')
for n in [0,1,5,7,20]:raises(lambda n=n:ns['arp_request'](bytes(n),'192.0.2.1','192.0.2.2'))
raises(lambda:ns['arp_request'](mac,'999.1.1.1','192.0.2.2'))
for _ in range(1000):
 a=rng.randbytes(4);b=rng.randbytes(4);aip='.'.join(map(str,a));bip='.'.join(map(str,b));pkt=ns['arp_request'](mac,aip,bip)
 check(pkt==b'\x00\x01\x08\x00\x06\x04\x00\x01'+mac+a+bytes(6)+b)
# Independent integer polynomial division oracle.
def rem(value,gen):
 while value.bit_length()>=gen.bit_length():value^=gen<<(value.bit_length()-gen.bit_length())
 return value
for degree in range(1,7):
 for gen in range((1<<degree)|1,1<<(degree+1),2):
  for width in range(1,9):
   for value in range(1<<width):
    actual=ns['crc_remainder'](format(value,'0'+str(width)+'b'),format(gen,'b'))
    check(int(actual,2)==rem(value<<degree,gen))
    check(rem((value<<degree)|int(actual,2),gen)==0)
for data,gen in [('', '11'),('012','11'),('1',''),('1','1'),('1','0101'),('1','110'),('1','12')]:raises(lambda data=data,gen=gen:ns['crc_remainder'](data,gen))
check(rem(int('101010011',2),int('1001',2))==4)
check(ns['crc_remainder']('1101','1011')=='001')
for n in range(2000):
 data=rng.randbytes(n%513);words=data+b'\0'*(len(data)%2)
 total=sum(int.from_bytes(words[i:i+2],'big') for i in range(0,len(words),2))
 while total>>16:total=(total&65535)+(total>>16)
 check(ns['inet_checksum'](data)==(~total&65535))
 check(ns['crc32'](data)==zlib.crc32(data))
check(ns['inet_checksum'](bytes.fromhex('4500007300004000'))==0x7a8c)
# Learning/forwarding behaviour against an independent last-observed trace.
sw=ns['Switch']([1,2,3,4]);history=[]
for _ in range(10000):
 port=rng.randrange(1,5);src=rng.choice('ABCD');dst=rng.choice('ABCDZ');history.append((src,port))
 known=next((p for m,p in reversed(history) if m==dst),None)
 target=([p for p in [1,2,3,4] if p!=port] if known is None else [] if known==port else [known])
 check(sw.receive(port,src,dst)==target)
raises(lambda:sw.receive(5,'A','B'))
# ARQ sequence-space counterexamples and corrected deterministic loss quizzes.
for k in range(1,10):
 M=2**k
 for w in range(1,M):
  old=set(range(w));new={(w+i)%M for i in range(w)}
  check(bool(old&new)==(2*w>M))
 check(M%M==0);check((M-1)%M!=0)
check(math.ceil((.03+12000/1e9)/(12000/1e9))==2501)
check(math.ceil((.01+10000/1e9)/(10000/1e9))==1001)
p=1-(1-1e-6)**12000
check(round(100*p,4)==1.1928)
check(round(100*(1-p)/(1+2500*p),2)==3.21)
# Static syntax/codes in all question fields; mathematical text examples separately recomputed above.
question_fences=[]
def visit(v):
 if isinstance(v,str):question_fences.extend(re.findall(r'```([^\n]*)\n(.*?)```',v,re.S))
 elif isinstance(v,list):
  for x in v:visit(x)
 elif isinstance(v,dict):
  for x in v.values():visit(x)
for p in root.glob('*.questions.json'):visit(json.loads(p.read_text()))
for lang,code in question_fences:
 if lang=='python':exec(compile(code,'quiz','exec'),dict(ns))
result={'assertions':count,'python_lesson_fences':len(outputs),'python_question_fences':sum(x[0]=='python' for x in question_fences),'outputs':outputs,'scope':'Offline algorithm, encoding and arithmetic checks. No network/PHY/performance hardware validation.'}
Path('/tmp/cs-study-audit-2026-10-04/network01-results.json').write_text(json.dumps(result,indent=2))
print(json.dumps(result,indent=2))
