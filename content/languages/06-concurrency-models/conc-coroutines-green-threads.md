---
id: conc-coroutines-green-threads
title: Coroutines and green threads
level: intermediate
minutes: 13
summary: Functions that can pause and resume, the difference between stackless and stackful coroutines, and how Go, Erlang and Java virtual threads schedule millions of lightweight threads on a handful of OS threads.
---

The last lesson used `await` as a black box: "pause here, resume later". This lesson opens the box. Underneath every async/await system, and every "lightweight thread" runtime, sits the same idea: a **coroutine**, a function that can suspend in the middle and carry on later from exactly where it stopped.

How a language implements that pause decides a lot: whether you get function colouring, how much memory a task costs, and whether ordinary blocking code is fine to write.

## Subroutines vs coroutines

An ordinary subroutine runs from invocation until it returns or exits exceptionally, without exposing coroutine-style resumable suspension. You call it, it runs to the end, its stack frame is thrown away.

A **coroutine** can **yield** part way through. Its local variables and position are kept, and the next resume continues from that point. Conway described coroutines in his 1963 compiler paper. An exact first-use date is omitted here because this audit has not established it from a primary historical artifact.

Python generators are the most familiar example:

```python
def counter():
    print("start")
    yield 1
    print("middle")
    yield 2

g = counter()   # nothing runs yet
print(next(g))  # start, 1
print(next(g))  # middle, 2
```

Each `next` resumes the frame until the following `yield`. A third `next` would raise `StopIteration`.

## A scheduler in fifteen lines

Coroutines plus a queue is already a concurrency runtime. This is, in miniature, what asyncio's event loop does:

```python
from collections import deque

def task(name, n):
    for i in range(n):
        print(name, i)
        yield          # give way

def run(tasks):
    q = deque(tasks)
    while q:
        t = q.popleft()
        try:
            next(t)    # run one step
        except StopIteration:
            continue   # finished: drop
        q.append(t)    # back of queue

run([task("A", 2), task("B", 3)])
```

Output: `A 0`, `B 0`, `A 1`, `B 1`, `B 2`. Each task runs until it yields, then goes to the back of the queue. Add "and if it yielded a socket, park it until the OS says the socket is ready" and you have an event loop. Python's `async def` grew out of exactly this: PEP 342 (2005) let generators receive values, PEP 380 added `yield from`, and PEP 492 (2015) gave the pattern its own syntax.

## Stackless coroutines

Python generators, async functions in Python, JavaScript, C#, Rust and Kotlin, and C++20 coroutines are all **stackless**. Only the coroutine's *own* frame can be suspended. Implementations preserve resumable state, often using compiler-generated state machines. Python retains interpreter frames and instruction position rather than necessarily generating the same explicit struct used by Rust.

```
async fn get() {        state 0: start
  let a = read().await;  -> state 1
  let b = read().await;  -> state 2
  a + b                  -> done
}
```

A concrete compiler-generated Rust future has a statically known size; it can live inside another struct with no heap allocation at all.

The catch: a function *called from* the coroutine cannot suspend it.

```python
def helper():
    yield "deep"

def task():
    helper()   # makes a generator,
               # never runs it!
    yield "top"
```

`task` must write `yield from helper()` to pass the suspension up. That is the root of **function colouring**: every function on the path to a suspension point must itself be a coroutine (`async`), because each frame has to be turned into a state machine separately.

## Stackful coroutines

A **stackful** coroutine has its own separate call stack. Nested calls can suspend the coroutine stack where the runtime permits yielding; native-call boundaries may impose restrictions. Lua, Ruby's Fibers and Python's `greenlet` library work this way.

```lua
local function helper()
  coroutine.yield("deep")
end

local co = coroutine.create(function()
  helper()          -- ordinary call
  return "done"
end)

print(coroutine.resume(co)) -- true deep
print(coroutine.resume(co)) -- true done
```

`helper` is a plain function, yet it suspends `co` from two frames down. No colouring is needed. Preserving nested call state costs memory; implementations may use separate native stacks, copied stacks, or VM-managed frames.

| | Stackless | Stackful |
|---|---|---|
| Suspend from | Own frame only | Any depth |
| Memory | Exact-size object | A stack |
| Colouring | Yes | No |
| Examples | Python, JS, Rust, C# | Lua, Go, greenlet |

## Green threads

Put stackful coroutines under a scheduler that *pretends they are threads* and you get **green threads**: threads managed by the language runtime rather than the kernel. The programmer writes ordinary, blocking-looking code; the runtime quietly switches threads whenever one would block.

The mapping between user threads and OS threads has three shapes:

```
1:1  (Java platform threads, C++)
 T1   T2   T3      user threads
 |    |    |
 K1   K2   K3      OS threads

M:1  (early Java, Python greenlet)
 T1   T2   T3
  \   |   /
     K1            one OS thread

M:N  (Go, Erlang, Java virtual threads)
 T1 T2 T3 T4 T5 T6
  \  |  \/  |  /
     K1   K2       a few OS threads
```

M:1 is simple but cannot use more than one core, and one blocking system call freezes everything. Early JVMs on Solaris shipped green threads like this and abandoned them for 1:1 native threads. M:N gets both cheap threads and multicore, at the cost of a sophisticated runtime.

### Go: goroutines

`go f()` starts a **goroutine**. The runtime uses a small initial stack, with a 2 KiB minimum in the cited implementation that grows on demand: when a function's prologue finds too little room, the runtime allocates a stack twice the size and copies the old one over, fixing up pointers. Large counts are possible, but memory, retained state and work per goroutine still limit scale.

The scheduler uses three structures, usually written **G, M, P**:

