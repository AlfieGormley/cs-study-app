import ast,contextlib,io,json,math,pathlib,random,re,socket,struct,subprocess,sys,time,threading,asyncio
root=pathlib.Path(sys.argv[1] if len(sys.argv)>1 else '.')
p=root/'content/networks/03-tcp'
lesson={f.stem:re.findall(r'```python\n(.*?)```',f.read_text(),re.S) for f in p.glob('*.md')}
quiz={q['id']:{k:re.findall(r'```python\n(.*?)```',v,re.S) for k,v in q.items() if isinstance(v,str)} for f in p.glob('*.questions.json') for q in json.loads(f.read_text())}
n=0
def check(v):
 global n
 n+=1
 assert v,n

def capture(code,ns):
 b=io.StringIO()
 with contextlib.redirect_stdout(b):exec(code,ns)
 return b.getvalue()

def definitions(code,ns):
 tree=ast.parse(code);tree.body=[x for x in tree.body if isinstance(x,(ast.Import,ast.ImportFrom,ast.FunctionDef,ast.AsyncFunctionDef))]
 exec(compile(tree,'lesson','exec'),ns)

def rejects(fn,kind=ValueError):
 try:fn()
 except kind:check(True)
 else:check(False)

# Execute model fences and both contextual quiz calls.
ns={};out=capture(lesson['tcp-reliability'][0],ns);check('ACK 5001 held []' in out)
rng=random.Random(42003)
for _ in range(3000):
 arrivals=[(rng.randrange(100),rng.randrange(1,25)) for z in range(25)]
 actual=capture('rx(arrivals,nxt=0)',dict(ns,arrivals=arrivals)).splitlines();received=set();nxt=0
 for (seq,length),line in zip(arrivals,actual):
  received.update(range(seq,seq+length))
  while nxt in received:nxt+=1
  check(int(line.split()[1])==nxt)
