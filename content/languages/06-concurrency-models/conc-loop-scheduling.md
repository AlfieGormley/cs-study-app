---
id: conc-loop-scheduling
title: How one event loop shares its thread
level: basic
minutes: 3
sourceLesson: conc-async-await
summary: A single-loop task yields when an operation actually suspends.
---

Many concurrent I/O-oriented programs spend much of their time waiting. They are **waiting**: for a database, an HTTP response, a file, a timer. A web server with 10,000 open connections might be using the CPU for a few of them at any moment, while the rest sit idle.

Giving each connection its own OS thread works, but it is heavy: every thread needs its own stack and kernel bookkeeping, and switching between them costs time. A single-threaded async event loop takes a different route: run many tasks on one thread, and switch between them only at the points where they would otherwise wait.

## The intuition: one waiter, many tables

A restaurant does not hire one waiter per table. One waiter takes an order, hands it to the kitchen, and *instead of standing there until it is cooked*, goes to the next table. When the kitchen rings the bell, the waiter comes back.

- The waiter is the **event loop** (one thread).
- Each table is an **async task** (a coroutine).
- "Hand it to the kitchen and move on" is `await`.
- The bell is an **I/O event** from the operating system.

The key word is **cooperative**. In the single-loop examples, tasks yield cooperatively when an await actually suspends; awaiting an already-ready Python awaitable need not yield. If a table keeps the waiter chatting for ten minutes, every other table waits too.

## What the event loop does

```
      +-----------------------+
      |      ready queue      |
      |  [task B] [task C]    |
      +-----------+-----------+
                  |  run one until
                  v  it awaits
           +-------------+
           |   task A    |
           +------+------+
                  | await sock.read()
                  v
   +--------------------------------+
   | waiting: sockets, timers       |
   | OS poller (epoll / kqueue)     |
   +---------------+----------------+
                   | data arrived
                   v
           back on ready queue
```

A conceptual loop repeatedly performs these activities (exact order and batching vary):

1. Run every ready task until it hits an `await` on something not yet available.
2. Ask the OS which sockets have data, and which timers have expired (via `epoll` on Linux, `kqueue` on macOS, IOCP on Windows).
3. Move the tasks waiting on those events back to the ready queue.

Ordinary tasks on the same asyncio loop do not pre-empt one another between suspension points. This does not protect against other threads or synchronous re-entrancy, including eager task creation, and compound operations spanning awaits may still need locks.

## Key takeaways
- A single-loop task yields when an operation actually suspends.
- Ordinary task serialization does not protect against other threads or re-entrancy.

## Further reading
- [Primary source: docs.python.org](https://docs.python.org/3/library/asyncio-task.html)
- [Primary source: html.spec.whatwg.org](https://html.spec.whatwg.org/multipage/webappapis.html#event-loops)
- [Primary source: nodejs.org](https://nodejs.org/en/learn/asynchronous-work/event-loop-timers-and-nexttick)
