from pathlib import Path
import re, socket, threading, contextlib, io, random
p=Path('content/networks/04-application/app-http-wire.md');codes=re.findall(r'```python\n(.*?)```',p.read_text(),re.S)
count=0
def ck(v):
 global count
 assert v;count+=1
# Actual wire inspection code, deterministic socketpair transport rather than external example.com availability.
real=socket.create_connection
for response in [b'HTTP/1.1 200 OK\r\nContent-Length:3\r\n\r\nabc',b'HTTP/1.1 404 Missing\r\nContent-Length:0\r\n\r\n']:
 a,b=socket.socketpair();a.settimeout(3)
 def server():
  with b:
   request=b.recv(4096);ck(request==b'GET / HTTP/1.1\r\nHost: example.com\r\nConnection: close\r\n\r\n')
   for byte in response:b.sendall(bytes([byte]))
 t=threading.Thread(target=server);t.start();socket.create_connection=lambda *args,**kwargs:a
 out=io.StringIO()
 try:
  with contextlib.redirect_stdout(out):exec(codes[0],{})
 finally:socket.create_connection=real;t.join()
 ck(out.getvalue().strip()==repr(response.split(b'\r\n')[0]));ck(a.fileno()==-1)
ns={};exec(codes[1],ns);decode=ns['read_chunked']
ck(decode(b'7\r\nMozilla\r\n11\r\nDeveloper Network\r\n0\r\n\r\nNEXT')==(b'MozillaDeveloper Network',b'NEXT'))
ck(decode(b'4\r\nWiki\r\n6\r\npedia \r\nE\r\nin \r\n\r\nchunks.\r\n0\r\n\r\n')[0]==b'Wikipedia in \r\n\r\nchunks.')
for wire in [b'',b'0\r\n',b'0\r\nX: a\r\n\r\n',b'-1\r\nx',b'+1\r\nx\r\n0\r\n\r\n',b'1_0\r\n',b'0x10\r\n',b'1;ext\r\nx\r\n0\r\n\r\n',b'1\r\nxXX0\r\n\r\n',b'3\r\nx',b'1\r\nx\r\n']:
 try:decode(wire)
 except ValueError:ck(True)
 else:raise AssertionError(wire)
rng=random.Random(4)
for _ in range(1000):
 chunks=[rng.randbytes(rng.randrange(1,65)) for i in range(rng.randrange(10))];tail=rng.randbytes(8)
 wire=b''.join(format(len(c),'x').encode()+b'\r\n'+c+b'\r\n'for c in chunks)+b'0\r\n\r\n'+tail
 ck(decode(wire)==(b''.join(chunks),tail))
 for cut in range(len(wire)-len(tail)-1):
  try:decode(wire[:cut])
  except ValueError:ck(True)
  else:raise AssertionError(('accepted truncation',cut))
ck(len(b'0\r\n\r\nSMUGGLED')==13);ck(61*2500==152500)
print('PASS',count,'assertions;2actual lessonPythonfences;socketpairfixture, no externalserverclaim')