for a in [[(-1,2)],[(1,0)],[(True,2)]]:rejects(lambda:capture('rx(a)',dict(ns,a=a)))
out=capture(quiz['tcp-reliability-q4']['prompt'][0],ns);check([int(l.split()[1]) for l in out.splitlines()]==[501,501,1501,2001])
ns={};capture(lesson['tcp-congestion'][0],ns)
check(capture(quiz['tcp-congestion-q6']['prompt'][0],ns).splitlines()[4].strip()=='4 9 9')
for _ in range(2000):
 cw=rng.randrange(1,100);ss=rng.randrange(2,100);events={r:rng.choice(['dupack','timeout']) for r in range(12) if rng.randrange(4)==0}
 output=capture('reno(12, events,cwnd=cw,ssth=ss)',dict(ns,events=events,cw=cw,ss=ss))
 for r,line in enumerate(output.splitlines()):
  vals=line.split();check((int(vals[1]),int(vals[2]))==(cw,ss))
  if events.get(r)=='dupack':ss=max(cw//2,2);cw=ss
  elif events.get(r)=='timeout':ss=max(cw//2,2);cw=1
  elif cw<ss:cw=min(cw*2,ss)
  else:cw+=1
for args in [(-1,{}),(1,{2:'dupack'}),(1,{0:'bad'}),(1,{},0,2)]:rejects(lambda:capture('reno(*args)',dict(ns,args=args)))
ns={};out=capture(lesson['tcp-performance'][0],ns);check([float(x) for x in out.splitlines()]==[14.2496,1.42496])
for _ in range(2000):
 mss=rng.randrange(1,9000);rtt=rng.uniform(.001,1);loss=rng.uniform(.000001,.1)
 check(math.isclose(ns['mathis'](mss,rtt,loss)*rtt*math.sqrt(loss),mss*8*1.22))
for args in [(0,1,.1),(1,0,.1),(1,1,0),(1,1,1)]:rejects(lambda:ns['mathis'](*args))
check(math.isclose(200*.7,140));check(math.isclose((150**(1/3)),5.313292845913055));check(math.isclose(500000*8/1e7,.4))

# Framing fences: fake fragmentation oracle, EOF, invalid size; exact quiz buggy and fixed code.
helpers={};exec(lesson['tcp-sockets'][0],helpers)
class Fragmented:
 def __init__(self,data,chunk=2):self.data=data;self.chunk=chunk
 def recv(self,n):out=self.data[:min(n,self.chunk)];self.data=self.data[len(out):];return out
for length in range(1500):
 payload=rng.randbytes(length);s=Fragmented(struct.pack('!I',length)+payload,1+length%29)
 check(helpers['recv_msg'](s)==payload)
rejects(lambda:helpers['recv_msg'](Fragmented(b'\0\0')),EOFError)
rejects(lambda:helpers['recv_msg'](Fragmented(struct.pack('!I',helpers['MAX_MSG']+1))))
rejects(lambda:helpers['send_msg'](None,b'x'*(helpers['MAX_MSG']+1)))
rejects(lambda:helpers['recv_exact'](None,-1))
a=Fragmented(b'\0\0\0\3abcdef',100);check(helpers['recv_msg'](a)==b'abc');check(a.data==b'def')
qns=dict(helpers,sock=Fragmented(struct.pack('!I',3)+b'abc'));rejects(lambda:exec(quiz['tcp-sockets-q5']['prompt'][0],qns),struct.error)
qns=dict(helpers,sock=Fragmented(struct.pack('!I',3)+b'abc'));exec(quiz['tcp-sockets-q5']['workedExample'][0],qns);check(qns['body']==b'abc')

# Actual bounded loopback fixtures in network-disconnected Linux container.
def wait_tcp(port):
 for _ in range(100):
  try:return socket.create_connection(('127.0.0.1',port),timeout=.05)
  except OSError:time.sleep(.01)
 raise AssertionError('server did not start')

def start(code):return subprocess.Popen([sys.executable,'-u','-c',code],stdout=subprocess.PIPE,stderr=subprocess.PIPE)
def stop(proc):
 proc.terminate()
 try:proc.communicate(timeout=3)
 except subprocess.TimeoutExpired:proc.kill();proc.communicate()

proc=start(lesson['tcp-udp-ports'][0])
try:
 with socket.socket(socket.AF_INET,socket.SOCK_DGRAM) as u:
  u.settimeout(.05)
  for _ in range(100):
   u.sendto(b'hello',('127.0.0.1',9999))
   try:check(u.recvfrom(4096)[0]==b'HELLO');break
   except socket.timeout:pass
  else:raise AssertionError('UDP server unavailable')
finally:stop(proc)
with socket.socket(socket.AF_INET,socket.SOCK_DGRAM) as rx,socket.socket(socket.AF_INET,socket.SOCK_DGRAM) as tx:
 rx.bind(('127.0.0.1',0));rx.settimeout(1)
 exec(quiz['tcp-udp-ports-q4']['prompt'][0],dict(s=tx,srv=rx.getsockname()))
 check([len(rx.recvfrom(1000)[0]) for _ in range(3)]==[100,200,300])

proc=start(lesson['tcp-sockets'][0]+'\n'+lesson['tcp-sockets'][1])
try:
 wait_tcp(9000).close()
 check(capture(lesson['tcp-sockets'][2],dict(helpers)).strip()=="b'HELLO'")
 with socket.create_connection(('127.0.0.1',9000),timeout=2) as c:
  for msg in [b'',b'abc',b'x'*100000]:helpers['send_msg'](c,msg);check(helpers['recv_msg'](c)==msg.upper())
  c.sendall(struct.pack('!I',helpers['MAX_MSG']+1));check(c.recv(1)==b'')
finally:stop(proc)

# send_request on real TCP, and retained-pool EOF leak demonstration.
with socket.create_server(('127.0.0.1',0)) as srv:
 with socket.create_connection(srv.getsockname(),timeout=2) as client:
  conn,_=srv.accept()
  with conn:
   fns={};exec(lesson['tcp-flow-control'][0],fns);fns['send_request'](client,b'head',b'body')
   check(helpers['recv_exact'](conn,8)==b'headbody');check(client.getsockopt(socket.IPPROTO_TCP,socket.TCP_NODELAY)==1)
   client.shutdown(socket.SHUT_WR)
   class Pool:
    def get(self):return conn
   pns={};exec(quiz['tcp-connections-q5']['workedExample'][0],pns);pns['handle'](Pool());check(conn.fileno()>=0)
ns={'socket':socket};exec(quiz['tcp-sockets-q6']['workedExample'][0],ns);check(ns['s'].getsockname()[1]==8080);ns['s'].close()

# Execute deliberately faulty selector fence with deterministic event/socket fixtures.
# Actual default-selector echo happy path separately; forced faults need controllable send results.
proc=start(lesson['tcp-sockets'][3])
try:
 with wait_tcp(9001) as c:
  c.settimeout(2);c.sendall(b'abc');check(helpers['recv_exact'](c,3)==b'abc')
finally:stop(proc)
code=lesson['tcp-sockets'][3]
class Done(Exception):pass
class FakeConn:
 def __init__(self,fail=False):self.sent=b'';self.fail=fail
 def recv(self,n):return b'abcdef'
 def send(self,data):
  if self.fail:raise BlockingIOError
  self.sent=data[:2];return 2
class FakeSelector:
 def __init__(self,c):self.c=c;self.called=False
 def select(self):
  if self.called:raise Done
  self.called=True;return [(type('Key',(),{'fileobj':self.c})(),1)]
loop=code[code.index('while True:'):]
for fail in [False,True]:
 c=FakeConn(fail)
 rejects(lambda:exec(loop,dict(sel=FakeSelector(c),srv=object())),BlockingIOError if fail else Done)
 if not fail:check(c.sent==b'ab')

# Full async fence including main entry point, finite process lifetime.
proc=start(lesson['tcp-sockets'][4])
try:
 with wait_tcp(9002) as c:
  c.settimeout(2);c.sendall(b'hello');check(helpers['recv_exact'](c,5)==b'HELLO');c.shutdown(socket.SHUT_WR);check(c.recv(1)==b'')
finally:stop(proc)
print(json.dumps({'assertions':n,'lesson_python_fences':sum(map(len,lesson.values())),'quiz_python_fences':sum(len(c) for q in quiz.values() for c in q.values()),'environment':'Linux disposable Docker --network none; loopback only','limitations':['No WAN/packet-loss/QUIC/AQM load experiment','Faulty selector intentionally demonstrated, not certified production-ready','No exact TIME_WAIT timer or backlog exhaustion measurement']},indent=2))
