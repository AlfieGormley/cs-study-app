---
id: cx-space-complexity
title: Space complexity
level: intermediate
minutes: 11
summary: Measuring memory as well as time, auxiliary versus total space, the hidden cost of the recursion stack, in-place algorithms and time-space trade-offs.
---

Time is not the only resource an algorithm consumes. **Space complexity** measures how much memory an algorithm needs as a function of the input size n. It uses exactly the same notation (O, Ω, Θ) and the same habits (drop constants, keep the dominant term).

Memory often matters more than people expect. A job allocating a dense n-by-n table needs 10 billion cells at n = 100,000; its memory budget may be exhausted before runtime becomes the main concern. Phones, serverless functions and containers usually have hard memory limits, and exceeding them kills the process outright.

## What counts

There are two common conventions, and you should say which you mean:

- **Total space**: everything, including the input itself.
- **Auxiliary space**: only the *extra* memory the algorithm uses beyond its input.

Auxiliary space is usually the more useful figure, because every algorithm that reads an n-item list has Ω(n) total space just from the input. When people say "merge sort uses O(n) space" or "this is O(1) space", they mean auxiliary.

**Output** is sometimes counted separately too. A function that returns all n squares of its input needs O(n) memory for the result, but it couldn't do better, so some authors exclude it.

Like time analysis, space analysis assumes each number, pointer or character takes one "word" of memory: O(1). That breaks down for unbounded integers (a number N takes about `log2 N` bits), but it is the normal assumption.

## Examples

```python
def total(xs):          # O(1) aux
    s = 0
    for x in xs:
        s += x
    return s

def reversed_copy(xs):  # O(n) aux
    return xs[::-1]

def table(n):           # O(n^2) aux
    return [[0] * n for _ in range(n)]
```

`total` only ever holds one running sum, however long the list. `reversed_copy` builds a new list of n items. `table` builds n rows of n entries.

In a model that reads or writes only O(1) cells per step, an O(T)-time computation can touch only O(T) **auxiliary cells**. This excludes the pre-existing input and does not bound untouched virtual memory reserved by an allocator. Low space does not imply low time: an n-bit counter can enumerate 2ⁿ values while reusing O(n) bits.

## The recursion stack

This is where most space mistakes happen. Every call that hasn't returned yet holds a **stack frame** with its local variables, arguments and return address. Recursive code uses space proportional to the **maximum depth** of the recursion, even if it never creates a list.

```python
def fact(n):
    if n <= 1:
        return 1
    return n * fact(n - 1)
```

When `fact(5)` reaches its base case, five frames are alive at once:

```
fact(1)   <- top: about to return 1
fact(2)   waiting to multiply by 2
fact(3)   waiting to multiply by 3
fact(4)   waiting to multiply by 4
fact(5)   waiting to multiply by 5
```

Counting frames and treating arithmetic values as atomic, `fact` uses Θ(n) auxiliary space; an iterative version keeps a constant number of values. Actual Python integers are not fixed-size: n! alone needs Θ(n log n) bits.

Note that it's **depth**, not the total number of calls, that matters. Naive `fib(n)` makes about 1.618^n calls, but at any moment only one path from the root to a leaf is active, so its stack is only Θ(n) deep. Time Θ(φ^n), space Θ(n).

| Function | Calls | Max depth (space) |
|---|---|---|
| fact(n) | n | n |
| naive fib(n) | ~1.618^n | n |
| binary search | log n | log n |
| merge sort | ~2n | log n |

