import os,json,tempfile,contextlib,io,math,itertools,socket,threading,mmap,platform
from pathlib import Path
codes={'fs-modern-distributed': [], 'fs-page-cache': ['import mmap\n\nwith open("big.bin", "rb") as f:\n    m = mmap.mmap(f.fileno(), 0,\n                  access=mmap.ACCESS_READ)\n    header = m[:16]   # copies 16 bytes\n    n = m.find(b"needle")\n    m.close()\n', 'while chunk := os.read(fd, 65536):\n    sock.sendall(chunk)\n', 'os.sendfile(sock.fileno(), fd,\n            offset, count)\n'], 'fs-on-disk-structures': ['import os\nos.link("a", "b")\nos.symlink("a", "c")\nprint(os.stat("a").st_nlink)   # 2\nos.unlink("a")\nprint(os.stat("b").st_nlink)   # 1\nprint(os.path.exists("c"))     # False\nwith open("b") as f:\n    print(f.read())           # data\n'], 'fs-storage-devices': [], 'fs-crash-consistency': ['import os\nimport tempfile\n\ndef atomic_write(path, data):\n    d = os.path.dirname(path) or "."\n    fd, tmp = tempfile.mkstemp(dir=d)\n    try:\n        try:\n            view = memoryview(data)\n            while view:\n                n = os.write(fd, view)\n                if n <= 0:\n                    raise OSError("no progress")\n                view = view[n:]\n            os.fsync(fd)\n        finally:\n            os.close(fd)\n        os.replace(tmp, path)\n        dfd = os.open(d, os.O_RDONLY)\n        try:\n            os.fsync(dfd)\n        finally:\n            os.close(dfd)\n    finally:\n        try:\n            os.unlink(tmp)\n        except FileNotFoundError:\n            pass\n'], 'fs-file-abstraction': ['import os\n\nfd = os.open("demo.txt",\n             os.O_WRONLY | os.O_CREAT\n             | os.O_TRUNC, 0o644)\nprint(fd)                    # often 3\nn = os.write(fd, b"hello world\\n")\nprint(n)                     # 12\nos.close(fd)\n\nfd = os.open("demo.txt", os.O_RDONLY)\nprint(os.read(fd, 5))        # b\'hello\'\nprint(os.read(fd, 100))      # b\' world\\n\'\nprint(os.read(fd, 100))      # b\'\'\nos.close(fd)\n', 'def write_all(fd, data):\n    view = memoryview(data)\n    while view:\n        n = os.write(fd, view)\n        if n <= 0:\n            raise OSError("write stalled")\n        view = view[n:]\n']}

results=[]
def check(name,fn):
 fn();results.append(name)
