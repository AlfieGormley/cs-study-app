echo_code='import selectors, socket\n\nsel = selectors.DefaultSelector()\nR = selectors.EVENT_READ\nW = selectors.EVENT_WRITE\nHIGH = 65536\n\ndef close(conn):\n    sel.unregister(conn)\n    conn.close()\n\ndef accept(lsock, mask):\n    try:\n        conn, _ = lsock.accept()\n    except BlockingIOError:\n        return\n    conn.setblocking(False)\n    out, eof = bytearray(), False\n\n    def echo(conn, mask):\n        nonlocal eof\n        try:\n            if mask & R and not eof:\n                room = HIGH - len(out)\n                if room:\n                    try:\n                        data = conn.recv(\n                            min(4096, room))\n                    except BlockingIOError:\n                        data = None\n                    if data == b"":\n                        eof = True\n                    elif data:\n                        out.extend(data)\n            if mask & W and out:\n                try:\n                    n = conn.send(out)\n                except BlockingIOError:\n                    n = None\n                if n == 0:\n                    close(conn)\n                    return\n                if n:\n                    del out[:n]\n        except OSError:\n            close(conn)\n            return\n        events = W if out else 0\n        if not eof and len(out) < HIGH:\n            events |= R\n        if events:\n            sel.modify(conn, events, echo)\n        else:\n            close(conn)\n\n    sel.register(conn, R, echo)\n\nls = socket.socket()\nls.setsockopt(socket.SOL_SOCKET,\n              socket.SO_REUSEADDR, 1)\nls.bind(("127.0.0.1", 9000))\nls.listen(128)\nls.setblocking(False)\nsel.register(ls, R, accept)\ntry:\n    while True:\n        for key, mask in sel.select():\n            key.data(key.fileobj, mask)\nfinally:\n    for key in list(sel.get_map().values()):\n        key.fileobj.close()\n    sel.close()\n'
proc_code='for row, line in enumerate(\n        open("/proc/net/softnet_stat")):\n    f = [int(x, 16) for x in line.split()]\n    print(row, "done", f[0],\n          "drop", f[1], "squeeze", f[2])\n'

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