- **G**: a goroutine (its stack and state).
- **M**: an OS thread ("machine").
- **P**: a processor slot with a local run queue. There are `GOMAXPROCS` of them, with defaults based on available logical CPUs and, since Go 1.25 on Linux, container CPU limits; defaults can update as constraints change.

An M must hold a P to run Gs. An idle P **steals** half the run queue of a busy one. When a goroutine reads a socket that has no data, the runtime registers it with the **netpoller** (epoll/kqueue) and parks the G; the M runs something else. When a goroutine enters a genuinely blocking system call, the M stays blocked with it, but a monitor thread (`sysmon`) hands the P to another M so the other goroutines keep running.

Scheduling is effectively **pre-emptive**. Before Go 1.14, pre-emption relied heavily on cooperative safe points such as function prologues, so a tight loop like `for {}` could stall the garbage collector. Go 1.14 added asynchronous pre-emption on supported platforms, including a signal-based implementation on Unix.

### Erlang: processes

Erlang's lightweight **processes** are green threads with their own small heap each (a few hundred words to start). The BEAM VM pre-empts by counting **reductions**, roughly function calls: each process gets a budget of a few thousand, then goes to the back of the queue. Reduction accounting limits ordinary Erlang execution, but long-running native functions can still block a scheduler unless designed to yield or use dirty schedulers. Lesson 5 covers what Erlang does with them.

### Java: virtual threads

Java 21 (JEP 444) added **virtual threads**: `java.lang.Thread` objects scheduled by the JVM onto a small pool of **carrier** (platform) threads.

```java
try (var ex = Executors
       .newVirtualThreadPerTaskExecutor()) {
  for (int i = 0; i < 10_000; i++) {
    ex.submit(() -> {
      Thread.sleep(1000); // unmounts
      return null;
    });
  }
}  // waits for all submitted tasks
```

For supported blocking operations, a virtual thread can unmount while its continuation state is retained in heap stack chunks. Some operations instead block a carrier or require compensation. The point is that existing blocking code (JDBC, `InputStream`) scales without being rewritten in async style.

> [!warning] Pinning
> A virtual thread that blocks while it cannot unmount **pins** its carrier, making that carrier unavailable for other virtual threads while it is blocked. In JDK 21 to 23 that happened when blocking inside a `synchronized` block; JDK 24 (JEP 491) fixed that case. Blocking inside native code still pins.

## Python's green threads: gevent

Python has no built-in green threads, but `gevent` builds them from `greenlet` (stackful coroutines) plus **monkey-patching**: it replaces `socket`, `time.sleep` and friends with versions that switch greenlets instead of blocking. Ordinary `requests` code then becomes concurrent. It works, but any C extension doing its own blocking I/O (some database drivers) bypasses the patch and blocks the hub thread and its greenlets; independently running OS threads are a separate matter.

That illustrates the general rule: **cheap parking requires runtime-aware blocking or an offload/compensation mechanism**. Go and Erlang control their whole standard library; Java spent years reworking `java.io` and `java.net` for Loom; gevent has to patch from the outside.

## Choosing between them

| Concern | Async/await | Green threads |
|---|---|---|
| Colouring | Yes | No |
| Task storage | Resumable state plus retained data | Stack plus retained data |
| Where it switches | Visible `await` | Hidden |
| C interop | Easy | Awkward |
| Scheduling | Executor/runtime | Runtime scheduler, built in or library |

Hidden switch points are a double-edged sword. With `await`, you can see every place another task might run. With goroutines or virtual threads, any call might switch, and with M:N on several cores, tasks really do run in parallel, so you are back to needing locks or channels for shared data. Rust chose stackless async partly because green threads need a runtime and complicate calling C, and Rust removed its early green threads before 1.0.

## Key takeaways
- A coroutine can suspend and resume, keeping its local state. Generators plus a queue already make a scheduler.
- **Stackless** coroutines (Python, JS, Rust, C#, Kotlin) compile to state machines: cheap, but only the top frame can suspend, which causes function colouring.
- **Stackful** coroutines (Lua, greenlet, Go) have their own stack, so a call at any depth can suspend.
- **Green threads** are runtime-scheduled threads. M:N runtimes (Go, Erlang, Java virtual threads) give cheap threads and multicore.
- Go: small growable stacks (a cited minimum of 2 KiB), G-M-P scheduler, work stealing, netpoller, signal-based pre-emption since 1.14.
- Green threads need every blocking call to go through the runtime; otherwise one call blocks the carrier (pinning, unpatched C code).

## Further reading
- [Coroutine — Wikipedia](https://en.wikipedia.org/wiki/Coroutine)
- [Green thread — Wikipedia](https://en.wikipedia.org/wiki/Green_thread)
- [JEP 444: Virtual Threads — OpenJDK](https://openjdk.org/jeps/444)
- [JEP 491: Synchronize Virtual Threads without Pinning — OpenJDK](https://openjdk.org/jeps/491)
- [PEP 342: Coroutines via Enhanced Generators](https://peps.python.org/pep-0342/)
- [Lua 5.4 Reference Manual: Coroutines](https://www.lua.org/manual/5.4/manual.html#2.6)
- [Go 1.14 Release Notes (asynchronous pre-emption)](https://go.dev/doc/go1.14)
- [Primary verification source 1](https://go.dev/src/runtime/stack.go)
- [Primary verification source 2](https://go.dev/doc/go1.25)
- [Primary verification source 4](https://www.erlang.org/doc/system/eff_guide_processes.html)
- [Primary verification source 5](https://www.gevent.org/intro.html)
- [Primary verification source 7](https://docs.oracle.com/en/java/javase/24/migrate/jdk-migration-guide.pdf)
- [Primary verification source 9](https://melconway.com/Home/pdf/compiler.pdf)
