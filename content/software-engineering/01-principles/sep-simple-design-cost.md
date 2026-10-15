---
id: sep-simple-design-cost
title: Simple code and the cost of hidden copying
level: intermediate
minutes: 4
summary: Simple means fewer intertwined concepts, rather than fewer lines.
sourceLesson: sep-dry-kiss-yagni
---

DRY protects shared knowledge; KISS asks for simplicity; YAGNI challenges speculative features. Here the useful test is the cost of understanding and changing the design.

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

The clever version is shorter, but a reader must untangle `sum` over lists, a lambda and a conditional expression. It is also slow. `sum(..., [])` adds lists with `+`, and list `+` builds a brand-new list each time, copying both operands. On a flat list, step 1 copies 1 element reference, step 2 copies 2, and so on:

```formula
T(n) = 1 + 2 + … + n
T(n) = n(n + 1) / 2
T(n) = Θ(n^2)
where
T(n): the total number of element references copied while flattening, as a function of n
n: the number of elements in the input list
…: and so on: keep adding each whole number up to n
Θ: Big-Theta: "grows in proportion to", ignoring constant factors and small inputs
n^2: n multiplied by itself
In words: the k-th step copies k references, so the total is the sum of 1 to n, which grows with the square of the list's length.
```

For a list of 1,000 elements that is 1,000 × 1,001 / 2 = 500,500 copies; for 100,000 elements it is about 5 billion. Doubling the list roughly quadruples the work. The simple version appends each element once, so its work grows only in proportion to n. Its recursive `extend` avoids that flat-list penalty, although deep nesting still adds repeated copying and recursion overhead. Both examples assume finite, acyclic nested lists; a list containing itself does not terminate normally, and sufficiently deep nesting can exceed Python’s recursion limit.

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
- Repeated list concatenation copies growing prefixes and is quadratic on the flat input considered here.
- Correctness and clear intent precede minimising the number of elements.

## Further reading
- [Kelly Johnson — Lockheed Martin](https://www.lockheedmartin.com/en-us/news/features/history/johnson.html)
- [www.infoq.com](https://www.infoq.com/presentations/Simple-Made-Easy/)
- [BeckDesignRules](https://martinfowler.com/bliki/BeckDesignRules.html)
