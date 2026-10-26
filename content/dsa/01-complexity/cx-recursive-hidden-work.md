---
id: cx-recursive-hidden-work
sourceLesson: cx-analysing-code
title: Recursive work and hidden costs
level: intermediate
minutes: 2
summary: Count recursive calls and uncover work hidden inside ordinary Python operations.
---

A short function can perform a large amount of work. Count all recursive calls and the work each call performs outside its children. Here n is the recursive argument or list length, as stated.

## Repeated subproblems multiply work

```python
# fib(5) returns 5.
def fib(n):
    if n < 2:
        return n
    return fib(n - 1) + fib(n - 2)
```

Both children repeat calculations already performed elsewhere. Drawing the calls for `fib(5)` reveals repeated `fib(3)` and `fib(2)` work. The total call count grows exponentially. More precisely it is Θ(φⁿ), where n is the nonnegative argument and φ is the golden ratio, about 1.618. The branches have different depths, so a full binary tree with base two is a loose upper bound, not the tight call count.

Memoisation stores completed answers by argument. Only a linear number of distinct arguments need calculating. This gives a linear number of additions; it does not make arithmetic on increasingly large Python integers constant-time.

## A line of Python is not one operation

For CPython lists, indexing and reading length are constant-cost in the usual model. Membership scans may inspect every item. Front removal shifts remaining references. Slicing creates a new list of references. Appending is constant amortised time, allowing occasional resizing.

```python
# unique([3, 1, 3]) returns [3, 1].
def unique(items):
    seen = []
    out = []
    for x in items:
        if x not in seen:
            seen.append(x)
            out.append(x)
    return out
```

All-distinct input makes each membership scan longer, giving quadratic comparisons. Replacing `seen` with a set and using `add` gives expected linear work for hashable values with constant-cost hashing and equality under a suitable hashing model. Keeping `out` as a list preserves first-occurrence order.

A recursive binary search that slices its chosen half also hides work. Its comparison count is logarithmic, but the copied halves form a linear total in the original list length. Passing index bounds avoids those copies.

## Key takeaways
- Count the whole call tree, including repeated subproblems.
- Include comparison, hashing, copying and shifting costs.
- Changing the representation can remove repeated work while preserving the result.

## Further reading
- [CPython 3.14 list implementation](https://raw.githubusercontent.com/python/cpython/3.14/Objects/listobject.c)
- [Python caching tools](https://docs.python.org/3.14/library/functools.html)
