import os,sys,ctypes,fcntl,errno,socket,array,signal,mmap,json,platform,tempfile
n=0

def ck(x):
 global n
 assert x;n+=1
lib=ctypes.CDLL(None,use_errno=True)
# Generic libc syscall API still translates errors; native Linux ABI differs by architecture.
num={'aarch64':(64,172),'x86_64':(1,39)}[platform.machine()]
ck(lib.syscall(num[1])==os.getpid())
ck(lib.syscall(num[0],-1,ctypes.c_char_p(b'x'),1)==-1);ck(ctypes.get_errno()==errno.EBADF)
# Kernel-provided vDSO mapping, proc task state and pipe limits.
ck('[vdso]' in open('/proc/self/maps').read());ck('voluntary_ctxt_switches:' in open('/proc/self/status').read())
r,w=os.pipe();cap=fcntl.fcntl(w,fcntl.F_GETPIPE_SZ);pipebuf=os.fpathconf(w,'PC_PIPE_BUF');ck(pipebuf==4096);ck(cap>=pipebuf)
os.set_blocking(w,False);written=0
try:
 while True:written+=os.write(w,b'x'*pipebuf)
except BlockingIOError:pass
ck(written==cap);ck(os.read(r,7)==b'x'*7);os.close(w)
while os.read(r,4096):pass
ck(os.read(r,1)==b'');os.close(r)
# Shared open-file-description offset after fork.
f=tempfile.TemporaryFile();f.write(b'abcdef');f.seek(0);c=os.fork()
if c==0:os.read(f.fileno(),2);os._exit(0)
os.waitpid(c,0);ck(f.read()==b'cdef');f.close()
# Normal exit137 and SIGKILL produce distinguishable raw wait states despite same shell status.
c=os.fork()
if c==0:os._exit(137)
_,st=os.waitpid(c,0);ck(os.WIFEXITED(st) and os.WEXITSTATUS(st)==137)
c=os.fork()
if c==0:os.kill(os.getpid(),signal.SIGKILL);os._exit(0)
_,st=os.waitpid(c,0);ck(os.WIFSIGNALED(st) and os.WTERMSIG(st)==signal.SIGKILL)
# Standard signal coalescing while blocked.
old=signal.pthread_sigmask(signal.SIG_BLOCK,{signal.SIGUSR1})
for _ in range(3):os.kill(os.getpid(),signal.SIGUSR1)
ck(signal.SIGUSR1 in signal.sigpending());ck(signal.sigwait({signal.SIGUSR1})==signal.SIGUSR1);ck(signal.SIGUSR1 not in signal.sigpending());signal.pthread_sigmask(signal.SIG_SETMASK,old)
# Unix SCM_RIGHTS installs a new fd referencing the same open file description.
a,b=socket.socketpair();f=tempfile.TemporaryFile();f.write(b'abc');f.seek(0)
a.sendmsg([b'fd'],[(socket.SOL_SOCKET,socket.SCM_RIGHTS,array.array('i',[f.fileno()]))]);msg,anc,flags,addr=b.recvmsg(16,socket.CMSG_SPACE(4));received=array.array('i');received.frombytes(anc[0][2][:4]);fd=received[0]
ck(msg==b'fd' and fd!=f.fileno());ck(os.read(fd,1)==b'a');ck(f.read()==b'bc');os.close(fd);f.close();a.close();b.close()
# POSIX shared-memory creator/attacher with synchronised observation after wait.
lib.shm_open.argtypes=[ctypes.c_char_p,ctypes.c_int,ctypes.c_uint];lib.shm_open.restype=ctypes.c_int
name=('/csstudy-audit-'+str(os.getpid())).encode();fd=lib.shm_open(name,os.O_CREAT|os.O_EXCL|os.O_RDWR,0o600);ck(fd>=0);os.ftruncate(fd,4096);m=mmap.mmap(fd,4096)
c=os.fork()
if c==0:m[0:4]=b'0042';os._exit(0)
os.waitpid(c,0);ck(m[:4]==b'0042');ck(lib.shm_unlink(name)==0);m.close();os.close(fd)
# POSIX mqueue bounds, message length and priority.
class Attr(ctypes.Structure):_fields_=[('flags',ctypes.c_long),('maxmsg',ctypes.c_long),('msgsize',ctypes.c_long),('curmsgs',ctypes.c_long),('pad',ctypes.c_long*4)]
name=('/csstudy-mq-'+str(os.getpid())).encode();attr=Attr(0,10,256,0);q=lib.mq_open(ctypes.c_char_p(name),os.O_CREAT|os.O_EXCL|os.O_RDWR,0o600,ctypes.byref(attr));ck(q>=0)
for payload,priority in [(b'low',1),(b'first-high',5),(b'second-high',5)]:ck(lib.mq_send(q,payload,len(payload),priority)==0)
for expected,prio in [(b'first-high',5),(b'second-high',5),(b'low',1)]:
 buf=ctypes.create_string_buffer(256);p=ctypes.c_uint();length=lib.mq_receive(q,buf,256,ctypes.byref(p));ck(buf.raw[:length]==expected and p.value==prio)
ck(lib.mq_close(q)==0);ck(lib.mq_unlink(name)==0)
print(json.dumps({'linux':platform.release(),'architecture':platform.machine(),'assertionsPassed':n,'pipeCapacityObserved':cap,'scope':'Native libc syscall/error handling, vDSO/proc, pipe capacity/EOF, shared file offset after fork, normal137 versus SIGKILL wait status, signal coalescing, Unix SCM_RIGHTS, POSIX shared memory and mqueue priority. Isolated container; no performance benchmark.'}))
