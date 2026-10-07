import json,re,subprocess,os,tempfile
from pathlib import Path
base=Path('content/os/07-io');out=Path('/tmp/cs-study-audit-full/os07');out.mkdir(exist_ok=True)
code={p.stem:re.findall(r'```([^\n]*)\n(.*?)```',p.read_text(),re.S) for p in base.glob('*.md')}
def blocks(name,lang):return [c for l,c in code[name] if l==lang]
checks=[]
headers='#include <stdio.h>\n#include <stdlib.h>\n#include <errno.h>\n#include <unistd.h>\n#include <fcntl.h>\n#include <signal.h>\n#include <assert.h>\n#include <string.h>\n'
def ccheck(name,src):
 p=out/(name+'.c');p.write_text(src);subprocess.run(['clang','-Wall','-Wextra',str(p),'-o',str(out/name)],check=True,capture_output=True);r=subprocess.run([str(out/name)],check=True,capture_output=True,timeout=10);checks.append(name)
aio=blocks('io-models','c')[-1]
ccheck('posix-aio-fragment',headers+'#include <aio.h>\nvoid do_other_work(void){}\nint main(void){char path[]="/tmp/io-audit-XXXXXX";int fd=mkstemp(path);unlink(path);assert(write(fd,"hello",5)==5);char buf[4096];\n'+aio+'\nassert(status==0 && n==5 && memcmp(buf,"hello",5)==0);close(fd);return 0;}')
selectcode=blocks('io-multiplexing','c')[0]
ccheck('select-dispatch-fragment',headers+'#include <sys/select.h>\nvoid handle(int fd){char c;assert(read(fd,&c,1)==1&&c==42);exit(0);}\nint main(void){int p[2];assert(pipe(p)==0);char c=42;assert(write(p[1],&c,1)==1);int fds[]={p[0]};int n=1;alarm(2);\n'+selectcode+'\n}')
pollcode=blocks('io-multiplexing','c')[1].replace('/* p[i].fd = fd; p[i].events = POLLIN; */','p[0].fd=fds[0];p[0].events=POLLIN;')
ccheck('poll-dispatch-fragment',headers+'#include <poll.h>\n#define MAXCONN 1\nvoid handle_events(int fd,short ev){assert(ev&POLLIN);char c;assert(read(fd,&c,1)==1&&c==42);exit(0);}\nint main(void){int fds[2];assert(pipe(fds)==0);char c=42;assert(write(fds[1],&c,1)==1);int n=1;alarm(2);\n'+pollcode+'\n}')
kq=blocks('io-multiplexing','c')[-1]
ccheck('kqueue-dispatch-fragment',headers+'#include <sys/event.h>\nint main(void){int p[2];assert(pipe(p)==0);char c=42;assert(write(p[1],&c,1)==1);int fd=p[0];void *conn=NULL;alarm(2);\n'+kq+'\nassert(n==1&&ev[0].filter==EVFILT_READ&&ev[0].data==1);close(kq);close(p[0]);close(p[1]);}')
js=json.loads((base/'io-event-loops.questions.json').read_text())[3]['prompt'];js=re.search(r'```js\n(.*?)```',js,re.S).group(1);(out/'ordering.cjs').write_text(js)
r=subprocess.run(['node',str(out/'ordering.cjs')],check=True,capture_output=True,text=True);assert r.stdout.splitlines()==['immediate','timeout'];checks.append('Node CommonJS I/O callback immediate-before-timeout')
xdp=blocks('io-network-stack','c')[0]
xhead='''#include <stdint.h>
#include <string.h>
#include <assert.h>
#include <arpa/inet.h>
#define SEC(x)
#define XDP_PASS 2
#define XDP_DROP 1
#define ETH_P_IP 0x0800
#define bpf_htons htons
#define bpf_ntohs ntohs
struct xdp_md{uintptr_t data,data_end;};
struct __attribute__((packed)) ethhdr{unsigned char d[6],s[6];uint16_t h_proto;};
struct __attribute__((packed)) iphdr{unsigned ihl:4,version:4;uint8_t tos;uint16_t tot_len,id,frag_off;uint8_t ttl,protocol;uint16_t check;uint32_t saddr,daddr;};
struct __attribute__((packed)) udphdr{uint16_t source,dest,len,check;};
'''
xtest='''int main(void){unsigned char b[128]={0};struct ethhdr *e=(void*)b;struct iphdr *ip=(void*)(e+1);struct udphdr *udp=(void*)(b+34);struct xdp_md ctx={(uintptr_t)b,(uintptr_t)(b+42)};e->h_proto=htons(0x0800);ip->version=4;ip->ihl=5;ip->protocol=17;ip->tot_len=htons(28);udp->dest=htons(9999);assert(drop9999(&ctx)==XDP_DROP);udp->dest=htons(80);assert(drop9999(&ctx)==XDP_PASS);udp->dest=htons(9999);ip->ihl=4;assert(drop9999(&ctx)==XDP_PASS);ip->ihl=5;ip->frag_off=htons(1);assert(drop9999(&ctx)==XDP_PASS);ip->frag_off=htons(0x2000);assert(drop9999(&ctx)==XDP_PASS);ip->frag_off=0;ip->tot_len=htons(20);assert(drop9999(&ctx)==XDP_PASS);ip->tot_len=htons(28);ctx.data_end=(uintptr_t)(b+41);assert(drop9999(&ctx)==XDP_PASS);ctx.data_end=(uintptr_t)(b+42);e->h_proto=htons(0x8100);assert(drop9999(&ctx)==XDP_PASS);return 0;}'''
ccheck('XDP-parser-native-logic-8-cases-not-BPF-verifier',xhead+xdp+xtest)
(out/'host-results.json').write_text(json.dumps({'checks':checks,'count':len(checks),'limitations':['XDP fragment compiled as native C with uintptr_t context shim; no BPF target compilation/load or kernel verifier test.','C select/poll/kqueue/POSIX AIO snippets exercised on macOS, not Linux kernel implementation.']},indent=2))
worker=r'''
import os,socket,select,json,tempfile,subprocess,sys,time,threading,ctypes,errno,math,contextlib,io
checks=[]
def check(name,fn):fn();checks.append(name)
def eq(a,b):assert a==b,(a,b)
def readiness(edge):
 a,b=socket.socketpair();a.setblocking(False);ep=select.epoll();ep.register(a.fileno(),select.EPOLLIN|(select.EPOLLET if edge else 0));b.sendall(b'abcd');assert ep.poll(0);eq(a.recv(1),b'a');eq(bool(ep.poll(0)),not edge);eq(a.recv(8),b'bcd');eq(ep.poll(0),[]);b.sendall(b'e');assert ep.poll(0);a.close();b.close();ep.close()
check('epoll LT partial-read remains ready',lambda:readiness(False));check('epoll ET partial-read no guaranteed reminder then new activity',lambda:readiness(True))
def oneshot():
 a,b=socket.socketpair();ep=select.epoll();ep.register(a.fileno(),select.EPOLLIN|select.EPOLLONESHOT);b.sendall(b'x');assert ep.poll(0);eq(ep.poll(0),[]);ep.modify(a.fileno(),select.EPOLLIN|select.EPOLLONESHOT);assert ep.poll(0);a.close();b.close();ep.close()
check('EPOLLONESHOT rearm required',oneshot)
def dup():
 a,b=socket.socketpair();old=a.fileno();copy=os.dup(old);ep=select.epoll();ep.register(old,select.EPOLLIN);a.close();b.sendall(b'x');eq(ep.poll(0)[0][0],old);os.close(copy);ep.close();b.close()
check('epoll duplicate retains original registration data',dup)
def file_epoll():
 with tempfile.TemporaryFile() as f:
  ep=select.epoll()
  try:ep.register(f.fileno(),select.EPOLLIN)
  except PermissionError:pass
  else:raise AssertionError('regular file unexpectedly supported')
  ep.close()
check('epoll rejects ordinary regular file',file_epoll)
def recv():
 a,b=socket.socketpair();a.setblocking(False)
 try:a.recv(100)
 except BlockingIOError:pass
 else:raise AssertionError('no EAGAIN')
 b.sendall(b'x');eq(a.recv(100),b'x');b.shutdown(socket.SHUT_WR);eq(a.recv(100),b'');a.close();b.close()
check('nonblocking EAGAIN/data/EOF distinction',recv)
# Exercise exact lesson Python echo server, with no external network.
with tempfile.TemporaryDirectory() as td:
 p=os.path.join(td,'echo.py');open(p,'w').write(echo_code)
 proc=subprocess.Popen([sys.executable,p],stdout=subprocess.PIPE,stderr=subprocess.PIPE)
 try:
  for _ in range(100):
   if proc.poll() is not None:raise AssertionError(proc.stderr.read().decode())
   try:probe=socket.create_connection(('127.0.0.1',9000),timeout=.1);probe.close();break
   except OSError:time.sleep(.01)
  def echo():
   c=socket.create_connection(('127.0.0.1',9000));c.settimeout(5);payload=bytes(range(256))*4096;errors=[]
   def send():
    try:c.sendall(payload);c.shutdown(socket.SHUT_WR)
    except Exception as e:errors.append(str(e))
   t=threading.Thread(target=send);t.start();got=bytearray();time.sleep(.03)
   while chunk:=c.recv(997):got.extend(chunk)
   t.join();c.close();eq(errors,[]);eq(bytes(got),payload)
  check('exact buffered echo code handles 1MiB payload and half-close',echo)
  check('echo server remains usable after prior disconnect',echo)
 finally:proc.terminate();proc.wait(timeout=2)
# Exact proc parser, capture varying host data without claiming static output.
buf=io.StringIO()
with contextlib.redirect_stdout(buf):exec(proc_code,{})
assert 'done' in buf.getvalue();checks.append('softnet_stat lesson parser on Linux')
eq(84*8,672);assert math.isclose(672/1e10*1e9,67.2);eq(20000*8/1024,156.25);eq(50000*16384/2**20,781.25);eq(50000*2000,100000000);eq(50*2000,100000);checks.append('Ethernet stack-reservation buffer-capacity and polling arithmetic')
libc=ctypes.CDLL(None,use_errno=True);params=ctypes.create_string_buffer(256);ring=libc.syscall(425,2,ctypes.byref(params));err=ctypes.get_errno()
if ring>=0:os.close(ring)
print(json.dumps({'environment':os.uname().sysname+' '+os.uname().release,'checks':checks,'count':len(checks),'io_uring_setup':{'result':ring,'errno':err if ring<0 else None},'limitations':['No live NIC/IRQ/DMA/DPDK/XDP loader, Redis, nginx, throughput or kernel fault-injection test. io_uring probe checks availability only; no security restrictions changed.']},indent=2))
'''
worker='echo_code='+repr(blocks('io-event-loops','python')[0])+'\nproc_code='+repr(blocks('io-network-stack','python')[0])+'\n'+worker
(out/'linux.py').write_text(worker);print(json.dumps({'hostChecks':len(checks),'linuxScript':str(out/'linux.py')}))
