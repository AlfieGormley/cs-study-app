---
id: sep-simple-design-cost
title: Simple code and the cost of hidden copying
level: intermediate
minutes: 4
summary: Simple means fewer intertwined concepts, rather than fewer lines.
sourceLesson: sep-dry-kiss-yagni
---

What makes code simple? Not shortness, as this lesson shows with a one-liner that is both harder to read and dramatically slower than the plain loop it replaces.

## KISS: simple is not the same as easy

Lockheed Martin associates "Keep it simple, stupid" with Kelly Johnson and the Skunk Works engineering approach.

In software, simplicity means **fewer concepts and fewer interactions** for a reader to hold in their head. It is not the same as "fewest lines" or "least typing".

```python
# List addition repeatedly copies prefixes.
# Clever
def flatten(xs):
    return sum(map(lambda x: flatten(x)
               if isinstance(x, list)
               else [x], xs), [])
```

```python
# Append leaves; extend flattened sublists.
# Simple
def flatten(xs):
    out = []
    for x in xs:
        if isinstance(x, list):
            out.extend(flatten(x))
        else:
            out.append(x)
    return out
```

The clever version is shorter, but a reader must untangle `sum` over lists, a lambda and a conditional expression. It is also slow. `sum(..., [])` adds lists with `+`, and list `+` builds a brand-new list each time, copying everything accumulated so far. Each step therefore copies one more element than the step before.

That adds up quickly: the total copying grows with the *square* of the list's length, so doubling the list roughly quadruples the work. Counting each element reference that `+` copies (a model of the work, not a timing), a flat list of 1,000 elements needs about half a million copies and 100,000 elements need about 5 billion. The simple version appends each element once, so its work grows only in proportion to the length. Its recursive `extend` avoids that flat-list penalty, although deep nesting still adds repeated copying and recursion overhead. Both examples assume finite, acyclic nested lists; a list containing itself does not terminate normally, and sufficiently deep nesting can exceed Python’s recursion limit.

Rich Hickey's talk *Simple Made Easy* draws a useful line:

- **Easy** means familiar or close at hand ("I already know this framework").
- **Simple** means not intertwined: few parts, each doing one thing.

A heavyweight framework can be easy to start with and far from simple. A plain function and a dictionary can be unfamiliar to someone used to the framework, yet simple.

### Kent Beck's rules of simple design

In Fowler's presentation of Beck's rules, a simple design:

1. Passes the tests.
2. Reveals intention.
3. Has no duplication (of knowledge).
4. Has the fewest elements.

Correctness comes first and minimising elements comes last. Formulations differ on the middle two: Fowler notes that clarity and removing duplication usually reinforce one another; they are not a universally agreed tie-breaking order.

## Key takeaways
- Simple means fewer intertwined concepts, rather than fewer lines.
- Repeated list concatenation copies a growing prefix each time, so its work grows with the square of the length.
- Correctness and clear intent precede minimising the number of elements.

## Further reading
- [Kelly Johnson — Lockheed Martin](https://www.lockheedmartin.com/en-us/news/features/history/johnson.html)
- [Rich Hickey: Simple Made Easy (InfoQ)](https://www.infoq.com/presentations/Simple-Made-Easy/)
- [Martin Fowler: Beck Design Rules](https://martinfowler.com/bliki/BeckDesignRules.html)
