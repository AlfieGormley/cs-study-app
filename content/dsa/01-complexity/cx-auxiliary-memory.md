---
id: cx-auxiliary-memory
sourceLesson: cx-space-complexity
title: Counting auxiliary memory
level: intermediate
minutes: 5
summary: Distinguish extra storage, output memory and lazy value generation.
---

Space counts memory rather than elapsed work. The examples below use the usual one-word model unless they explicitly discuss integer bit lengths.

Time is not the only resource an algorithm consumes. **Space complexity** measures how much memory an algorithm needs as a function of the input size n. It uses exactly the same notation (O for an upper bound, Ω for a lower bound, Θ for a tight bound) and the same habits (drop constants, keep the dominant term).

Memory often matters more than people expect. A job allocating a dense n-by-n table (n rows of n cells) needs a lot of cells very quickly:

```formula
S(n) = n × n = n^2
S(100000) = 10^5 × 10^5 = 10^10
10^10 × 8 B = 8 × 10^10 B = 80 GB
where
S(n): the number of cells in the table
n: the number of rows (and of columns), here 100,000 = 10^5
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
    # A new list; xs keeps its order.
    return xs[::-1]

def table(n):           # O(n^2) aux
    # Build a separate list for each row.
    return [[0] * n for _ in range(n)]
```

`total` only ever holds one running sum, however long the list. `reversed_copy` builds a new list of n items. `table` builds n rows of n entries.

In a model that reads or writes only O(1) cells per step, an O(T)-time computation can touch only O(T) **auxiliary cells**. This excludes the pre-existing input and does not bound untouched virtual memory reserved by an allocator. Low space does not imply low time: an n-bit counter can enumerate 2ⁿ values while reusing O(n) bits.

## Producing values one at a time

The reverse also happens: when memory is tight, you can recompute values instead of storing them, or process data as a **stream**.

```python
# builds a list of n squares: O(n) space
sum([x * x for x in range(n)])

# generator: one value at a time, O(1)
sum(x * x for x in range(n))
# Both expressions give 30 when n is 5.
```

## Key takeaways
- Say whether the space count includes the input and output.
- Measure the largest amount of extra memory held at once.
- A generator can supply values one at a time instead of storing the whole intermediate list.

## Further reading
- [Space complexity — Wikipedia](https://en.wikipedia.org/wiki/Space_complexity)
