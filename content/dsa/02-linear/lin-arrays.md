---
id: lin-arrays
title: Arrays and memory
level: basic
minutes: 11
summary: Why arrays give O(1) indexing, how contiguous memory and CPU caches make them fast, and how dynamic arrays like Python's list, Java's ArrayList and C++'s vector grow.
---

An **array** is the simplest data structure there is: a fixed number of same-sized slots laid out one after another in memory. Almost every other structure in this course is either built on arrays or defined by how it differs from one.

Two properties make arrays special:

- **Contiguous layout.** Element `i+1` sits immediately after element `i`. There are no gaps and no pointers between them.
- **Uniform element size.** Every slot is the same number of bytes, so the machine can compute where any element lives.

Everything good about arrays (instant indexing, cache-friendliness) and everything bad (expensive inserts, fixed size) follows from those two facts.

## Indexing is arithmetic

If an array starts at address `base` and each element takes `size` bytes, element `i` lives at:

```
address(i) = base + i * size
```

That is one multiply and one add, whatever the array's length. This is why indexing is **O(1)**: the CPU does not walk to element `i`, it calculates where it is.

```
int32 array, base = 1000, size = 4

index:    0     1     2     3     4
        +-----+-----+-----+-----+-----+
        |  7  | 12  |  3  | 40  |  9  |
        +-----+-----+-----+-----+-----+
addr:   1000  1004  1008  1012  1016
```

This also explains why most languages start indexing at **0**: the index is an *offset* from the start. Element 0 is zero elements past `base`.

> [!note] O(1) access, O(n) search
> Indexing by position is O(1). Finding a *value* in an unsorted array is still O(n), because you must look at each slot. If the array is sorted, binary search finds a value in O(log n).

## Why contiguous memory is fast

Both indexed access and a single pointer load are constant-time operations in the usual RAM model. Their measured latencies can differ because that model abstracts away the memory hierarchy.

CPUs do not fetch single bytes from RAM. They fetch a **cache line**, typically 64 bytes, and keep it in a small, fast cache. A cache hit can be much faster than a main-memory access; latency depends on hardware, contention and access pattern.

> [!note] Evidence gap
> Universal nanosecond latency figures are omitted because no measured hardware configuration or reproducible benchmark is provided.

When you scan an array, one cache line brings in sixteen 4-byte integers at once. The hardware **prefetcher** also spots the sequential pattern and loads the next lines before you ask. This is **spatial locality**, and it is why a simple loop over an array is one of the fastest things a computer can do.

A linked list (lesson 3) scatters its nodes around the heap. Each step can be a cache miss. Same O(n) on paper; often several times slower in practice.

### 2D arrays: row-major order

A rectangular built-in C or C++ array is contiguous and row-major: row 0 first, then row 1. A newly created C-order NumPy array has this layout too; NumPy also supports other strides and orders. Java int[][] is an array of references to separate int[] rows, which may have different lengths. Fortran, MATLAB and R normally use column-major layout.

```
grid (3 x 4), row-major:

[r0c0 r0c1 r0c2 r0c3 r1c0 r1c1 ...]

address(r, c) = base + (r * cols + c) * size
```

Loop order matters. Iterating row by row walks memory sequentially. Iterating column by column jumps `cols * size` bytes every step, potentially touching a different cache line each time when that stride is large. Performance depends on dimensions, cache hierarchy and compiler transformations.

## Operations and their cost

| Operation | Cost | Why |
|---|---|---|
| Read/write `a[i]` | O(1) | Address arithmetic |
| Search (unsorted) | O(n) | Check every slot |
| Insert/delete at end | O(1)* | No shifting |
| Insert/delete at `i` | O(n − i + 1) without resizing | Shift the tail; reallocation may add O(n) |

*For a dynamic array, amortised; see below.

Inserting at position `i` means shifting every later element one slot right to make room. Inserting at the front of a million-element array moves a million elements.

```python
a = [10, 20, 30, 40]
a.insert(1, 15)   # shifts 20, 30, 40 right
print(a)          # [10, 15, 20, 30, 40]
```

## Static vs dynamic arrays

A **fixed-size array** has a size chosen when it is created; this is distinct from static storage duration. C's `int a[100]` and Java's `new int[100]` are static: you cannot append a 101st element.

A **dynamic array** (resizable array) wraps a static array and tracks two numbers:

- **length**: how many elements are in use.
- **capacity**: how many slots the underlying array has.

When `length == capacity` and you append, it allocates a bigger array, copies everything across, and frees the old one.

```
capacity 4, length 4: full
[ a | b | c | d ]

append e -> allocate 8, copy, add e
[ a | b | c | d | e |   |   |   ]
```

### Why growth must be geometric

Copying is O(n), so you might expect appends to be slow. The trick is *how much* to grow.

If capacity **doubles** each time, then, from initial capacity 1, total resizing copies are C − 1, where C is the final capacity. Since n ≤ C < 2n, this is fewer than 2n copies. Spread over n appends, that is fewer than two copies per append: **amortised O(1)**.

