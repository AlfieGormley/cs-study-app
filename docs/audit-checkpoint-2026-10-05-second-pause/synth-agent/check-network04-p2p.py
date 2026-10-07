from pathlib import Path
import re,random,struct,io,contextlib
src=Path('content/networks/04-application/app-p2p-webrtc.md').read_text();ns={};count=0
with contextlib.redirect_stdout(io.StringIO()) as out:
 for c in re.findall(r'```python\n(.*?)```',src,re.S):exec(c,ns)
assert out.getvalue()=="b'd3:cow3:moo4:spaml1:ai42eee'\n2 111 6699 960\n";count+=1
enc=ns['bencode']
def dec(s,i=0):
 if s[i:i+1]==b'i':
  j=s.index(b'e',i);return int(s[i+1:j]),j+1
 if s[i:i+1] in [b'l',b'd']:
  typ=s[i];a=[];i+=1
  while s[i:i+1]!=b'e':v,i=dec(s,i);a.append(v)
  return (a if typ==108 else dict(zip(a[::2],a[1::2]))),i+1
 j=s.index(b':',i);n=int(s[i:j]);return s[j+1:j+1+n],j+1+n
rng=random.Random(953)
for _ in range(10000):
 d={rng.randbytes(5):[rng.randrange(-10000,10000),rng.randbytes(rng.randrange(30))] for _ in range(5)}
 b=enc(d);v,end=dec(b);assert v==d and end==len(b);assert enc(dict(reversed(list(d.items()))))==b;count+=2
 seq=rng.randrange(65536);ts=rng.randrange(2**32);pt=rng.randrange(128);mark=rng.randrange(2)
 p=struct.pack('!BBHII',128,(mark<<7)|pt,seq,ts,123)
 b0,b1,s,t,ssrc=struct.unpack('!BBHII',p);assert (b0>>6,b1>>7,b1&127,s,t,ssrc)==(2,mark,pt,seq,ts,123);count+=1
for x in [True,1.2,None,{1:'bad'},{'a':1,b'a':2}]:
 try:enc(x)
 except (TypeError,ValueError):count+=1
 else:raise AssertionError(x)
assert enc({'b':7,'a':'xy'})==b'd1:a2:xy1:bi7ee';count+=1
for a in range(16):
 for b in range(16):
  for c in range(16):assert a^c <= (a^b)+(b^c);count+=1
assert min([8,3,14],key=lambda x:x^11)==8;count+=1
b0,b1,s,t,z=struct.unpack('!BBHII',bytes.fromhex('80e0000500015f9012345678'));assert(b1>>7,b1&127,s,t)==(1,96,5,90000);count+=1
assert 48000*.02==960 and 90000/30==3000 and 5*1.2==6;count+=1
# Compact RTCP elapsed-time arithmetic across wrap, with quantization.
lsr=0xfffff000;a=(lsr+round(.190*65536))%(2**32);dlsr=round(.040*65536)
assert abs(((a-lsr-dlsr)%(2**32))/65536-.150)<2/65536;count+=1
print('PASS',count,'assertions, both extracted Python fences, bencode roundtrips/invalid inputs, exhaustive four-bit XOR metric, RTP packing and RTCP wrap arithmetic. No live torrent/WebRTC network.')
