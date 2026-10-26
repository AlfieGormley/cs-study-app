---
id: cx-auxiliary-memory
sourceLesson: cx-space-complexity
title: Counting auxiliary memory
level: intermediate
minutes: 2
summary: Distinguish extra storage, output memory and lazy value generation.
---

Space complexity measures the largest amount of memory needed at once. It does not count every object ever created if earlier objects have already been released.

## Say what the count includes

**Total space** includes the stored input. **Auxiliary space** measures additional storage. State whether output is included: a function producing a new list has to store that result even if its working variables are few. Streaming input need not remain resident, so reading many items alone does not imply storing them all.

Here n is input length or table side length. The following counts treat each value and reference as one memory word and include returned collections:

```python
def total(xs):
    s = 0
    for x in xs:
        s += x
    return s

def reversed_copy(xs):
    return xs[::-1]

def table(n):
    return [[0] * n for _ in range(n)]
```

The sum retains a constant number of values. The reverse creates n reference slots. The square table retains n rows each containing n slots, giving quadratic space. A triangle of increasingly long rows still contains a quadratic number of slots, even when every slot refers to the same zero object.

## Produce values when needed

```python
# Both produce 30 when n is 5.
sum([x * x for x in range(n)])
sum(x * x for x in range(n))
```

The first expression builds all squares before summing. The second is a generator expression: `sum` requests one square at a time. Under the atomic-value model, this removes the linear intermediate collection and uses constant auxiliary storage. It still computes every square.

Python integers can grow in bit length. A constant number of integer objects therefore does not necessarily mean constant bytes. Also, a generator can retain a large source or other state; its memory saving depends on the particular producer and consumer.

## Key takeaways
- Measure peak live storage and state input/output conventions.
- Shared values still require slots in a collection.
- Streaming avoids storing all intermediate values when the consumer can process them one at a time.

## Further reading
- [Python sequence types and integers](https://docs.python.org/3.14/library/stdtypes.html)
