---
id: pattern-observer-lifecycles
title: Observers, subscription and failure
level: intermediate
minutes: 3
sourceLesson: pattern-behavioural-1
summary: Observers decouple the emitter from an open-ended set of reactions.
---

## Observer pattern

### The problem

When one object (the **observer subject**) changes, several others need to react: update a UI, invalidate a cache, send an email, write an application audit log. The subject shouldn't know who they are, or it ends up importing half the codebase.

### The structure

```
 Subject                     Observer
 -observers: [Observer] ---> +update(e)
 +subscribe(o)                 ^    ^
 +unsubscribe(o)               |    |
 +notify(e): for o in obs:   Cache Mailer
             o.update(e)
```

Also called **publish-subscribe** when a broker sits in between, though some people reserve that term for systems where publisher and subscriber don't know about each other at all.

### In Python

```python
class Event:
    def __init__(self):
        self._handlers = []

    def subscribe(self, fn):
        self._handlers.append(fn)
        # The closure remembers this
        # handler.
        def unsubscribe():
            self._handlers.remove(fn)
        return unsubscribe

    def emit(self, *args):
        # Snapshot: removals cannot shift
        # the collection being traversed.
        for fn in list(self._handlers):
            fn(*args)

order_paid = Event()
log = []
stop = order_paid.subscribe(
    lambda oid: log.append(f"email {oid}"))
order_paid.subscribe(
    lambda oid: log.append(f"ship {oid}"))

order_paid.emit(42)
stop()                  # unsubscribe email
order_paid.emit(43)
print(log)
# ['email 42', 'ship 42', 'ship 43']
```

Two details matter. `subscribe` returns a way to **unsubscribe**. And `emit` loops over a **copy** of the list, so a handler that unsubscribes itself mid-loop doesn't make the loop skip the next one. The snapshot also means a newly subscribed handler waits until the next emission, while a handler removed after the snapshot can still run in this emission. The returned unsubscribe closure is one-shot in this toy: calling it twice raises `ValueError`; an application API can deliberately make cancellation idempotent.

### Pitfalls

- **Lapsed listeners (memory leaks).** The subject holds a strong reference to each observer. If an observer is discarded but never unsubscribes, it remains reachable while the subject retains it and can keep receiving events. Fixes: always unsubscribe, or hold observers via `weakref`.
- **Notification order.** This `Event` calls handlers in subscription order. Other dispatchers can define a different order or leave it unspecified. Do not make correctness depend on an order the dispatcher has not promised.
- **Exceptions.** If one handler raises, do the remaining ones still run? Decide deliberately.
- **Cascades.** Observer A's handler changes subject B, which notifies C, which changes A again. Event chains become very hard to trace and debug.
- **Synchronous notification in this example.** A slow handler (sending email) blocks the code that emitted the event. Real systems often push slow work onto a queue.

### When not to use it

- When there's exactly one known receiver. A direct call is easier to read, trace and debug.
- When the order of reactions or their success matters to correctness (charge the card, *then* ship). Write that as explicit sequential code, or a workflow.

### In real libraries

- **Django signals**: `post_save.connect(handler, sender=Order)`. Receivers are held by **weak reference** by default (`weak=True`), which avoids lapsed listeners but means a lambda or local function can be garbage-collected and silently stop firing.
- **Qt signals and slots**: `button.clicked.connect(handler)`.
- **The browser DOM**: `addEventListener("click", fn)` and `removeEventListener`.
- **Python's `logging`**: a logger routes eligible records to handlers subject to levels, filters and propagation settings.
- **Reactive libraries** (RxJS, RxPY) generalise observers into streams with operators such as `map`, `filter` and `debounce`.

## Key takeaways
- Observers decouple the emitter from an open-ended set of reactions.
- Make subscription lifetime, notification order and exception policy explicit.
- A snapshot avoids skipping callbacks when the live handler list changes.
- Synchronous observers run on the emitter’s call path and can delay or interrupt it.

## Further reading
- [Signals — Django documentation](https://docs.djangoproject.com/en/stable/topics/signals/)