(Merge sort's stack is only log n deep, but its merge step needs an O(n) buffer, so its total auxiliary space is O(n).)

> [!warning] Python stops at 1,000
> CPython's default recursion limit is 1,000 frames (`sys.getrecursionlimit()`). `fact(5000)` raises `RecursionError`. You can raise the limit with `sys.setrecursionlimit`, but very deep recursion stays fragile: every frame costs memory, and recursion that passes through C code can still overflow the real thread stack and crash the interpreter. Python doesn't do **tail-call optimisation**, so even tail-recursive functions use one frame per call. For deep linear recursion, rewrite it as a loop.

Other languages vary. Scheme guarantees proper tail calls. Some C and C++ compilers eliminate tail calls when optimising, but the language standards don't require it. Stack limits depend on the operating system, thread configuration and build, so measure the actual limits and frame costs before relying on a recursion depth.

## In-place algorithms

An algorithm is **in-place** if it transforms its input using only O(1) auxiliary space (some definitions allow O(log n), to cover a recursion stack). Reversing a list with two pointers is the classic example:

```python
def reverse_in_place(xs):
    i, j = 0, len(xs) - 1
    while i < j:
        xs[i], xs[j] = xs[j], xs[i]
        i += 1
        j -= 1
```

Compare `xs[::-1]`, which is simpler but allocates a whole new list.

In-place algorithms save memory and often run faster (less allocation, better cache use). The costs:

- **They destroy the input.** If the caller still needs the original, it has to copy it first, and the saving vanishes.
- **They can be harder to get right.** Swapping elements around inside one array is fiddlier than building a new one.
- **They don't play well with sharing.** Mutating a list that other code (or another thread) holds a reference to causes surprising bugs.

Sorting is the familiar case. Heapsort sorts in place with O(1) auxiliary space. Quicksort partitions in place, but its recursion needs a stack: O(log n) expected depth, O(n) in the worst case. A standard trick bounds it at O(log n) even in the worst case: **recurse into the smaller partition and loop on the larger one**, because the smaller side is at most half the size. Python's `list.sort()` mutates its input, but is not in-place in the strict O(1)-auxiliary-space sense; it may allocate a temporary buffer of up to n/2 items while merging.

## Time-space trade-offs

Many speed-ups work by spending memory:

- **Hashing for lookups.** Checking for duplicates with a set takes expected O(n) time and O(n) space. Sorting in place, then scanning neighbours, takes O(n log n) time with little extra space.
- **Memoisation.** Caching `fib` results turns Θ(φ^n) time into Θ(n) time, at the cost of Θ(n) space for the cache. A loop keeping just the last two values gets Θ(n) time *and* O(1) space.
- **Precomputation.** A prefix-sum array (n extra numbers) answers "sum of `xs[a:b]`" in O(1) instead of O(b - a).
- **Lookup tables.** Counting set bits in a byte with a 256-entry table instead of looping over bits.

The reverse also happens: when memory is tight, you can recompute values instead of storing them, or process data as a **stream**.

```python
# builds a list of n squares: O(n) space
sum([x * x for x in range(n)])

# generator: one value at a time, O(1)
sum(x * x for x in range(n))
```

## Constants matter for memory

Asymptotic notation hides constant factors, but with memory, those constants decide whether something fits. For a typical 64-bit CPython build (check `sys.getsizeof` on the actual build):

- A small `int` object is 28 bytes (`sys.getsizeof(1)`).
- A list stores an 8-byte pointer per element, plus the objects themselves.

So a list of 10 million distinct small integers costs roughly 80 MB of pointers plus about 280 MB of int objects: around 360 MB. A NumPy `int64` array or the standard `array` module stores the same numbers as raw 8-byte values: about 80 MB. Both are "O(n)", but the packed data fits below a 256 MB budget, while the list does not. Runtime overhead and temporary conversion buffers still need headroom.

> [!example] An interview-style check
> "Find whether any two numbers in this list sum to a target." Hash set: expected O(n) time, O(n) space. Sort then two pointers: O(n log n) time, O(1) extra if you may sort in place. Neither is "better"; it depends on whether memory or time is the constraint, and whether you may modify the input.

## Key takeaways
- Space complexity uses the same notation as time. Usually quote auxiliary (extra) space and say so.
- Recursion uses stack space proportional to maximum depth, not total calls: naive fib is exponential time but linear space.
- Python's default recursion limit is 1,000 and it has no tail-call optimisation; convert deep recursion into loops.
- In-place algorithms use O(1) extra space but overwrite their input.
- Many speed-ups trade memory for time: hash sets, memoisation, prefix sums, lookup tables.
- Constant factors decide whether data fits: a Python list of ints uses several times more memory than a packed array.

## Further reading
- [Space complexity — Wikipedia](https://en.wikipedia.org/wiki/Space_complexity)
- [In-place algorithm — Wikipedia](https://en.wikipedia.org/wiki/In-place_algorithm)
- [Call stack — Wikipedia](https://en.wikipedia.org/wiki/Call_stack)
- [sys.setrecursionlimit — Python docs](https://docs.python.org/3/library/sys.html)
- [Tail call — Wikipedia](https://en.wikipedia.org/wiki/Tail_call)