def equal(a,b): assert a==b,(a,b)
with tempfile.TemporaryDirectory() as td:
 os.chdir(td)
 def abstraction():
  out=io.StringIO()
  with contextlib.redirect_stdout(out):exec(codes['fs-file-abstraction'][0],{})
  equal(out.getvalue().splitlines()[1:],['12',"b'hello'","b' world\\n'","b''"])
 check('regular-file Python example exact byte output',abstraction)
 def offsets():
  a=os.open('demo.txt',os.O_RDONLY);b=os.open('demo.txt',os.O_RDONLY);c=os.dup(a)
  try:
   equal(os.read(a,5),b'hello');equal(os.read(b,5),b'hello');equal(os.read(c,6),b' world')
  finally:
   for fd in (a,b,c):os.close(fd)
 check('independent opens versus dup shared offsets',offsets)
 def links():
  Path('a').write_text('data\n');out=io.StringIO()
  with contextlib.redirect_stdout(out):exec(codes['fs-on-disk-structures'][0],{})
  equal(out.getvalue().splitlines(),['2','1','False','data',''])
 check('hard-link count and dangling symlink snippet',links)
 def unlinkmap():
  Path('mapped').write_bytes(b'keep');fd=os.open('mapped',os.O_RDONLY);mm=mmap.mmap(fd,0,access=mmap.ACCESS_READ)
  os.unlink('mapped');os.close(fd);equal(mm[:],b'keep');mm.close()
 check('mapping retains unlinked contents after descriptor close',unlinkmap)
 def sparse():
  with open('sparse','wb') as f:f.seek(1<<30);f.write(b'!')
  equal(os.stat('sparse').st_size,(1<<30)+1)
  with open('sparse','rb') as f:equal(f.read(32),bytes(32))
 check('sparse logical size and zero-filled hole',sparse)
 def mmapexample():
  payload=b'0123456789abcdef--needle';Path('big.bin').write_bytes(payload);d={};exec(codes['fs-page-cache'][0],d)
  equal(d['header'],payload[:16]);equal(d['n'],18);assert isinstance(d['header'],bytes)
 check('mmap slice copies and find offset',mmapexample)
 # Test write helper against controlled short and zero returns.
 class Stub:
  def __init__(self,zero=False):self.data=bytearray();self.zero=zero
  def write(self,fd,data):
   if self.zero:return 0
   self.data.extend(data[:2]);return min(2,len(data))
 def helper_short():
  stub=Stub();d={'os':stub};exec(codes['fs-file-abstraction'][1],d);d['write_all'](9,b'abcdefg');equal(bytes(stub.data),b'abcdefg')
 check('write_all retries partial writes',helper_short)
 def helper_zero():
  d={'os':Stub(True)};exec(codes['fs-file-abstraction'][1],d)
  try:d['write_all'](9,b'x')
  except OSError:return
  raise AssertionError('zero write accepted')
 check('write_all rejects no-progress result',helper_zero)
 d={};exec(codes['fs-crash-consistency'][0],d);atomic=d['atomic_write']
 def atomic_normal():
  Path('config').write_bytes(b'old');atomic('config',b'new');equal(Path('config').read_bytes(),b'new');equal(os.stat('config').st_mode&0o777,0o600)
 check('atomic_write replacement and documented private mode',atomic_normal)
 realwrite=os.write;realsync=os.fsync
 def atomic_short():
  os.write=lambda fd,data:realwrite(fd,data[:2])
  try:atomic('config',b'abcdefgh')
  finally:os.write=realwrite
  equal(Path('config').read_bytes(),b'abcdefgh')
 check('atomic_write tolerates short writes',atomic_short)
 def atomic_zero():
  before=set(os.listdir());old=Path('config').read_bytes();os.write=lambda fd,data:0
  try:
   try:atomic('config',b'bad')
   except OSError:pass
   else:raise AssertionError('accepted zero')
  finally:os.write=realwrite
  equal(Path('config').read_bytes(),old);equal(set(os.listdir()),before)
 check('atomic_write zero progress preserves old file and removes temp',atomic_zero)
 def atomic_sync_fail(which):
  calls=0;before=set(os.listdir());old=Path('config').read_bytes()
  def sync(fd):
   nonlocal calls
   calls+=1
   if calls==which:raise OSError('injected sync failure')
   return realsync(fd)
  os.fsync=sync
  try:
   try:atomic('config',b'after')
   except OSError:pass
   else:raise AssertionError('missing failure')
  finally:os.fsync=realsync
  equal(Path('config').read_bytes(),old if which==1 else b'after');equal(set(os.listdir()),before)
 check('pre-rename fsync failure preserves old contents',lambda:atomic_sync_fail(1))
 check('post-rename fsync failure can expose replacement despite error',lambda:atomic_sync_fail(2))
 def transfers(sendfile):
  data=b'payload'*1000;Path('transfer').write_bytes(data);fd=os.open('transfer',os.O_RDONLY);sock,peer=socket.socketpair();got=bytearray()
  def reader():
   while chunk:=peer.recv(4096):got.extend(chunk)
  t=threading.Thread(target=reader);t.start()
  try:exec(codes['fs-page-cache'][2 if sendfile else 1],{'os':os,'fd':fd,'sock':sock,'offset':0,'count':len(data)})
  finally:sock.close();t.join();peer.close();os.close(fd)
  equal(bytes(got),data)
 check('buffered socket transfer fragment',lambda:transfers(False))
 check('sendfile fragment in small successful Linux transfer',lambda:transfers(True))
 def parity():
  for a,b,c,new in itertools.product(range(16),repeat=4):
   p=a^b^c;equal(p^b^new,a^new^c)
   equal(p^b^c,a);equal(p^a^c,b);equal(p^a^b,c)
 check('RAID5 XOR update and reconstruction exhaustive 65536 cases',parity)
 def arithmetic():
  equal(12+1024+1024**2+1024**3,1074791436)
  equal((1<<30)//4096,262144);equal((1<<30)//(32768*4096),8)
  equal(81920+3000-1,84919);equal((1<<40)//4096*4,1<<30)
  equal(10*(1<<30)//(128*(1<<20)),80);equal((1<<40)//(128*(1<<20)),8192)
  equal(200_000_000*150,30_000_000_000);equal(600*9/6,900)
  assert math.isclose(1/(1-.8),5)
 check('inode pointers extent mapping flash map HDFS heap and EC arithmetic',arithmetic)
 def models():
  assert math.isclose(math.exp(-3.84)*100,2.1493601345,rel_tol=1e-9)
  assert math.isclose(16e12/150e6/3600,29.6296296296)
  assert math.isclose(48e12/150e6/3600,88.8888888889)
  assert math.isclose(12.8*(1<<30)/30e6,458.129844907)
  assert math.isclose(2*(1<<30)/1e9,2.147483648)
  equal(1e6*.000064,64);equal(1e6*4096,4_096_000_000)
 check('URE Poisson rebuild backlog Little law teaching models',models)
 def inodeindex():
  for n in range(1,32769):
   group,index=divmod(n-1,8192);equal(group*8192+index+1,n)
 check('ext4 inode group/index 32768 boundary cases',inodeindex)
print(json.dumps({'environment':platform.platform(),'checkGroupsPassed':len(results),'checks':results,'limitations':['No power-loss simulation, live ext4/XFS/Btrfs/ZFS/NFS/HDFS cluster or real device benchmark. Injected Python errors test control flow only. Sendfile small successful call does not prove absence of short sends.']},indent=2))
