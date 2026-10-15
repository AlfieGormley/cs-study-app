---
id: pattern-state-and-transitions
title: State objects and transition tables
level: advanced
minutes: 3
sourceLesson: pattern-behavioural-2
summary: State objects group behaviour that differs with the current state.
---

The next four short lessons deal with **control flow that varies**: by the object's current state, by subclass, by how a collection is traversed, or by the type of each node in a structure.

They also show a recurring theme of this module. Each started as a class-based design in C++ or Smalltalk, and modern Python offers lighter alternatives: enums and transition tables, hooks, generators, and `match` or `singledispatch`. Knowing the pattern helps you choose between them.

## State pattern

### The problem

An object's behaviour depends on its state, and the rules differ a lot between states. A document can be *draft*, *in review* or *published*: "edit" works in draft, is refused in review and creates a new revision when published.

Written naively, every method becomes a large `if self.status == ...` chain, and adding a state means editing every one of them.

### The structure

```
 Context ------------> State
 -state               +publish(ctx)
 +publish():          +edit(ctx)
   state.publish(self)   ^      ^
                         |      |
                      Draft  Review ...
 each state sets ctx.state to the next
```

Each state is an object that implements the behaviour for that state, and switches the context to the next state.

### In Python

```python
class Draft:
    def publish(self, doc):
        # Submit first; approval is
        # separate.
        doc.state = Review()
        return "sent for review"

class Review:
    def publish(self, doc):
        # Keep the state until approved.
        if not doc.approved:
            return "needs approval"
        doc.state = Published()
        return "published"

class Published:
    def publish(self, doc):
        return "already published"

class Document:
    def __init__(self):
        self.state = Draft()
        self.approved = False

    def publish(self):
        return self.state.publish(self)

d = Document()
print(d.publish())   # sent for review
print(d.publish())   # needs approval
d.approved = True
print(d.publish())   # published
print(d.publish())   # already published
```

### The table-driven alternative

When states differ mainly in **which transitions are allowed**, rather than in rich behaviour, a transition table is clearer than a class per state:

```python
from enum import Enum

class S(Enum):
    DRAFT = 1
    REVIEW = 2
    PUBLISHED = 3

ALLOWED = {
    (S.DRAFT, "submit"): S.REVIEW,
    (S.REVIEW, "reject"): S.DRAFT,
    (S.REVIEW, "approve"): S.PUBLISHED,
}

def step(state, event):
    # Encode the transition as a pair.
    key = (state, event)
    if key not in ALLOWED:
        msg = f"{event} in {state}"
        raise ValueError(msg)
    return ALLOWED[key]
```

The whole state machine is visible in one place, can be drawn as a diagram, and can be tested by checking every pair.

### When not to use it

- Two or three states with trivial differences. An `if` is fine.
- When transitions, not behaviour, are the interesting part. Use a table.
- When state must be stored in a database. You'll be persisting an enum value anyway, so a class per state means converting back and forth.

### In real libraries

- The GoF's own example was a **TCP connection** whose `open`, `close` and `acknowledge` behave differently in Established, Listen and Closed states.
- **`transitions`** (Python) and **Spring Statemachine** (Java) are libraries for declaring state machines.
- Many real implementations are table- or enum-driven instead: the **h11** HTTP/1.1 library tracks the state of each side (IDLE, SEND_BODY, DONE and so on) with explicit transition rules, and `asyncio.Future` moves between PENDING, CANCELLED and FINISHED.

## Key takeaways
- State objects group behaviour that differs with the current state.
- A transition table is often clearer when allowed transitions are the main variation.
- Persisted state and valid event sequences still need explicit representation.

## Further reading
- [Design Patterns — publisher catalogue](https://www.informit.com/store/design-patterns-elements-of-reusable-object-oriented-software-9780201633610)
