---
id: cx-space-complexity
title: Space complexity
level: intermediate
minutes: 11
summary: Measuring memory as well as time, auxiliary versus total space, the hidden cost of the recursion stack, in-place algorithms and time-space trade-offs.
---

Time is not the only resource an algorithm consumes. **Space complexity** measures how much memory an algorithm needs as a function of the input size n. It uses exactly the same notation (O for an upper bound, Ω for a lower bound, Θ for a tight bound) and the same habits (drop constants, keep the dominant term).

Memory often matters more than people expect. A job allocating a dense n-by-n table (n rows of n cells) needs a lot of cells very quickly:

```formula
S(n) = n × n = n^2
S(100000) = 10^5 × 10^5 = 10^10
10^10 × 8 B = 8 × 10^10 B = 80 GB
where
S(n): the number of cells in the table
n: the number of rows (and of columns), here 100,000 = 10^5
n^2: n squared, n × n
B: bytes; each cell here is assumed to be one 8-byte number
GB: gigabytes; 1 GB = 10^9 bytes
In words: a square table of side 100,000 has ten billion cells, which at 8 bytes each is about 80 gigabytes.
```

Its memory budget may be exhausted before runtime becomes the main concern. Phones, serverless functions and containers usually have hard memory limits, and exceeding them kills the process outright.

## What counts

There are two common conventions, and you should say which you mean:

- **Total space**: everything, including the input itself.
- **Auxiliary space**: only the *extra* memory the algorithm uses beyond its input.

Auxiliary space is usually the more useful figure, because every algorithm that reads an n-item list has Ω(n) total space just from the input. When people say "merge sort uses O(n) space" or "this is O(1) space", they mean auxiliary.

**Output** is sometimes counted separately too. A function that returns all n squares of its input needs O(n) memory for the result, but it couldn't do better, so some authors exclude it.

Like time analysis, space analysis assumes each number, pointer or character takes one "word" of memory: O(1). That breaks down for unbounded integers, whose size grows with their value:

```formula
b = ⌊log_2(N)⌋ + 1
N = 1000000:  b = ⌊19.93⌋ + 1 = 20
where
b: the number of bits needed to store the whole number N
N: a positive whole number being stored
log_2(N): the base-2 logarithm of N, the power you raise 2 to in order to get N
⌊x⌋: floor: round x down to a whole number
In words: the bits a number needs grow with the logarithm of its value, so a million needs 20 bits and a number with a thousand digits needs over 3,000.
```

Treating each number as one word is still the normal assumption.

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

This is where most space mistakes happen. Every call that hasn't returned yet holds a **stack frame** with its local variables, arguments and return address. Recursive code uses space proportional to the **maximum depth of the recursion**, even if it never creates a list.

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

Counting frames and treating arithmetic values as atomic, `fact` uses Θ(n) auxiliary space (n frames for `fact(n)`); an iterative version keeps a constant number of values. Actual Python integers are not fixed-size: n! (n factorial) alone needs Θ(n log n) bits, because the number of bits is the logarithm of the value and log(n!) grows like n log n.

Note that it's **depth**, not the total number of calls, that matters. Naive `fib(n)` makes an exponential number of calls, but at any moment only one path from the root to a leaf is active:

```formula
time(n) = Θ(φ^n) ≈ Θ(1.618^n)
space(n) = Θ(n)
where
time(n): the number of calls naive fib(n) makes, which sets its running time
space(n): the maximum number of stack frames alive at once, which sets its memory use
n: the argument passed to fib, which is also the depth of the deepest path in the recursion tree
φ: phi, the golden ratio, about 1.618
φ^n: φ multiplied by itself n times
Θ: Big-Theta: grows at exactly this rate, up to a constant factor
≈: approximately equal to
In words: naive Fibonacci takes exponential time but only linear space, because each finished branch hands its stack frames back before the next branch starts.
```

In the table below, n is the input (the argument, or the list length) and log n is the base-2 logarithm of n:

| Function | Calls | Max depth (space) |
|---|---|---|
| fact(n) | n | n |
| naive fib(n) | ~1.618^n | n |
| binary search | log n | log n |
| merge sort | ~2n | log n |

