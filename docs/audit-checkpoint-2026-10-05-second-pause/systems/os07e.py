from helper import *
b='content/os/07-io/io-event-loops';m=b+'.md';q=b+'.questions.json'
nd=['https://nodejs.org/en/learn/asynchronous-work/event-loop-timers-and-nexttick'];pr=['https://nodejs.org/api/process.html#when-to-use-queuemicrotask-vs-processnexttick'];uv=['https://docs.libuv.org/en/v1.x/design.html','https://docs.libuv.org/en/v1.x/threadpool.html'];ng=['https://nginx.org/en/docs/ngx_core_module.html','https://nginx.org/en/docs/http/ngx_http_core_module.html#aio'];re=['https://raw.githubusercontent.com/redis/redis/6.0/redis.conf'];sc=['https://redis.io/docs/latest/commands/scan/'];un=['https://redis.io/docs/latest/commands/unlink/'];py=['https://docs.python.org/3/library/selectors.html','https://docs.python.org/3/library/socket.html']
def e(a,c,r,s):edit(m,a,c,r,s)
def f(i,k,c,r,s,o=None):qe(q,'io-event-loops-q'+str(i),k,c,r,s,o)
e('## The shape of every event loop','## A common event-loop model','Notallloopsidentical.',uv)
e('An event loop is a single thread running this, forever:','A common design runs the following dispatch logic on one thread until shutdown:','Notallloopsforever.',uv)
e('not a thread with an 8 MB stack.','rather than requiring a dedicated waiting thread and stack for each connection.','Stacksize notuniversal.',uv)
e('No preemption means no locks for loop-owned data.','Other threads can still run and the OS can preempt this thread. Data exclusively owned by the loop often needs no inter-thread lock, but reentrant callbacks and shared state require care.','NoOSpreemption/globalnolocks false.',uv)
e('**Every operation is non-blocking.**','**Keep blocking work off the dispatch thread.**','Designgoalnotimplementationguarantee.',uv)
e('## A complete loop in Python','## A small buffered echo loop in Python','Boundexamplescope.',py)
e('Here is a working echo server:','This local teaching server retains partial sends, handles receive EOF after flushing queued output, and bounds each connection\'s queued payload. It omits production concerns such as idle timeouts and a global connection/memory limit:', 'Actualexamplescope.',py)
a=Path(m).read_text();st=a.index('```python\n');ed=a.index('\n```',st)+4
code='''```python
import selectors, socket

sel = selectors.DefaultSelector()
R, W = selectors.EVENT_READ, selectors.EVENT_WRITE
HIGH = 65536

def close(conn):
    sel.unregister(conn)
    conn.close()

def accept(lsock, mask):
    try:
        conn, _ = lsock.accept()
    except BlockingIOError:
        return
    conn.setblocking(False)
    out, eof = bytearray(), False

    def echo(conn, mask):
        nonlocal eof
        try:
            if mask & R and not eof:
                room = HIGH - len(out)
                if room:
                    try:
                        data = conn.recv(
                            min(4096, room))
                    except BlockingIOError:
                        data = None
                    if data == b"":
                        eof = True
                    elif data:
                        out.extend(data)
            if mask & W and out:
                try:
                    n = conn.send(out)
                except BlockingIOError:
                    n = None
                if n == 0:
                    close(conn)
                    return
                if n:
                    del out[:n]
        except OSError:
            close(conn)
            return
        events = W if out else 0
        if not eof and len(out) < HIGH:
            events |= R
        if events:
            sel.modify(conn, events, echo)
        else:
            close(conn)

    sel.register(conn, R, echo)

ls = socket.socket()
ls.setsockopt(socket.SOL_SOCKET,
              socket.SO_REUSEADDR, 1)
ls.bind(("127.0.0.1", 9000))
ls.listen(128)
ls.setblocking(False)
sel.register(ls, R, accept)
try:
    while True:
        for key, mask in sel.select():
            key.data(key.fileobj, mask)
finally:
    for key in list(sel.get_map().values()):
        key.fileobj.close()
    sel.close()
```'''
code=code.replace('R, W = selectors.EVENT_READ, selectors.EVENT_WRITE','R = selectors.EVENT_READ\nW = selectors.EVENT_WRITE')
e(a[st:ed],code,'Replace nonblocking sendall data-loss/crash example with buffered sends and bounded perconnection output.',py)
e('> [!warning] The hidden block\n> `sendall` on a non-blocking socket raises `BlockingIOError` once the kernel\'s send buffer is full (and may have sent part of the data). A real loop keeps unsent bytes in a per-connection buffer, registers for `EVENT_WRITE`, and finishes the write when the socket becomes writable. Handling partial writes is where most hand-written loops go wrong.','> [!warning] Preserve partial writes\n> Non-blocking sendall can raise after sending some bytes without exposing a usable partial count. The loop above uses send, retains the unsent suffix, enables write interest while output remains and pauses reading at HIGH. That is a per-connection payload bound, not a total process memory bound.','Explainimplementedfixandboundedclaim.',py)
e('so the loop sleeps exactly until either I/O or the earliest timer.','so the loop requests a wait no longer than the time to the next expiry; interruption, timer granularity and scheduling can alter actual wakeup time.','Notexactwakeguarantee.',nd)
e('This is why a timer is a *minimum* delay. `setTimeout(f, 10)` runs `f` no sooner than 10 ms later, but if a callback hogs the thread for 200 ms, `f` runs at roughly 200 ms.','A timer establishes a scheduling threshold, not an exact deadline. Long callbacks can delay it substantially. Runtime clock granularity and rounding mean a nominal millisecond value is not a precision timing contract.','Avoid hardrealminimumacrossclockresolution.',nd)
e('Each loop iteration runs these **phases** in order:','The main recurring phases in modern Node/libuv can be sketched as follows; startup behavior and version details matter. Since libuv 1.45 (used by Node 20), timers run after polling in the recurring loop rather than both before and after it:', 'Versioned timerphasechange.',nd)
e(' +--> timers         (setTimeout)\n |    pending        (deferred I/O cbs)\n |    idle, prepare  (internal)\n |    poll           (epoll_wait; I/O cbs)\n |    check          (setImmediate)\n +--- close          (on \'close\' cbs)',' +--> pending        (deferred I/O cbs)\n |    idle, prepare  (internal)\n |    poll           (wait; I/O cbs)\n |    check          (setImmediate)\n |    close          (on \'close\' cbs)\n +--- timers         (setTimeout)','Aligncurrentrecurringphasesdiagram.',nd)
e('Between callbacks, Node drains two extra queues: `process.nextTick` callbacks first, then promise **microtasks**. Both run before the loop moves on, so a recursive `nextTick` or a promise chain that never yields can starve I/O completely.','Node also services nextTick and promise microtask queues. In typical CommonJS callback contexts, nextTick processing precedes promise microtasks; ES-module evaluation is itself microtask-driven and can produce a different apparent order. Recursive nextTick or endlessly replenished microtasks can starve normal I/O progress.','ESMorderingexception.',pr)
e('Some work has no non-blocking kernel interface, so libuv runs it on a **thread pool** and posts the result back to the loop:','libuv uses a shared **thread pool** for several asynchronous APIs, with results delivered back to the originating loop. Alternative supported filesystem backends can exist:', 'Notabsenceallkernelinterfaces.',uv)
e('Network sockets do **not** use the pool; they go through epoll on the loop thread.','Ordinary asynchronous network socket readiness/completion uses the platform backend rather than a blocked pool worker per socket. Unix often uses epoll/kqueue; Windows uses IOCP. DNS lookup can still use the pool.', 'Platformscope.',uv)
e('`worker_processes auto` starts one worker per CPU core. Each worker is single-threaded and runs its own epoll loop.','worker_processes auto attempts to detect available CPUs; inspect the actual count under affinity/cgroup constraints. Each worker has its own event loop, with platform-specific backends and optional worker threads.', 'Notphysicalcore/allworkeronlyone thread.',ng)
e('Total capacity is roughly workers × connections.','workers × worker_connections is an aggregate connection-slot ceiling, not a guarantee of that many clients: upstream connections and descriptor/resource limits also consume capacity.', 'Proxyupstreamcount.',ng)
e('No shared state between workers in the hot path, so the design scales across cores without locks.','Per-worker connections reduce shared-state contention, but shared-memory zones, caches and other coordination can still use locks.', 'Nginxnotnolocks.',ng)
e("NGINX's own benchmark reported up to a ninefold speed-up when serving files that didn't fit in memory.",'Performance depends on storage, files, concurrency and configuration; no benchmark reproduction is included here.', 'Removeunsourcedspecificspeedup.',ng)
e('that\'s how nginx reloads with zero dropped requests.','this supports graceful reloads, but errors, timeouts and worker shutdown limits mean zero dropped requests is not an unconditional guarantee.', 'Gracefulnotzeroalways.',ng)
e('Redis is the famous example of a single-threaded server that is fast *because* it is single-threaded.','Redis illustrates serial command execution combined with event-driven I/O and background work.','Avoidsinglecauseperformanceranking.',re)
e('That makes every command atomic with no locks, and lets the data structures be simple.','Serial command execution avoids interleaving ordinary command handlers on one instance; it does not make all server code lock-free or turn multi-command client workflows into transactions.', 'Scopeatomicityandnolocks.',re)
e('Most commands touch memory only, taking around a microsecond, so one core can serve on the order of 100,000+ simple operations a second, more with pipelining.','Command cost depends on command complexity, data size, persistence, networking and hardware. Pipelining can amortize round trips without removing command work.', 'Unsupportedtimingthroughputremoved.',re)
e('Deleting a huge key frees memory synchronously. `UNLINK` (Redis 4.0) moves the freeing to a background thread.','Ordinary synchronous deletion of a large aggregate can be expensive. UNLINK (introduced in Redis 4.0) detaches keys and defers expensive freeing; small objects and lazy-free configuration affect which work runs in the background.', 'DELlazyfreeandsmallunlinkexceptions.',un+re)
e('Since Redis 6.0, optional **I/O threads** (`io-threads`) parallelise reading requests from and writing replies to sockets, which dominates at high connection counts. Command execution stays single-threaded, so the atomicity guarantee is unchanged.','Redis 6.0 introduced configurable I/O threads. In that version, threaded reads additionally require io-threads-do-reads yes; they are not automatically enabled merely by raising io-threads. Ordinary command execution remains serial on the main thread. Benefits depend on the actual I/O bottleneck; later versions can change implementation details.', 'Version6readconfigurationandconditionalperformance.',re)
e('| Many processes behind a proxy | Redis Cluster |','| Partitioned service instances | Redis Cluster shards |','RedisClusterisclientroutednotnecessarilyproxy.',re)
e('each `await` is a point where the coroutine yields back to it.','an await can suspend, but an already-completed operation may continue immediately (for example in Python); language/runtime behavior differs.', 'Notallawaityield.',py)
e('Under the hood these write to an `eventfd` or pipe the loop is watching.','The backend wakeup mechanism is platform-specific, such as an eventfd, pipe or completion notification.', 'Windowsotherwakeups.',uv)
e('callbacks never block.','callbacks should avoid blocking the dispatch thread.', 'Goalnotguarantee.',uv)
e('Redis executes commands on one thread for lock-free atomicity.','ordinary Redis commands execute serially, while background/I/O work has separate synchronization.', 'Notlockfreeentiresystem.',re)
e('## Further reading','> [!note] Workload evidence gap\n> Fixed Redis latency/throughput, universal connection capacities and an unreproduced nginx speedup figure are omitted. Measure the deployed workload and runtime. The echo example bounds queued payload per connection; it does not implement production admission control, timeouts or global memory limits.\n\n## Further reading','Visiblemeasurementgaps.',ng+re)
f(1,'prompt','One Node.js event-loop thread owns 5,000 connections and runs a synchronous CPU task for two seconds without yielding. What happens to other callbacks on that same loop during that interval?','Workerthread/platform scope.',nd)
f(1,'text','Their callbacks and timers wait for the running callback to return; the kernel and other threads may still process I/O','NoallkernelIOstops.',nd,0)
f(1,'explanation','Correct. The blocked dispatch thread cannot run another callback on that loop. Kernel networking, existing worker jobs and other event loops can still make progress.','Loopnotwholeprocess/kernel.',nd,0)
f(2,'prompt','In the buffered selectors echo loop, what does this dispatch do?\n\n```python\nfor key, mask in sel.select():\n    key.data(key.fileobj, mask)\n```','Alignnewcallbackmask.',py)
f(2,'workedExample','Registration associates the listener with accept and each connection with its echo callback. select returns ready keys plus event masks; dispatch passes the socket and mask to the registered callback. The echo callback then performs appropriate non-blocking reads/writes, retaining any unsent data.','Alignnewworkingexample.',py)
f(4,'workedExample','1. Run this example as a CommonJS file so require and __filename exist.\n2. Both callbacks are scheduled from an I/O callback. Node documents that setImmediate runs before the zero-delay timeout in this context.\n3. The check phase handles the immediate; timer processing follows according to the current loop version. Since libuv1.45/Node20, recurring timer processing occurs after polling.\n4. The same ordering is not guaranteed when both are scheduled at top level. This is an ordering claim, not an exact elapsed-time guarantee.','Versionedphasesratherthanobsoletecycle.',nd)
f(5,'prompt','A Node.js service uses the default four-worker pool. During a burst of asynchronous crypto.pbkdf2 jobs, profiling shows new outbound requests waiting in dns.lookup before connecting. What best explains that delay?','Causefromprofilingnotguess.',uv)
f(5,'workedExample','1. A new https.request may need dns.lookup unless a connection or address is reused or lookup is customized.\n2. Async pbkdf2 and dns.lookup/getaddrinfo can share libuv worker capacity.\n3. Four busy workers can delay queued lookups in the default configuration.\n4. Validate worker utilization before changing the size; more threads can increase CPU contention. DNS caching or alternate resolution must respect TTLs and resolver semantics, and dns.resolve is not a drop-in substitute for every getaddrinfo behavior.','http.requesthttpswrongAPIandfixtradeoffs.',uv)
f(6,'explanation','In the illustrated timeout-driven loop, timer expiry is checked after the wait. Other loop designs can use timer descriptors or other mechanisms; the next deadline here is still 20 ms away.','Notalltimersneverusesignal.',uv,3)
f(6,'workedExample','1. Earliest modeled deadline:120 ms; current time:100 ms.\n2. Request a 20 ms wait (or less if other work requires it).\n3. epoll_wait can return earlier for I/O/signals or later because of scheduling/granularity.\n4. Read the clock again before computing the next timeout; it is 30 ms only if the new time is exactly120 ms.','Recomputeclocknotassumedexactwakeup.',uv)
f(7,'prompt','On one Redis instance, with ordinary synchronous DEL behavior (lazyfree-lazy-user-del disabled), which operations can perform substantial uninterrupted main-thread work and delay other ordinary commands? Select all that apply.','DELconfigurationandscopedcommandimpact.',re)
f(7,'explanation','Correct under the stated synchronous-free configuration. Freeing a large aggregate can require work proportional to its contents; UNLINK can defer expensive reclamation.','Configurationprerequisite.',un+re,1)
f(7,'explanation','SCAN spreads iteration across calls so other commands can interleave, but COUNT is a work hint, not a strict result or latency bound. Small encodings can return all members at once; no universal short-call guarantee follows.','SCANCOUNTnotbound.',sc,2)
f(7,'explanation','A small GET is normally short relative to full-keyspace/large-aggregate work, but no fixed microsecond latency is guaranteed.','Removeunsupportedtime.',re,4)
f(7,'workedExample','KEYS scans the keyspace in one call; synchronous deletion of a large aggregate and long Lua execution can also monopolize command execution. SCAN is incremental rather than a whole traversal in one command, but COUNT is only a hint and calls can vary in work. A small GET has constant lookup complexity in the ordinary model, not a guaranteed wall-clock latency.','SCANcomplexitywrongOC OUNT.',sc+re)
f(8,'text','To spread connection handling across independent worker processes, reducing shared state and limiting a worker crash to that worker\'s connections','Notalllocksabsent.',ng,1)
f(8,'explanation','Correct. Worker independence provides parallelism and partial fault isolation, though shared-memory features can still synchronize and a failed worker can lose its own connections.','Nozerofaultandnolocks.',ng,1)
f(8,'workedExample','1. Multiple worker loops can run on multiple CPUs; auto attempts to determine a suitable CPU count.\n2. Each worker manages its own connections, reducing contention; shared zones and other coordination can still use locks.\n3. For eight workers and 4,096 connection slots each, the aggregate slot ceiling is32,768.\n4. That is not automatically32,768 proxied clients: upstream sockets and descriptor/resource limits consume slots too.\n5. reuseport distributes connections among listener sockets but does not guarantee equal application work.','Connectionceilingnotclients.',ng)
f(9,'prompt','Profiling an nginx worker identifies blocking file reads on page-cache misses as the cause of delayed unrelated callbacks. On a build/platform supporting threaded file I/O, which change targets that bottleneck?','Tracecauseratherthanambiguousworkload.',ng)
f(9,'explanation','Changing readiness APIs does not make blocking regular-file reads asynchronous. Performance comparisons between select and epoll otherwise depend on workload.','Selectnotstrictlyworseallcases.',ng,1)
f(9,'workedExample','1. A cached read can complete without storage I/O; an uncached read can wait for storage. Actual latency varies.\n2. Waiting in the worker\'s dispatch thread delays its other callbacks.\n3. Supported aio threads configuration offloads applicable file work to a pool, allowing dispatch to continue.\n4. Validate build support, queue limits and workload performance; this does not remove storage latency or all possible blocking.','Nofixedtimings/allreadsautomaticallyoffload.',ng)
f(10,'explanation','Correct for the described unbounded per-stream output queue. Pausing upstream reads propagates TCP flow control, while chunk limits and global admission/memory budgets are also needed to bound the whole process.','Highwaternotglobalhardbound.',py,0)
f(11,'prompt','For Redis6.0 configured with multiple I/O threads and io-threads-do-reads yes, which statements describe the ordinary command/I/O split? Select all that apply.','Versionandreadenabled.',re)
f(11,'explanation','Correct in this configured model. Socket processing can be parallelized; benefits depend on measured workload bottlenecks.','Nohighconnectionalwaysdominates.',re,0)
f(11,'explanation','Correct for ordinary command execution in this version. It preserves serial command execution, not a guarantee that the entire server contains no locks.','Atomicityscope.',re,1)
f(11,'workedExample','In the stated Redis6.0 configuration, I/O threads can assist socket reads/parsing and reply writes, while ordinary commands execute on the main thread. Extra threads can help when that I/O work is the bottleneck; they do not make a long command execute in parallel with other normal commands. With the default io-threads-do-reads no in that version, threaded reads are not enabled merely by increasing io-threads.','Configurationandbenefitqualify.',re)
r['currentModule']={'module':'content/os/07-io','status':'Five pairs full read/corrected:5 lessons/56 questions. Network-stack pair, execution, final consistency and stamp pending. os07a/b/c/d/e applied; do not rerun. Node recurring-phase source fence changed; notify root if shared override mismatch.'}
save([m,q])
