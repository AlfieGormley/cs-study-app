---
id: conc-async-await
title: async/await and event loops
level: basic
minutes: 12
summary: How one thread can juggle thousands of connections, what `await` really does, how Python's asyncio and JavaScript's event loop schedule work, and the classic ways to get it wrong.
---

Many concurrent I/O-oriented programs spend much of their time waiting. They are **waiting**: for a database, an HTTP response, a file, a timer. A web server with 10,000 open connections might be using the CPU for a few of them at any moment, while the rest sit idle.

Giving each connection its own OS thread works, but it is heavy: every thread needs its own stack and kernel bookkeeping, and switching between them costs time. A single-threaded async event loop takes a different route: run many tasks on one thread, and switch between them only at the points where they would otherwise wait.

## The intuition: one waiter, many tables

A restaurant does not hire one waiter per table. One waiter takes an order, hands it to the kitchen, and *instead of standing there until it is cooked*, goes to the next table. When the kitchen rings the bell, the waiter comes back.

- The waiter is the **event loop** (one thread).
- Each table is a **task** (a coroutine).
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

## Python asyncio

An `async def` function is a **coroutine function**. Calling it does *not* run it; it returns a coroutine object that runs when awaited or scheduled.

```python
import asyncio, time

async def fetch(name, delay):
    await asyncio.sleep(delay)  # fake I/O
    return name

async def main():
    t = time.perf_counter()
    a = await fetch("a", 1)
    b = await fetch("b", 1)
    print(time.perf_counter() - t)  # ~2.0

    t = time.perf_counter()
    r = await asyncio.gather(
        fetch("a", 1), fetch("b", 1),
        fetch("c", 1))
    print(r)  # ['a', 'b', 'c']
    print(time.perf_counter() - t)  # ~1.0

asyncio.run(main())
```

The first half takes two seconds: `await` means "pause *this* coroutine until the result is ready", so the second fetch does not start until the first finishes. `async` does not make code concurrent on its own; you have to start several things before awaiting them. `asyncio.gather` (or `asyncio.create_task`, or a `TaskGroup`, see lesson 6) does that.

Tasks can interleave at suspension points:

```python
async def worker(name, n):
    for i in range(n):
        print(name, i)
        await asyncio.sleep(0)  # yield

async def main():
    await asyncio.gather(
        worker("A", 2), worker("B", 2))
# prints: A 0, B 0, A 1, B 1
```

`asyncio.sleep(0)` is the idiom for "let others run". Without any `await` inside the loop, A would print both lines before B started.

## JavaScript: the event loop is the runtime

In Python you opt in to asyncio. In JavaScript the event loop *is* the execution model, in browsers and in Node.js. Each JavaScript agent has its own execution context; workers can run other agents concurrently. The examples below concern one main-thread agent.

JavaScript distinguishes two queues:

- **Tasks** (macrotasks): timers (`setTimeout`), I/O callbacks, UI events.
- **Microtasks**: promise reactions (`.then`, the continuation after `await`) and `queueMicrotask`.

At microtask checkpoints, the browser drains the microtask queue, including newly queued microtasks. Node also has event-loop phases and a distinct process.nextTick queue; the simple example below has the shown order in both. So:

```js
console.log('A');
setTimeout(() => console.log('B'), 0);
Promise.resolve()
  .then(() => console.log('C'));
queueMicrotask(() => console.log('D'));
(async () => {
  console.log('E');
  await null;
  console.log('F');
})();
console.log('G');
// A E G C D F B
```

Walk through it: the script itself is one task. `A`, `E` and `G` print synchronously. Note `E`: an `async` function in JavaScript runs **immediately** up to its first `await`, unlike Python. Then the microtasks run in the order they were queued: `C`, `D`, `F`. Only then does the timer task run: `B`, even though its delay was 0.

> [!warning] Starting eagerly vs lazily
> Calling an async function in JavaScript starts it and returns a promise. Calling one in Python just creates a coroutine object; nothing happens until it is awaited or wrapped in a task. Python warns "coroutine ... was never awaited" if you forget.

## The pitfalls

### Blocking the loop

Anything that does not `await` holds the only thread. A CPU-heavy loop, a synchronous library call (`requests.get`, `time.sleep`), or a big `JSON.parse` freezes every other task.

```python
async def bad():
    time.sleep(1)  # blocks the loop!
    return "x"

# gather(bad(), bad()) takes ~2s, not 1s
```

