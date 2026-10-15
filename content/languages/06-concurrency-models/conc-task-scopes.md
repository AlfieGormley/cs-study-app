---
id: conc-task-scopes
title: TaskGroup failure and cooperative cancellation
level: advanced
minutes: 4
sourceLesson: conc-structured-rust
summary: A structured scope waits for its children, including their cancellation cleanup.
---

Every model so far has left two problems to the programmer's discipline. **Task lifetimes**: a goroutine or `create_task` can outlive the code that started it, so tasks leak and errors vanish (the event-loop and channel units). **Sharing**: nothing stops two threads touching the same data unsafely (the shared-memory units), unless isolation rules or synchronization APIs prevent unsafe sharing.

This lesson covers two approaches to these problems. **Structured concurrency** ties every task's lifetime to a lexical block. **Rust** keeps shared memory but makes the compiler prove there are no data races.

## Structured concurrency

### The problem with "go"

In 2018 Nathaniel J. Smith, author of Python's Trio library, argued in *Go statement considered harmful* that `go f()`, `create_task`, `thread.start()` and friends are the `goto` of concurrency. Once you call one, control splits in two, and nothing in the code's shape says where the second path ends.

```
 unstructured            structured
   main                    main
    |---spawn--> task       |
    |              |        +--------+
    |  (returns)   |        | task 1 |
    x              |        | task 2 |
          still running...  +--------+
                            | both done
                            v
```

Dijkstra's argument against `goto` was that you could no longer reason about a block as a unit. Smith's point is the same: with unstructured spawns, you cannot know whether a function has finished its work when it returns, where an exception in a child goes, or how to cancel everything it started.

### The rule

Structured concurrency adds one rule: **a task may not outlive the scope that started it**. Concretely, a fail-fast task scope such as a Trio nursery or asyncio TaskGroup typically:

1. Waits for all its children before the block exits.
2. If a child has an ordinary failure, requests sibling cancellation and propagates failure to the parent; cancellation exceptions and supervisory policies have distinct rules.
3. If the parent is cancelled, cancels all children.

The call tree of tasks then mirrors the block structure of the code, just as it does for ordinary function calls.

### Python: TaskGroup

Python 3.11 added `asyncio.TaskGroup`, modelled on Trio's nurseries:

```python
# Group exit waits for child cleanup.
import asyncio

async def boom():
    await asyncio.sleep(0.1)
    raise ValueError("bad")

async def slow():
    try:
        await asyncio.sleep(10)
    except asyncio.CancelledError:
        print("slow cancelled")
        raise

async def both():
    async with asyncio.TaskGroup() as tg:
        tg.create_task(slow())
        tg.create_task(boom())

async def main():
    try:
        await both()
    except* ValueError as eg:
        print("caught", eg.exceptions)

asyncio.run(main())
```

After about 0.1 seconds this prints `slow cancelled`, then `caught (ValueError('bad'),)`. `boom` fails, the group cancels `slow` instead of letting it run for 10 seconds, waits for it to finish cancelling, and raises an **ExceptionGroup**, because several children can fail at once. `except*` (also new in 3.11) matches exceptions inside a group by type.

Compare `asyncio.gather`: by default, if one awaitable fails, `gather` raises that error but does not itself cancel the other awaitables. The caller may still retain their handles, and loop shutdown may later cancel them.

> [!tip] Re-raise CancelledError
> Cancellation requests delivery of CancelledError at the next opportunity; it does not pre-empt arbitrary blocking or CPU-bound code. If you catch it to clean up, re-raise it. Swallowing it can interfere with cancellation and delay group exit; the group still waits for its children.

### Other languages

- **Kotlin**: `coroutineScope { launch { ... } }` waits for its children and cancels them all if one fails. `supervisorScope` lets siblings survive a failure. `GlobalScope.launch` is the unstructured escape hatch, and is discouraged.
- **Swift**: `async let` and `withTaskGroup` are structured; `Task { }` is not.
- **Java**: `StructuredTaskScope`, designed for virtual threads. It has been a preview API since JDK 21 (re-previewed through the JDK 27 proposal). As checked on 2026-10-15, JEP 543 is Proposed to Target JDK 28 and proposes finalising it; that is a proposal status, not a guarantee about a released JDK. The example below uses the JDK 25 preview factory API, which requires preview flags and is different from JDK 21’s constructor API.

```java
// JDK 25 preview: join or cancel peers.
try (var scope =
       StructuredTaskScope.open()) {
  var user  = scope.fork(() -> findUser());
  var order = scope.fork(() -> getOrder());
  scope.join();  // throws if either failed
  return new Response(user.get(),
                      order.get());
}  // no subtask can outlive this block
```

## Key takeaways
- A structured scope waits for its children, including their cancellation cleanup.
- TaskGroup and gather have different sibling-failure policies.
- Structured lifetime and sibling-failure policy are related but distinct API choices.
- Java preview structured-concurrency APIs must be tied to a particular JDK release.

## Further reading
- [Primary source: docs.python.org](https://docs.python.org/3/library/asyncio-task.html#task-groups)
- [Primary source: doc.rust-lang.org](https://doc.rust-lang.org/nomicon/send-and-sync.html)
- [Primary source: doc.rust-lang.org](https://doc.rust-lang.org/std/thread/fn.scope.html)
- [Primary source: doc.rust-lang.org](https://doc.rust-lang.org/std/sync/struct.Mutex.html)
