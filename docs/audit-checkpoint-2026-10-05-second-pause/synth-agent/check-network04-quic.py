from pathlib import Path
import random,re,contextlib,io,json
p=Path('content/networks/04-application/app-http2-quic.md');codes=re.findall(r'```python\n(.*?)```',p.read_text(),re.S);ns={};count=0
def ck(v):
 global count
 assert v;count+=1
out=io.StringIO()
with contextlib.redirect_stdout(out):
 for c in codes:exec(c,ns)
ck(out.getvalue()=='[10]\n[31, 154, 10]\n(37, 1)\n(15293, 2)\n')
def dec_prefix(data,n):
 limit=2**n-1
 if data[0]<limit:return data[0]
 return limit+sum((x&127)*128**i for i,x in enumerate(data[1:]))
for n in range(1,9):
 for value in list(range(10000))+[2**60,2**100]:
  wire=ns['enc_int'](value,n);ck(dec_prefix(wire,n)==value);ck(all(0<=x<=255 for x in wire));ck(wire[-1]<128 or len(wire)==1)
for args in [(-1,5),(1,0),(1,9),(1.5,3),(True,3)]:
 try:ns['enc_int'](*args)
 except ValueError:ck(True)
 else:raise AssertionError(args)
r=random.Random(44)
for size in [1,2,4,8]:
 bits=size*8-2
 for value in [0,1,2**bits-1]+[r.randrange(2**bits) for _ in range(10000)]:
  wire=((size.bit_length()-1)<<(size*8-2)|value).to_bytes(size,'big')
  ck(ns['varint'](wire+b'junk')==(value,size))
  for cut in range(size):
   try:ns['varint'](wire[:cut])
   except ValueError:ck(True)
   else:raise AssertionError((size,cut))
ck(ns['varint'](bytes.fromhex('4025'))==(37,2))
ck(len('Mozilla/5.0 (X11)')==17);ck(10+17+32==59);ck(4050+59-4096==13)
ck(65535/.08*8==6553500);ck(65535/.1*8==5242800)
wire=bytes.fromhex('000010000100000003');ck(int.from_bytes(wire[:3],'big')==16);ck(wire[3:5]==b'\0\1');ck(int.from_bytes(wire[5:],'big')==3)
# HPACK literal sample: independent small decoder for its exact static/indexing subset.
wire=bytes.fromhex('82 86 84 41 0f 77 77 77 2e 65 78 61 6d 70 6c 65 2e 63 6f 6d')
static={1:(':authority',''),2:(':method','GET'),4:(':path','/'),6:(':scheme','http')}
fields=[];i=0
while i<len(wire):
 b=wire[i];i+=1
 if b&128:fields.append(static[b&127])
 else:
  ck(b==0x41);length=wire[i];i+=1;fields.append((static[b&63][0],wire[i:i+length].decode()));i+=length
ck(fields==[(':method','GET'),(':scheme','http'),(':path','/'),(':authority','www.example.com')]);ck(sum(map(len,fields[-1]))+32==57)
print(json.dumps({'assertions':count,'actual_python_fences':len(codes),'scope':'Offline HPACK integer and sample block decoding, QUIC varint boundaries/truncation, frame and quiz arithmetic; no live QUIC endpoint or browser'}))
