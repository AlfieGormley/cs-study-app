from pathlib import Path
import re,random,math,struct,contextlib,io
src=Path('content/networks/04-application/app-ntp-ssh-grpc.md').read_text();fences=re.findall(r'```python\n(.*?)```',src,re.S);ns={};count=0
with contextlib.redirect_stdout(io.StringIO()) as captured:
 for c in fences:exec(c,ns)
assert captured.getvalue()=='0.13 0.04\n00 00 00 00 07 08 96 01 12 02 68 69\n';count+=1
rng=random.Random(52)
for _ in range(10000):
 a,b,p=[rng.uniform(0,1) for i in range(3)];offset=rng.uniform(-100,100);start=rng.uniform(-1000,1000)
 got,delay=ns['ntp'](start,start+offset+a,start+offset+a+p,start+a+p+b)
 assert math.isclose(got,offset+(a-b)/2,abs_tol=1e-11);assert math.isclose(delay,a+b,abs_tol=1e-11);count+=2
 v=rng.randrange(2**64);encoded=ns['pb_varint'](v);decoded=sum((x&127)<<(7*i) for i,x in enumerate(encoded));assert decoded==v;assert len(encoded)<=10 and encoded[-1]<128;count+=2
for v in [-1,2**64,True,0.5,'1']:
 try:ns['pb_varint'](v)
 except ValueError:count+=1
 else:raise AssertionError(v)
assert ns['frame']==bytes.fromhex('00 00 00 00 07 08 96 01 12 02 68 69');count+=1
assert ns['ntp'](0,.004,.004,.028)==(-.01,.028);count+=1
assert math.isclose(2**30/2**15*.080,2621.44);assert math.isclose(2621.44/64,40.96);count+=2
print('PASS',count,'assertions, both extracted Python fences; no daemon, real clock, SSH or gRPC runtime tested')
