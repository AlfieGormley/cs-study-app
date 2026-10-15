---
id: conc-loop-blocking
title: Blocking the loop and forgetting await
level: basic
minutes: 4
sourceLesson: conc-async-await
summary: A blocking call inside an async function still blocks the loop thread.
---

The earlier event-loop model only helps while callbacks and tasks return control promptly. Declaring a function async does not offload its synchronous operations.

## The pitfalls

### Blocking the loop

While synchronous code keeps running on the loop thread, it prevents that loop from running another ordinary task. An `await` helps only when it actually suspends. A CPU-heavy loop, a synchronous library call (`requests.get`, `time.sleep`), or a big `JSON.parse` freezes every other task.

```python
# This sleep occupies the loop thread.
async def bad():
    time.sleep(1)  # blocks the loop!
    return "x"

# gather(bad(), bad()) takes ~2s, not 1s
```

Because `time.sleep` holds the thread, the two waits cannot overlap: the total is the sum, 1 s + 1 s = 2 s, rather than the longest single wait of 1 s.

Fixes: use the async version (`asyncio.sleep`, `aiohttp`, `httpx`), push blocking work to a thread with `await asyncio.to_thread(f)`, or push CPU work to a process pool. In Node, use worker threads for CPU work. asyncio debug mode logs slow callbacks using `loop.slow_callback_duration`, whose default is 100 ms (0.1 seconds).

### Forgetting `await`

```js
// A Promise object is always truthy.
async function isAllowed() {
  return false;
}
if (isAllowed()) grantAccess();  // runs!
```

`isAllowed()` returns a Promise, and every Promise object is truthy. The type-aware typescript-eslint no-misused-promises rule can flag this conditional; no-floating-promises addresses unhandled promise expressions.

### Races still exist, across awaits

Restricting ordinary task switches reduces some races on one loop, but does not make all access safe. A check and an action separated by an `await` can interleave:

```python
# Suspension splits check from update.
balance = 100

async def withdraw(amount):
    global balance
    if balance >= amount:
        await asyncio.sleep(0.1)  # API call
        balance -= amount

# gather(withdraw(80), withdraw(80))
# -> balance == -60
```

Both tasks check `100 >= 80` before either subtracts, so both subtractions happen:

```formula
B_final = B_0 − a − a
B_final = 100 − 80 − 80 = −60
where
B_final: the balance after both withdrawals have finished
B_0: the starting balance, 100 (any currency unit)
a: the amount each task withdraws, 80
In words: both tasks passed the check against the old balance of 100, so both subtract 80, leaving −60 instead of refusing the second withdrawal.
```

With only ordinary tasks on this loop and no re-entrancy or other threads touching the balance, had the check and subtraction run with no suspension between them, the second task would have seen a balance of 20, failed the check and left the balance at 20. Use an `asyncio.Lock` around the whole operation, or do no awaiting between check and act.

### Lost and silent tasks

In asyncio, the loop only keeps a **weak reference** to tasks, so a fire-and-forget `asyncio.create_task(job())` with no saved reference can be garbage-collected mid-flight; the docs say to keep a reference. An unretrieved task exception is normally reported through the loop exception handler when the task is finalized; retaining and inspecting the task allows explicit handling. In Node’s default `--unhandled-rejections=throw` mode (the default since Node 15), an unhandled rejection becomes an uncaught exception if no `unhandledRejection` handler handles it; without an overriding uncaught-exception handler the process exits. Flags and installed handlers can change this policy.

## Function colouring

Async spreads. Await syntax generally requires an async context (JavaScript modules also support top-level await). Callers can instead return or schedule the awaitable, so propagation need not mean every caller immediately awaits. Bob Nystrom called this **function colouring**: red (async) functions can call blue (sync) ones, but not the other way round without help. Libraries end up shipping two versions of everything (`requests` vs `httpx.AsyncClient`).

Green or virtual threads can avoid async function colouring for runtime-supported blocking operations; CPU work and unsupported blocking calls still have costs.

## Threads vs async

| | OS threads | One event-loop thread |
|---|---|---|
| Ordinary switch | Kernel can pre-empt | At actual suspension; callbacks can re-enter |
| Cost per task | Stack and kernel resources | Coroutine state and retained data |
| Parallel CPU | Yes (no GIL) | No, one thread |
| Shared state | Synchronization as required | Protect thread sharing and cross-await invariants |
| Blocking call | Occupies that thread | Stalls that loop |

F# async workflows and C# 5 (2012) are earlier examples of language-level asynchronous syntax; later language features include Python 3.5 (PEP 492), JavaScript (ES2017), Rust (2019), Swift and Kotlin (as `suspend`). Node.js, nginx and Redis use event-driven designs, alongside worker threads or processes in relevant configurations.

## Key takeaways
- A blocking call inside an async function still blocks the loop thread.
- An unawaited JavaScript Promise is truthy, including one that will resolve to false.
- Protect a check and its dependent action as one operation across awaits.
- Keep task handles and observe errors; async syntax alone supplies no lifetime policy.

## Further reading
- [Coroutines and Tasks — Python asyncio docs](https://docs.python.org/3/library/asyncio-task.html)
- [Developing with asyncio — Python docs](https://docs.python.org/3/library/asyncio-dev.html)
- [JavaScript execution model — MDN](https://developer.mozilla.org/en-US/docs/Web/JavaScript/Reference/Execution_model)
- [Using microtasks in JavaScript — MDN](https://developer.mozilla.org/en-US/docs/Web/API/HTML_DOM_API/Microtask_guide)
- [The Node.js event loop — Node.js docs](https://nodejs.org/en/learn/asynchronous-work/event-loop-timers-and-nexttick)
- [What Color is Your Function? — Bob Nystrom](https://journal.stuffwithstuff.com/2015/02/01/what-color-is-your-function/)
- [Primary verification source 3](https://fastapi.tiangolo.com/async/)
- [Primary verification source 4](https://typescript-eslint.io/rules/no-misused-promises/)
- [Primary source: html.spec.whatwg.org](https://html.spec.whatwg.org/multipage/webappapis.html#event-loops)
