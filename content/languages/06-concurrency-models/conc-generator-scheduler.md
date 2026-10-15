---
id: conc-generator-scheduler
title: Resumable frames and a tiny scheduler
level: intermediate
minutes: 3
sourceLesson: conc-coroutines-green-threads
summary: A generator preserves its local state at yield and resumes at next.
---

The last lesson used `await` as a black box: "pause here, resume later". This lesson opens the box. Underneath every async/await system, and every "lightweight thread" runtime, sits the same idea: a **coroutine**, a function that can suspend in the middle and carry on later from exactly where it stopped.

How a language implements that pause decides a lot: whether you get function colouring, how much memory a task costs, and whether ordinary blocking code is fine to write.

## Subroutines vs coroutines

An ordinary subroutine runs from invocation until it returns or exits exceptionally, without exposing coroutine-style resumable suspension. You call it, it runs to the end, its stack frame is thrown away.

A **coroutine** can **yield** part way through. Its local variables and position are kept, and the next resume continues from that point. Conway described coroutines in his 1963 compiler paper. An exact first-use date is omitted here because this audit has not established it from a primary historical artifact.

Python generators are the most familiar example:

```python
# next resumes until the next yield.
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
# Each yield returns to this queue.
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

## Key takeaways
- A generator preserves its local state at yield and resumes at next.
- A queue plus one resumable step per turn gives a cooperative round-robin scheduler.

## Further reading
- [Primary source: peps.python.org](https://peps.python.org/pep-0342/)
- [Primary source: www.lua.org](https://www.lua.org/manual/5.4/manual.html#2.6)
- [Primary source: go.dev](https://go.dev/src/runtime/stack.go)
- [Primary source: openjdk.org](https://openjdk.org/jeps/444)
- [Primary source: openjdk.org](https://openjdk.org/jeps/491)
