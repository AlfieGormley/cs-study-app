---
id: pattern-behavioural-1
title: Strategy, observer and command
level: intermediate
minutes: 15
summary: Three behavioural patterns you will use weekly, swappable algorithms, change notification and requests as objects, with Python versions, failure modes such as lapsed listeners, and real uses in Django, Qt and the standard library.
---

Behavioural patterns are about **who does what** and **how objects talk**. They move decisions and messages around so that the parts that change often are separated from the parts that don't.

The three in this lesson are the ones you will meet most often:

- **Strategy** turns *an algorithm* into a value you can swap.
- **Observer** turns *"something happened"* into a notification any number of listeners can receive.
- **Command** turns *a request* into an object you can store, queue, log or undo.

All three are partly built into Python, because functions and closures are first-class values.

## Strategy

### The problem

A piece of code needs one of several interchangeable algorithms: pricing rules, compression codecs, retry policies, sort orders. Hard-coding them as an `if/elif` chain means editing (and retesting) the core every time a new one appears.

### The structure

```
  Context -----------> Strategy
  +strategy           +run(data)
  +do(): uses it        ^     ^
                        |     |
                     FastA   CheapB
```

The context holds a strategy and delegates the varying step to it. Callers pick which strategy to give it.

### In Python

Java can use lambdas or method references for functional-interface strategies; Python commonly passes a function directly:

```python
def flat(total):
    return total

def ten_off(total):
    return total * 0.9

def bulk(total):
    if total > 50:
        return total - 5
    return total

def checkout(items, pricing=flat):
    return pricing(sum(items))

print(checkout([30, 40]))           # 70
print(checkout([30, 40], ten_off))  # 63.0
print(checkout([30, 40], bulk))     # 65
```

If a strategy needs configuration, use a closure, `functools.partial`, or a small class with `__call__`. If it needs several related methods (say, `encode` *and* `decode`), a class with those methods is clearer than a pair of functions.

> [!tip] Replace the `if` chain with a dict
> `PRICING = {"flat": flat, "sale": ten_off}` then `PRICING[name](total)` is strategy plus a lookup table. Adding a rule is one new function and one dict entry.

### When not to use it

- When there's only one algorithm and no real prospect of another.
- When strategies need very different inputs. A shared signature that has to carry everything any strategy might want is a sign the abstraction is wrong.
- When callers shouldn't be choosing. Exposing a strategy parameter is a public commitment you'll have to support.

### In real libraries

- **`sorted(key=...)`, `max(key=...)`, `min(key=...)`**: the comparison key is a strategy.
- **`json.dumps(default=..., cls=...)`**: plug in how unknown types are serialised.
- **Django's `PASSWORD_HASHERS`**: a list of hasher classes (PBKDF2, Argon2, bcrypt and so on) with a common interface. The first is used for new passwords; the rest can still verify old ones.
- **requests' `auth=`**: pass `HTTPBasicAuth`, `HTTPDigestAuth` or your own callable that modifies the request.
- **Java's `Comparator`**, and **scikit-learn**, where any estimator with `fit` and `predict` can be dropped into the same code.

## Observer

### The problem

When one object (the **subject**) changes, several others need to react: update a UI, invalidate a cache, send an email, write an audit log. The subject shouldn't know who they are, or it ends up importing half the codebase.

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
        def unsubscribe():
            self._handlers.remove(fn)
        return unsubscribe

    def emit(self, *args):
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

Two details matter. `subscribe` returns a way to **unsubscribe**. And `emit` loops over a **copy** of the list, so a handler that unsubscribes itself mid-loop doesn't make the loop skip the next one.

### Pitfalls

- **Lapsed listeners (memory leaks).** The subject holds a strong reference to each observer. If an observer is discarded but never unsubscribes, it remains reachable while the subject retains it and can keep receiving events. Fixes: always unsubscribe, or hold observers via `weakref`.
- **Unknown order.** Observers usually run in subscription order, but code shouldn't depend on it.
- **Exceptions.** If one handler raises, do the remaining ones still run? Decide deliberately.
- **Cascades.** Observer A's handler changes subject B, which notifies C, which changes A again. Event chains become very hard to trace and debug.
- **Synchronous by default.** A slow handler (sending email) blocks the code that emitted the event. Real systems often push slow work onto a queue.

### When not to use it

- When there's exactly one known receiver. A direct call is easier to read, trace and debug.
- When the order of reactions or their success matters to correctness (charge the card, *then* ship). Write that as explicit sequential code, or a workflow.

### In real libraries

