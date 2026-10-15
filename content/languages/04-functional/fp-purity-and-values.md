---
id: fp-purity-and-values
title: Pure functions and value semantics
level: basic
minutes: 3
sourceLesson: fp-pure-functions
summary: Purity needs stable explicit inputs and no observable external effects.
---

Functional programming rests on one idea: build programs out of functions that behave like the functions in maths. Give `square` the number 3 and you get 9. For the stated numeric domain and arithmetic semantics, repeated calls give the same value. Floating-point settings, effectful overloaded operators and external mutation must still be excluded.

Many functions in everyday code are not like that. They read a global, write to a database, print a log line or change the list you passed in. Functional programming does not ban those things (programs that do nothing observable are useless). It pushes them to the edges, so that the bulk of the code is made of pieces you can reason about on their own.

## What makes a function pure

A function is pure (a **pure function**) when both of these hold:

1. Same inputs, same output. The result depends only on the arguments. No dependence on clocks, random state, files or mutable globals that can change between calls; reading a fixed immutable constant is compatible with purity.
2. **No side effects.** Calling it changes nothing observable outside it: no mutation of arguments or globals, no I/O, no exceptions used as hidden control flow to the outside world.

```python
# Only total reads explicit numeric inputs.
# Pure
def total(prices):
    return sum(prices)

# Impure: reads a global that can change
TAX = 0.2
def with_tax(price):
    return price * (1 + TAX)

# Impure: mutates its argument
def add_item(cart, item):
    cart.append(item)
    return cart

# Impure: depends on the clock
import time
def greeting():
    h = time.localtime().tm_hour
    return "Morning" if h < 12 else "Hi"
```

These Python examples assume ordinary built-in numeric values and finite containers, without effectful custom operators or concurrent mutation. Purity here concerns returned values rather than allocation identity; returning mutable objects needs care if callers share or mutate them.

Local mutation inside a function is fine. A function that builds a list with a loop and returns it is still pure, as long as nothing outside can see the mutation happen.

```python
# Only this call sees the construction list.
def squares(n):
    out = []          # local, invisible
    for i in range(n):
        out.append(i * i)
    return out        # still pure
```

## Key takeaways
- Purity needs stable explicit inputs and no observable external effects.
- Local mutation can implement a pure value-producing operation.

## Further reading
- [Python Fp](https://docs.python.org/3/howto/functional.html)
- [Python Model](https://docs.python.org/3/reference/datamodel.html)
