---
id: conc-runtime-blocking
title: Erlang, virtual threads and runtime-aware blocking
level: intermediate
minutes: 3
sourceLesson: conc-coroutines-green-threads
summary: Java virtual-thread pinning rules depend on the JDK release and blocking operation.
---

Go’s parking mechanisms are one implementation of lightweight tasks. Erlang, Java and gevent make different choices; the common question is what happens when a task blocks in code the runtime cannot suspend.

### Erlang: processes

Erlang's lightweight **processes** are green threads with their own small heap each (a few hundred words to start). The BEAM VM pre-empts by counting **Erlang reductions**, units of work roughly equal to function calls: each process gets a budget of a few thousand, then goes to the back of the queue. Reduction accounting limits ordinary Erlang execution, but long-running native functions can still block a scheduler unless designed to yield or use dirty schedulers. The later actor units cover Erlang’s process protocols.

### Java: virtual threads

Java 21 (JEP 444) added **virtual threads**: `java.lang.Thread` objects scheduled by the JVM onto a small pool of **carrier** (platform) threads.

```java
// Supported sleep can free the carrier.
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
- Java virtual-thread pinning rules depend on the JDK release and blocking operation.
- A lightweight runtime cannot hide every native blocking call; profile and use supported operations.

## Further reading
- [Remove the old Rust runtime — original Rust RFC 230](https://rust-lang.github.io/rfcs/0230-remove-runtime.html)
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