- **Django signals**: `post_save.connect(handler, sender=Order)`. Receivers are held by **weak reference** by default (`weak=True`), which avoids lapsed listeners but means a lambda or local function can be garbage-collected and silently stop firing.
- **Qt signals and slots**: `button.clicked.connect(handler)`.
- **The browser DOM**: `addEventListener("click", fn)` and `removeEventListener`.
- **Python's `logging`**: a logger routes eligible records to handlers subject to levels, filters and propagation settings.
- **Reactive libraries** (RxJS, RxPY) generalise observers into streams with operators such as `map`, `filter` and `debounce`.

## Command

### The problem

You want to treat a request ("transfer £50", "insert this text", "resize image 7") as **data**: put it in a queue, run it later or on another machine, log it, retry it, or undo it.

### The structure

```
 Invoker ----> Command
 +history      +execute()
 +run(c)       +undo()
                  ^
                  |
           InsertText --> Receiver
           (args saved)   (Document)
```

The invoker doesn't know what the command does; it just calls `execute()` and keeps history. The receiver does the real work.

### In Python

Undo and redo for a text editor:

```python
class Insert:
    def __init__(self, doc, text):
        self.doc, self.text = doc, text

    def execute(self):
        self.doc.append(self.text)

    def undo(self):
        self.doc.pop()

class Editor:
    def __init__(self):
        self.doc = []
        self.done, self.undone = [], []

    def run(self, cmd):
        cmd.execute()
        self.done.append(cmd)
        self.undone.clear()

    def undo(self):
        cmd = self.done.pop()
        cmd.undo()
        self.undone.append(cmd)

    def redo(self):
        cmd = self.undone.pop()
        cmd.execute()
        self.done.append(cmd)

e = Editor()
e.run(Insert(e.doc, "a"))
e.run(Insert(e.doc, "b"))
e.undo()
e.redo()
e.undo()
print(e.doc)   # ['a']
```

Note `undone.clear()` in `run`. Doing a new action after undoing throws away the redo history, which is the conventional linear undo-stack policy. Some editors preserve branching histories instead.

If you don't need undo, a command is often just a function or `functools.partial(fn, *args)`, which is exactly what you hand to a thread pool.

> [!example] Undo is harder than it looks
> `Insert.undo` above assumes nothing else has changed the document since. Real editors either store enough state to reverse precisely (position and text), or snapshot state with the **memento** pattern.

### When not to use it

- When requests are always run immediately, once, with no logging, queuing or undo. A direct method call is simpler.
- When reversing an action is impossible (an email sent, a payment captured). Then "undo" must be a new compensating command, such as a refund, not a true reversal.

### In real libraries

- **Qt's `QUndoCommand` and `QUndoStack`**: commands with `undo()` and `redo()`.
- **Django migrations**: operations represent schema or data changes. Reversible operations support forwards/backwards execution; some operations or data changes are irreversible, and reversing schema operations need not restore lost data.
- **`concurrent.futures`**: `executor.submit(fn, *args)` packages a call to run on another thread or process.
- **Task queues** such as Celery: `send_email.delay(user_id)` serialises a command and puts it on a broker for a worker.
- **Redux actions** describe changes processed by reducers; Redux's store holds the current state and does not inherently persist an action log. **Event sourcing** instead treats the persisted event history as authoritative. Commands request changes; events record facts, so they are not interchangeable.

## Comparing the three

| Pattern | What becomes an object | Typical Python form |
|---|---|---|
| Strategy | An algorithm | A function argument |
| Observer | A subscription | A list of callbacks |
| Command | A request | Object with `execute` |

## Key takeaways
- Strategy makes an algorithm swappable; in Python that's usually a function argument or a dict of functions.
- Observer decouples a subject from those reacting to it, but brings lapsed-listener leaks, hidden ordering, exception handling and cascades.
- Always give observers a way to unsubscribe, and iterate over a copy when notifying.
- Command turns a request into an object you can queue, log, retry and undo; a conventional linear redo stack is cleared on a new action.
- Some actions can't be undone, only compensated for.
- You'll find these in `sorted(key=...)`, Django signals and migrations, Qt, `concurrent.futures` and task queues.

## Further reading
- [Strategy pattern — Wikipedia](https://en.wikipedia.org/wiki/Strategy_pattern)
- [Observer pattern — Wikipedia](https://en.wikipedia.org/wiki/Observer_pattern)
- [Lapsed listener problem — Wikipedia](https://en.wikipedia.org/wiki/Lapsed_listener_problem)
- [Signals — Django docs](https://docs.djangoproject.com/en/stable/topics/signals/)
- [Command pattern — Wikipedia](https://en.wikipedia.org/wiki/Command_pattern)
- [QUndoCommand — Qt docs](https://doc.qt.io/qt-6/qundocommand.html)
