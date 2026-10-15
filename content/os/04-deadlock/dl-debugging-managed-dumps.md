---
id: dl-debugging-managed-dumps
title: Java, Python and Go thread dumps
level: advanced
minutes: 2
sourceLesson: dl-debugging
summary: Java platform-thread tools expose supported monitor and ownable-synchronizer dependencies.
---

## Thread dumps, language by language

The goal is the same everywhere: for each stuck thread, find the lock it's **waiting for** and the locks it **holds**, then draw the wait-for graph by hand.

### Java

For platform threads, use `jstack -l <pid>` or `jcmd <pid> Thread.print -l`; on supported Unix HotSpot JVMs, `kill -3 <pid>` requests a dump to the JVM output. Classic dumps and management deadlock detection do not cover every virtual-thread dependency. The JVM can report current cycles involving object monitors and supported ownable synchronizers:

```
Found one Java-level deadlock:
=============================
"worker-2":
  waiting to lock monitor 0x7f3a...
  (object 0x7128..., a Account),
  which is held by "worker-1"
"worker-1":
  waiting to lock monitor 0x7f3b...
  (object 0x7130..., a Account),
  which is held by "worker-2"
```

(Abridged.) Each thread's stack also shows `- locked <0x...>` lines for the monitors it holds. `ThreadMXBean.findDeadlockedThreads()` exposes detection for platform threads using monitors and supported ownable synchronizers; it does not detect virtual-thread cycles. A watchdog can log and alert on reported cycles.

### Python

Python's `threading.Lock` doesn't record its owner, so a dump shows where threads wait but not who holds the lock. You infer the holder from which thread's stack is inside the matching `with` block.

- `py-spy dump --pid <pid>` prints every thread's Python stack from outside the process, without terminating it. Sampling may briefly pause threads; `--nonblocking` avoids pausing at the cost of potentially inconsistent samples.
- `faulthandler` can dump all threads from inside, on a Unix signal or after a timeout:

```python
import faulthandler
import signal

# kill -USR1 <pid> dumps all threads
faulthandler.register(signal.SIGUSR1)

# watchdog: dump if still running in 60 s
faulthandler.dump_traceback_later(
    60, exit=False)
```

### Go

The runtime notices one special case itself: if the scheduler finds no runnable work or supported source of future wakeups, it may crash with `fatal error: all goroutines are asleep - deadlock!`. A partial deadlock, where some goroutines are stuck while an HTTP server keeps running, is not detected.

For those, send `SIGQUIT` (the process prints all goroutine stacks and exits) or, without killing it, fetch `/debug/pprof/goroutine?debug=2` from `net/http/pprof`. Each goroutine shows a wait reason such as `sync.Mutex.Lock`, plus how long it has waited once that exceeds a minute.

## Key takeaways
- Java platform-thread tools expose supported monitor and ownable-synchronizer dependencies.
- Python primitive locks do not expose owners; infer relationships from application stacks.
- Go’s global no-progress detector misses partial deadlocks; SIGQUIT exits while pprof can preserve the process.

## Further reading
- [Java 21: jstack tool reference](https://docs.oracle.com/en/java/javase/21/docs/specs/man/jstack.html)
- [Python: faulthandler](https://docs.python.org/3/library/faulthandler.html)
- [Go: scheduler global no-progress checks](https://go.dev/src/runtime/proc.go)