Fixes: use the async version (`asyncio.sleep`, `aiohttp`, `httpx`), push blocking work to a thread with `await asyncio.to_thread(f)`, or push CPU work to a process pool. In Node, use worker threads for CPU work. asyncio debug mode logs slow callbacks using loop.slow_callback_duration, whose default is 100 ms.

### Forgetting `await`

```js
async function isAllowed() {
  return false;
}
if (isAllowed()) grantAccess();  // runs!
```

`isAllowed()` returns a Promise, and every Promise object is truthy. The type-aware typescript-eslint no-misused-promises rule can flag this conditional; no-floating-promises addresses unhandled promise expressions.

### Races still exist, across awaits

Restricting ordinary task switches reduces some races on one loop, but does not make all access safe. A check and an action separated by an `await` can interleave:

```python
balance = 100

async def withdraw(amount):
    global balance
    if balance >= amount:
        await asyncio.sleep(0.1)  # API call
        balance -= amount

# gather(withdraw(80), withdraw(80))
# -> balance == -60
```

Both tasks check `100 >= 80` before either subtracts. Use an `asyncio.Lock` around the whole operation, or do no awaiting between check and act.

### Lost and silent tasks

In asyncio, the loop only keeps a **weak reference** to tasks, so a fire-and-forget `asyncio.create_task(job())` with no saved reference can be garbage-collected mid-flight; the docs say to keep a reference. An unretrieved task exception is normally reported through the loop exception handler when the task is finalized; retaining and inspecting the task allows explicit handling. In Node, an unhandled promise rejection terminates the process by default (since Node 15).

## Function colouring

Async spreads. Await syntax generally requires an async context (JavaScript modules also support top-level await). Callers can instead return or schedule the awaitable, so propagation need not mean every caller immediately awaits. Bob Nystrom called this **function colouring**: red (async) functions can call blue (sync) ones, but not the other way round without help. Libraries end up shipping two versions of everything (`requests` vs `httpx.AsyncClient`).

Green or virtual threads can avoid async function colouring for runtime-supported blocking operations; CPU work and unsupported blocking calls still have costs.

## Threads vs async

| | OS threads | One event-loop thread |
|---|---|---|
| Switch | Anywhere (pre-emptive) | Only at `await` |
| Cost per task | Stack and kernel resources | Coroutine state and retained data |
| Parallel CPU | Yes (no GIL) | No, one thread |
| Shared state | Synchronization as required | Protect thread sharing and cross-await invariants |
| Blocking call | Fine | Freezes everything |

F# async workflows and C# 5 (2012) helped popularize structured async syntax; later language features include Python 3.5 (PEP 492), JavaScript (ES2017), Rust (2019), Swift and Kotlin (as `suspend`). Node.js, nginx and Redis use event-driven designs, alongside worker threads or processes in relevant configurations.

## Key takeaways
- Single-thread event loops multiplex tasks cooperatively; async/await itself does not require a single-threaded executor.
- The event loop runs ready tasks, then asks the OS (epoll/kqueue/IOCP) which waits have finished.
- `await` pauses the current coroutine; to run things concurrently, start them first (`gather`, `create_task`, `Promise.all`).
- JavaScript drains all microtasks (promise continuations) before the next task (timers, I/O).
- Python coroutines start lazily; JavaScript async functions start eagerly.
- Never block the loop; races are still possible across an `await`; keep references to tasks.

## Further reading
- [Coroutines and Tasks — Python asyncio docs](https://docs.python.org/3/library/asyncio-task.html)
- [Developing with asyncio — Python docs](https://docs.python.org/3/library/asyncio-dev.html)
- [JavaScript execution model — MDN](https://developer.mozilla.org/en-US/docs/Web/JavaScript/Reference/Execution_model)
- [Using microtasks in JavaScript — MDN](https://developer.mozilla.org/en-US/docs/Web/API/HTML_DOM_API/Microtask_guide)
- [The Node.js event loop — Node.js docs](https://nodejs.org/en/learn/asynchronous-work/event-loop-timers-and-nexttick)
- [What Color is Your Function? — Bob Nystrom](https://journal.stuffwithstuff.com/2015/02/01/what-color-is-your-function/)
- [Primary verification source 3](https://fastapi.tiangolo.com/async/)
- [Primary verification source 4](https://typescript-eslint.io/rules/no-misused-promises/)
