---
id: pattern-interface-adapters
title: Adapting incompatible interfaces
level: intermediate
minutes: 3
sourceLesson: pattern-structural
summary: An adapter presents the interface callers need and delegates to the existing API.
---

Structural patterns are about **fitting objects together**: making mismatched interfaces line up, adding behaviour without subclassing, hiding complexity, and treating groups of things like single things.

Four of them (adapter, decorator, proxy, facade) look almost identical in code: one object holds another and forwards calls to it. What separates them is **intent**, and the quickest way to tell them apart is to ask what happens to the interface.

| Pattern | Interface it presents | Why |
|---|---|---|
| Adapter | A *different* one | Make it fit |
| Decorator | The *same* one | Add behaviour |
| Proxy | The *same* one | Control access |
| Facade | A *simpler* one | Hide a subsystem |

## Adapter pattern

### The problem

You have code that expects interface A and a class that provides interface B. You can't (or shouldn't) change either. A typical case: wrapping a third-party SDK so the rest of your code depends on your own interface.

### The structure

```
 Client ---> Target interface
                  ^
                  |
              Adapter ------> Adaptee
              send(m)          post(body)
              calls post()
```

### In Python

```python
class LegacySms:
    def transmit(self, number, body):
        return f"sent {body!r} to {number}"

class SmsAdapter:
    """Presents send(to, msg)."""
    def __init__(self, legacy):
        self.legacy = legacy

    def send(self, to, msg):
        # Translate argument names, keeping
        # their destination/message meaning.
        return self.legacy.transmit(
            number=to, body=msg)

def notify(channel):
    to = "+447700900000"
    return channel.send(to, "hi")

print(notify(SmsAdapter(LegacySms())))
# sent 'hi' to +447700900000
```

### When not to use it

- When you own both sides. Just change one of them.
- When the mismatch is semantic, not just a matter of names. If one API is synchronous and the other is callback-based, or one has transactions and the other doesn't, a thin adapter will leak.

### In real libraries

- **`io.TextIOWrapper`** adapts a binary stream (bytes) to a text stream (str), handling encoding and newlines. `open("f.txt")` returns one wrapped around a buffered binary file.
- **requests** has `HTTPAdapter`, which adapts requests' session API to urllib3's connection pools. You can `mount()` your own adapter for a URL prefix.
- **SLF4J** (Java) ships adapters (it calls them bindings or providers) that route its API to Logback, Log4j and others.

## Key takeaways
- An adapter presents the interface callers need and delegates to the existing API.
- Renaming methods cannot repair incompatible semantics.
- TextIOWrapper adapts a binary stream into a text-stream contract.

## Further reading
- [io — Python documentation](https://docs.python.org/3/library/io.html)
- [Advanced usage — Requests documentation](https://requests.readthedocs.io/en/latest/user/advanced/)
