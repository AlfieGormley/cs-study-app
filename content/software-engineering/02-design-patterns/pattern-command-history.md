---
id: pattern-command-history
title: Commands, undo and compensation
level: intermediate
minutes: 3
sourceLesson: pattern-behavioural-1
summary: A command packages a request so it can be stored, queued or tracked.
---

## Command pattern

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

> [!analogy] Real-world analogy: a restaurant order slip
> A waiter writes your order on an order slip and clips it to the kitchen rail. The slip can wait in a queue, be read by whichever cook is free, be kept for the bill, or be torn up if you cancel before cooking starts. The waiter never needs to know how to cook.
>
> **How it maps:** The slip is the command object holding the request and its details, the waiter is the invoker, the cook is the receiver that does the work, and the rail of slips is the queue or history.
>
> **Where it stops:** Once a meal has been served and eaten, tearing up the slip undoes nothing; the restaurant can only offer a refund. Software undo is the same: an in-memory edit can be reversed, but an external effect such as a captured payment needs a new compensating command.

### In Python

Undo and redo for a text editor:

```python
class Insert:
    def __init__(self, doc, text):
        self.doc, self.text = doc, text

    def execute(self):
        self.doc.append(self.text)

    def undo(self):
        # Valid for this append-only
        # example.
        self.doc.pop()

class Editor:
    def __init__(self):
        self.doc = []
        self.done, self.undone = [], []

    def run(self, cmd):
        cmd.execute()
        self.done.append(cmd)
        # A new edit discards the redo
        # branch.
        self.undone.clear()

    def undo(self):
        cmd = self.done.pop()
        cmd.undo()
        self.undone.append(cmd)

    def redo(self):
        # Toy code: empty redo raises.
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
> `Insert.undo` above assumes nothing else has changed the document since. Real editors either store enough state to reverse precisely (position and text), or snapshot state with the **Memento pattern**.

### When not to use it

- When requests are always run immediately, once, with no logging, queuing or undo. A direct method call is simpler.
- When reversing an action is impossible (an email sent, a payment captured). Then "undo" must be a new compensating command, such as a refund, not a true reversal.

### In real libraries

- **Qt's `QUndoCommand` and `QUndoStack`**: commands with `undo()` and `redo()`.
- **Django migrations**: operations represent schema or data changes. Reversible operations support forwards/backwards execution; some operations or data changes are irreversible, and reversing schema operations need not restore lost data.
- **`concurrent.futures`**: `executor.submit(fn, *args)` packages a call to run on another thread or process.
- **Task queues** such as Celery: `send_email.delay(user_id)` serialises a command and puts it on a message broker for a worker.
- **Redux actions** describe changes processed by reducers; Redux's store holds the current state and does not inherently persist an action log. **Event sourcing** instead treats the persisted event history as authoritative. Commands request changes; events record facts, so they are not interchangeable.

## Comparing the three

| Pattern | What becomes an object | Typical Python form |
|---|---|---|
| Strategy | An algorithm | A function argument |
| Observer | A subscription | A list of callbacks |
| Command | A request | Object with `execute` |

## Key takeaways
- A command packages a request so it can be stored, queued or tracked.
- Linear undo history clears the redo branch when a new command runs.
- Irreversible side effects require compensating operations with their own failure handling.
- Commands request change; persisted events record facts.

## Further reading
- [QUndoCommand — Qt documentation](https://doc.qt.io/qt-6/qundocommand.html)
- [Migration operations — Django documentation](https://docs.djangoproject.com/en/stable/ref/migration-operations/)
- [Strategy pattern — Wikipedia](https://en.wikipedia.org/wiki/Strategy_pattern)
- [Observer pattern — Wikipedia](https://en.wikipedia.org/wiki/Observer_pattern)
- [Lapsed listener problem — Wikipedia](https://en.wikipedia.org/wiki/Lapsed_listener_problem)
- [Signals — Django docs](https://docs.djangoproject.com/en/stable/topics/signals/)
- [Command pattern — Wikipedia](https://en.wikipedia.org/wiki/Command_pattern)
- [QUndoCommand — Qt docs](https://doc.qt.io/qt-6/qundocommand.html)