(Merge sort's stack is only log n deep, because each call halves the list, but its merge step needs an O(n) buffer, so its total auxiliary space is O(n).)

> [!warning] Python stops at 1,000
> CPython's default recursion limit is 1,000 frames (`sys.getrecursionlimit()`). `fact(5000)` raises `RecursionError`. You can raise the limit with `sys.setrecursionlimit`, but very deep recursion stays fragile: every frame costs memory, and recursion that passes through C code can still overflow the real thread stack and crash the interpreter. Python doesn't do **tail-call optimisation**, so even tail-recursive functions use one frame per call. For deep linear recursion, rewrite it as a loop.

Other languages vary. Scheme guarantees proper tail calls. Some C and C++ compilers eliminate tail calls when optimising, but the language standards don't require it. Stack limits depend on the operating system, thread configuration and build, so measure the actual limits and frame costs before relying on a recursion depth.

## In-place algorithms

An algorithm is **in-place** if it transforms its input using only O(1) auxiliary space, a constant amount however big the input of n items is (some definitions allow O(log n), to cover a recursion stack). Reversing a list with two pointers is the classic example:

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

Sorting is the familiar case. Heapsort sorts in place with O(1) auxiliary space. Quicksort partitions in place, but its recursion needs a stack: O(log n) expected depth, O(n) in the worst case. A standard trick bounds it at O(log n) even in the worst case: **recurse into the smaller partition and loop on the larger one**, because the smaller side is at most half the size. Python's `list.sort()` mutates its input, but is not in-place in the strict O(1)-auxiliary-space sense; it may allocate a temporary buffer of up to half the list (n/2 items for a list of n) while merging.

Why does recursing into the smaller side bound the depth? Each recursive call at least halves the size of the part it works on:

```formula
s_{k+1} ≤ s_k / 2
s_k ≤ n / 2^k
depth ≤ log_2(n)
where
s_k: the size of the partition handled at recursion depth k
s_{k+1}: the size handled one level deeper
k: the recursion depth (0 for the first call)
n: the number of items being sorted
2^k: 2 multiplied by itself k times
depth: the maximum number of quicksort frames on the stack at once
log_2(n): the base-2 logarithm of n, the number of halvings that take n down to 1
≤: less than or equal to
In words: the smaller partition is at most half the current size, so you can only go about log_2(n) levels deep before reaching a single item.
```

For a million items that is at most about 20 frames instead of up to a million.

## Time-space trade-offs

Many speed-ups work by spending memory:

- **Hashing for lookups.** Checking for duplicates with a set takes expected O(n) time and O(n) space. Sorting in place, then scanning neighbours, takes O(n log n) time with little extra space.
- **Memoisation.** Caching `fib` results turns Θ(φ^n) time into Θ(n) time, at the cost of Θ(n) space for the cache. A loop keeping just the last two values gets Θ(n) time *and* O(1) space.
- **Precomputation.** A prefix-sum array (n extra numbers) answers "sum of `xs[a:b]`" in O(1) instead of O(b − a), the length of the range (formula below).
- **Lookup tables.** Counting set bits in a byte with a 256-entry table instead of looping over bits.

The prefix-sum trick stores running totals once, then answers any range sum with one subtraction:

```formula
P[0] = 0
P[i + 1] = P[i] + xs[i]
sum(xs[a:b]) = P[b] − P[a]
where
P: the prefix-sum array, n + 1 numbers; P[i] is the total of the first i items
xs: the original list of n numbers; xs[i] is the item at position i (counting from 0)
xs[a:b]: the items from position a up to but not including position b
sum: the total of the items in the range
i: a position in the list, from 0 to n − 1
a, b: the start and end positions of the range asked about
n: the number of items in xs
In words: the total of a range is "everything up to b" minus "everything up to a", so each query is one subtraction, at the cost of storing n + 1 extra numbers.
```

For xs = [3, 1, 4, 1, 5], P = [0, 3, 4, 8, 9, 14], and the sum of xs[1:4] is P[4] − P[1] = 9 − 3 = 6 (that is 1 + 4 + 1).

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

So a list of 10 million distinct small integers costs:

```formula
M_list = N × (8 B + 28 B)
M_list = 10^7 × 36 B = 3.6 × 10^8 B ≈ 360 MB
M_array = N × 8 B = 8 × 10^7 B ≈ 80 MB
where
M_list: the memory used by the Python list and its int objects, in bytes (B)
M_array: the memory used by a packed array of 8-byte integers, in bytes (B)
N: the number of integers stored, here 10 million = 10^7
B: bytes; one byte is 8 bits
MB: megabytes; 1 MB = 10^6 bytes
≈: approximately equal to
In words: each list element costs an 8-byte pointer plus a 28-byte int object, four and a half times the 8 bytes a packed array needs.
```

That is roughly 80 MB of pointers plus about 280 MB of int objects. A NumPy `int64` array or the standard `array` module stores the same numbers as raw 8-byte values: about 80 MB. Both are "O(n)", but the packed data fits below a 256 MB budget, while the list does not. Runtime overhead and temporary conversion buffers still need headroom.

> [!example] An interview-style check
> "Find whether any two numbers in this list of n numbers sum to a target." Hash set: expected O(n) time, O(n) space. Sort then two pointers: O(n log n) time, O(1) extra if you may sort in place. Neither is "better"; it depends on whether memory or time is the constraint, and whether you may modify the input.

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
