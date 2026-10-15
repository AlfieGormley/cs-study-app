---
id: conc-javascript-queues
title: JavaScript promises and microtask order
level: basic
minutes: 3
sourceLesson: conc-async-await
summary: JavaScript async functions start synchronously before their first await.
---

This unit concerns one JavaScript agent. Other workers may run independently; the ordering below is for the synchronous script, its promise reactions and a timer.

## JavaScript: the event loop is the runtime

In Python you opt in to asyncio. In JavaScript the event loop *is* the execution model, in browsers and in Node.js. Each JavaScript agent has its own execution context; workers can run other agents concurrently. The examples below concern one main-thread agent.

JavaScript distinguishes two queues:

- **JavaScript tasks** (macrotasks): timers (`setTimeout`), I/O callbacks, UI events.
- **Microtasks**: promise reactions (`.then`, the continuation after `await`) and `queueMicrotask`.

At microtask checkpoints, the browser drains the microtask queue, including newly queued microtasks. Node also has event-loop phases and a distinct process.nextTick queue; the simple example below has the shown order in both. So:

```js
// Sync code runs before microtasks.
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

## Key takeaways
- JavaScript async functions start synchronously before their first await.
- Promise reactions and await continuations run as microtasks; timers run later.

## Further reading
- [Primary source: docs.python.org](https://docs.python.org/3/library/asyncio-task.html)
- [Primary source: html.spec.whatwg.org](https://html.spec.whatwg.org/multipage/webappapis.html#event-loops)
- [Primary source: nodejs.org](https://nodejs.org/en/learn/asynchronous-work/event-loop-timers-and-nexttick)
