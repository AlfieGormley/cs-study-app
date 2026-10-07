import re,struct,random,math,io,contextlib
from pathlib import Path
s=Path('content/networks/04-application/app-dns-wire.md').read_text();ns={};out=io.StringIO();codes=re.findall(r'```python\n(.*?)```',s,re.S)
with contextlib.redirect_stdout(out):
 for code in codes:exec(code,ns)
assert out.getvalue()=='29\nab cd 01 00\n'
count=1
def ck(v):
 global count
 assert v;count+=1
f=ns['build_query']
for name,size in [('example.com',29),('example.com.',29),('api.service.io',32),('mail.example.org',34),('.',17),('.'.join(['a'*63]*3+['b'*61]),271)]:
 wire=f(name,qid=123);ck(len(wire)==size);ck(struct.unpack('!HHHHHH',wire[:12])==(123,256,1,0,0,0));ck(wire[-4:]==b'\0\1\0\1')
for name in ['', '..','a..b','a'*64,'.'.join(['a'*63]*4),'é.example']:
 try:f(name)
 except (ValueError,UnicodeError):ck(True)
 else:raise AssertionError(name)
for kw in [{'qid':-1},{'qid':65536},{'qid':True},{'qtype':-1},{'qtype':65536},{'qtype':1.5}]:
 try:f('example.com',**kw)
 except ValueError:ck(True)
 else:raise AssertionError(kw)
r=random.Random(12)
for _ in range(10000):
 labels=[''.join(r.choice('abcxyz0123456789')for _ in range(r.randrange(1,25)))for _ in range(r.randrange(1,5))];name='.'.join(labels);qid=r.randrange(65536);qt=r.randrange(65536);wire=f(name,qt,qid)
 ck(len(wire)==12+sum(len(x)+1 for x in labels)+1+4)
 i=12;decoded=[]
 while wire[i]:
  length=wire[i];i+=1;decoded.append(wire[i:i+length].decode());i+=length
 ck(decoded==labels);ck(wire[i+1:]==struct.pack('!HH',qt,1))
ck(0xc00c&0x3fff==12);ck(0x8183&15==3);ck(not(0x8183&0x200));ck(0x10e==270)
for guesses,expected in [(1,45426),(100,454),(200,227)]:
 p=guesses/65536;trials=math.ceil(math.log(.5)/math.log1p(-p));ck(trials==expected);ck(1-(1-p)**trials>=.5);ck(1-(1-p)**(trials-1)<.5)
ck(28000*65536==1835008000);ck(1280-40-8==1232)
print('PASS',count,'assertions;',len(codes),'actualPythonfences; offline wire encoding/model checks, no externalDNS or DNSSEC cryptographic validation')