Growing by any constant factor `r > 1` works. Ignoring integer rounding, total copying is roughly C / (r − 1), where C is final capacity. At full-capacity endpoints C = n, the following approximations apply; just after growth C is close to rn:

| Growth factor | Copies when n fills final capacity |
|---|---|
| 2 | about n |
| 1.5 | about 2n |
| 1.125 | about 8n |

Growing by a constant *amount* (say +10 slots) does not work. Reaching `n` elements needs n/10 resizes, copying 10 + 20 + 30 + ... elements: O(n²) in total.

> [!warning] Amortised is not worst case
> An individual append that triggers a resize is O(n). If you append to a 10-million-element vector in a latency-sensitive loop, that one append copies 10 million elements. When you know the final size, reserve it up front.

## Real implementations

### Python `list`

A Python list is a dynamic array of **pointers** to objects (8 bytes each on a 64-bit machine), not of the values themselves. `[1, 2, 3]` stores three pointers to three separate `int` objects elsewhere on the heap.

CPython over-allocates by about **12.5%** plus a small constant. The source comments give the capacity sequence as 0, 4, 8, 16, 24, 32, 40, 52, 64, 76... For a fixed CPython build, sys.getsizeof on an ordinary list can reveal backing-capacity changes. The mild factor saves memory; CPython leans on `realloc`, which can often extend a block in place without copying.

- `append` and `pop()` are amortised O(1).
- `insert(0, x)` and `pop(0)` are O(n). Use `collections.deque` for a queue (lesson 6).
- For dense numbers, `array.array` or NumPy store raw values contiguously, which is far more compact and cache-friendly.

### Java `ArrayList`

`ArrayList` wraps an `Object[]`. A default-constructed list allocates its 10-slot backing array lazily, on the first `add`, and grows by **1.5x** (`old + (old >> 1)`). `ensureCapacity(n)` or `new ArrayList<>(n)` pre-sizes it.

Because Java generics only hold objects, `ArrayList<Integer>` stores references to boxed `Integer` objects. An `int[]` of a million elements is about 4 MB; an `ArrayList<Integer>` of a million is several times that, plus the pointer chasing.

### C++ `std::vector`

`vector` stores elements directly and contiguously. The standard requires amortised constant `push_back` but leaves the growth factor to the implementation: common libraries use factors such as 2 or 1.5 for ordinary incremental growth, but those are implementation details rather than portable guarantees.

`reserve(n)` ensures capacity is at least n without changing size; it does not shrink existing capacity. The crucial pitfall is **invalidation**: a reallocation moves every element, so any pointer, reference or iterator into the vector becomes dangling.

```cpp
std::vector<int> v = {1, 2, 3};
int& first = v[0];
v.push_back(4);  // may reallocate
// 'first' may now dangle: using it is
// undefined behaviour
```

## Shrinking and other pitfalls

- **Shrink thrash.** If you double when full and halve when below half full, a workload that alternates push and pop right at the boundary resizes on every operation. The standard fix is to halve only when the array falls to a **quarter** full. CPython shrinks only when length drops below half the allocated size, and then reallocates with room to spare.
- **Wasted capacity.** After growth, up to half the slots (with doubling) may be empty. C++ shrink_to_fit makes a nonbinding request to reduce capacity; Java trimToSize reduces backing capacity to size. Allocators and garbage collectors determine when memory is reclaimed or returned to the OS.
- **Off-by-one errors.** The last valid index is `len − 1`. In C there is no bounds check, so reading or writing `a[len]` has undefined behavior, which can corrupt memory, crash or behave unpredictably, a classic source of security bugs.

## Key takeaways
- An array is contiguous, same-sized slots, so `a[i]` is one address calculation: O(1).
- Contiguity gives cache-friendly scans; this matters as much as Big-O in practice.
- Inserting or deleting anywhere but the end shifts elements: O(n).
- Dynamic arrays grow geometrically, which makes append amortised O(1); additive growth would be O(n²).
- Python lists hold pointers and grow ~12.5%; ArrayList grows 1.5x; vector grows 2x or 1.5x depending on the library.
- Reallocation invalidates pointers and iterators into a C++ vector.

## Further reading
- [Dynamic array — Wikipedia](https://en.wikipedia.org/wiki/Dynamic_array)
- [Array (data structure) — Wikipedia](https://en.wikipedia.org/wiki/Array_(data_structure))
- [CPython listobject.c (list_resize)](https://github.com/python/cpython/blob/main/Objects/listobject.c)
- [std::vector — cppreference](https://en.cppreference.com/w/cpp/container/vector)
- [ArrayList — Java SE 21 API](https://docs.oracle.com/en/java/javase/21/docs/api/java.base/java/util/ArrayList.html)
- [Row- and column-major order — Wikipedia](https://en.wikipedia.org/wiki/Row-_and_column-major_order)
