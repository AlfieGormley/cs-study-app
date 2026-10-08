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

Memory is a long row of numbered bytes; the number of a byte is its **memory address**. To read element `i`, the machine needs that element's address. Because the slots are contiguous and all the same size, it can work the address out directly from where the array starts:

```formula
address(i) = base + i × size
where
address(i): the memory address of the first byte of element i
i: the index of the element you want, counting from 0
base: the memory address where the array starts (the address of element 0)
size: how many bytes one element takes, e.g. 4 for a 32-bit integer, 8 for a 64-bit float or a pointer
In words: skip over i whole elements from the start of the array; the element you want begins right there.
```

For the array drawn below (base 1000, 4-byte integers), element 3 is at 1000 + 3 × 4 = 1012. The formula only works because every slot is the same size and there are no gaps; a structure without those two properties (a linked list, for example) has no such shortcut.

That is one multiply and one add, whatever the array's length. This is why indexing is **O(1)**, or **constant time**: the cost does not grow as the array gets longer. The CPU does not walk to element `i`, it calculates where it is.

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
> For an array of n elements: indexing by position is O(1). Finding a *value* in an unsorted array is still O(n) (**linear time**: the work grows in proportion to n), because you must look at each slot. If the array is sorted, binary search finds a value in O(log n), where log n means log₂ n, the number of times you can halve n before reaching 1 (about 20 for a million elements).

## Why contiguous memory is fast

Both indexed access and a single pointer load are constant-time operations in the usual RAM model. Their measured latencies can differ because that model abstracts away the memory hierarchy.

CPUs do not fetch single bytes from RAM. They fetch a **cache line**, typically 64 bytes, and keep it in a small, fast cache. A cache hit can be much faster than a main-memory access; latency depends on hardware, contention and access pattern.

> [!note] Evidence gap
> Universal nanosecond latency figures are omitted because no measured hardware configuration or reproducible benchmark is provided.

When you scan an array, one cache line brings in sixteen 4-byte integers at once. The hardware **prefetcher** also spots the sequential pattern and loads the next lines before you ask. This is **spatial locality**, and it is why a simple loop over an array is one of the fastest things a computer can do.

A linked list (lesson 3) scatters its nodes around the heap. Each step can be a cache miss. Scanning n elements is O(n) for both on paper; the list is often several times slower in practice.

### 2D arrays: row-major order

A rectangular built-in C or C++ array is contiguous and row-major: row 0 first, then row 1. A newly created C-order NumPy array has this layout too; NumPy also supports other strides and orders. Java int[][] is an array of references to separate int[] rows, which may have different lengths. Fortran, MATLAB and R normally use column-major layout.

```
grid (3 x 4), row-major:

[r0c0 r0c1 r0c2 r0c3 r1c0 r1c1 ...]
```

To find element (r, c), skip r whole rows, then c more elements within the row:

```formula
address(r, c) = base + (r × cols + c) × size
where
address(r, c): the memory address of the element in row r, column c
r: the row number, counting from 0
c: the column number, counting from 0
cols: how many columns each row has (4 in the grid above)
base: the memory address of element (0, 0), where the grid starts
size: how many bytes one element takes
In words: count how many elements come before (r, c) in the one long row-major line, then turn that count into bytes.
```

For the 3 × 4 grid of 4-byte integers starting at address 1000, element (1, 2) is at 1000 + (1 × 4 + 2) × 4 = 1000 + 24 = 1024. In a column-major language the roles swap: you skip whole columns first.

Loop order matters. Iterating row by row walks memory sequentially. Iterating column by column jumps a whole row's worth of bytes (cols × size) every step, potentially touching a different cache line each time when that **stride** is large. Performance depends on dimensions, cache hierarchy and compiler transformations.

## Operations and their cost

In this table n is the number of elements in the array and i is the position being read or changed.

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

When the length equals the capacity and you append, it allocates a bigger array, copies everything across, and frees the old one.

```
capacity 4, length 4: full
[ a | b | c | d ]

append e -> allocate 8, copy, add e
[ a | b | c | d | e |   |   |   ]
```

### Why growth must be geometric

Copying n elements is O(n) work, so you might expect appends to be slow. The trick is *how much* to grow. To compare growth policies, count the total number of element copies that resizing makes while you append n elements one at a time.

If capacity **doubles** each time, starting from capacity 1, the resizes copy 1, then 2, then 4, and so on, each resize copying the whole old array:

```formula
copies = 1 + 2 + 4 + ... + C/2
copies = C − 1
copies < 2 × n
where
copies: the total number of element copies made by all the resizes together
C: the final capacity, the smallest power of two that is at least n
n: the number of elements appended
In words: each resize copies as many elements as all the earlier resizes put together, plus one, so the grand total is always just under the final capacity, which is less than twice the number of elements.
```

For example, 17 appends end at capacity 32 after copying 1 + 2 + 4 + 8 + 16 = 31 elements, fewer than 2 × 17 = 34. Spread over n appends, that is fewer than two copies per append: **amortised O(1)**. *Amortised* means averaged over a long run of operations: an occasional append is expensive, but the total for n appends is still proportional to n.

Growing by any constant factor greater than 1 works. Going backwards from the last resize, each earlier resize copied 1/r as many elements as the one after it, so the copies form a shrinking **geometric series**:

```formula
copies ≈ C/r + C/r^2 + C/r^3 + ...
copies ≈ C / (r − 1)
where
copies: the total number of element copies made by all the resizes together
C: the final capacity
r: the growth factor: each resize multiplies the capacity by r, which must be greater than 1 (2 means doubling, 1.5 means grow by half)
≈: approximately equal to; integer rounding and the small starting capacity are ignored
In words: the total copying is the final capacity divided by (growth factor − 1). A factor close to 1 grows gently, saving memory, but copies more in total.
```

The formula holds for any number of appends, but the numbers are easiest to read when the last append exactly fills the final capacity, so C = n. Just after a resize, C can be close to r × n instead. With C = n:

| Growth factor | Copies when n fills final capacity |
|---|---|
| 2 | about n |
| 1.5 | about 2n |
| 1.125 | about 8n |

For instance, with factor 1.5 and a million elements: 1,000,000 / (1.5 − 1) = 2,000,000 copies. Every factor gives a total proportional to n, so append stays amortised O(1); smaller factors just pay a larger constant.

Growing by a constant *amount* (say +10 slots) does not work. Each resize now copies only 10 more elements than the last, so the copies form an **arithmetic series** whose total grows with the square of n:

```formula
resizes ≈ n / c
copies ≈ c + 2 × c + ... + n
copies ≈ n^2 / (2 × c)
where
resizes: how many times the array has to grow
copies: the total number of element copies made by all the resizes together
n: the number of elements appended
c: the fixed number of slots added at each resize, e.g. 10
≈: approximately equal to; small end effects are ignored
In words: adding a fixed number of slots means a resize every c appends, and each one copies everything so far, so total copying grows with n squared.
```

With c = 10 and a million elements that is about 1,000,000² / 20 = 5 × 10¹⁰ copies, against about a million for doubling. That is O(n²), **quadratic** time.

> [!warning] Amortised is not worst case
> An individual append that triggers a resize is O(n). If you append to a 10-million-element vector in a latency-sensitive loop, that one append copies 10 million elements. When you know the final size, reserve it up front.

## Real implementations

### Python `list`

A Python list is a dynamic array of **pointers** to objects (8 bytes each on a 64-bit machine), not of the values themselves. `[1, 2, 3]` stores three pointers to three separate `int` objects elsewhere on the heap.

CPython over-allocates by about **12.5%** plus a small constant. When a list needs room for n elements, `list_resize` in the CPython source picks the new capacity like this:

```formula
new ≈ n + n/8 + 6
where
new: the new capacity (number of pointer slots) CPython allocates
n: the number of elements the list must now hold
≈: approximately: in the real code n/8 is rounded down to a whole number and the result is rounded down to a multiple of 4
In words: make room for the elements needed, plus an eighth more (12.5%), plus a few spare slots so small lists don't resize on every append.
```

For n = 9: 9 + 1 + 6 = 16 (9/8 is rounded down to 1, and 16 is already a multiple of 4), so the capacity jumps to 16. For n = 17: 17 + 2 + 6 = 25, rounded down to 24. The source comments give the capacity sequence as 0, 4, 8, 16, 24, 32, 40, 52, 64, 76... For a fixed CPython build, sys.getsizeof on an ordinary list can reveal backing-capacity changes. The mild factor saves memory; CPython leans on `realloc`, which can often extend a block in place without copying.

For a list of n elements:

- `append` and `pop()` are amortised O(1).
- `insert(0, x)` and `pop(0)` are O(n). Use `collections.deque` for a queue (lesson 6).
- For dense numbers, `array.array` or NumPy store raw values contiguously, which is far more compact and cache-friendly.

### Java `ArrayList`

`ArrayList` wraps an `Object[]`. A default-constructed list allocates its 10-slot backing array lazily, on the first `add`, and grows by **1.5x**. The source writes this as `old + (old >> 1)`; `>> 1` shifts the bits right by one place, which halves a whole number and drops any remainder:

```formula
new = old + ⌊old / 2⌋
where
new: the capacity after growing, in elements
old: the capacity before growing, in elements
⌊ ⌋: floor: round down to a whole number
In words: the new array is the old size plus half again, rounded down.
```

From the default 10 slots this gives 15, then 15 + 7 = 22, then 22 + 11 = 33. `ensureCapacity(n)` or `new ArrayList<>(n)` pre-sizes it to hold n elements.

Because Java generics only hold objects, `ArrayList<Integer>` stores references to boxed `Integer` objects. An `int[]` of a million elements is about 4 MB; an `ArrayList<Integer>` of a million is several times that, plus the pointer chasing.

### C++ `std::vector`

`vector` stores elements directly and contiguously. The standard requires amortised constant `push_back` but leaves the growth factor to the implementation: common libraries use factors such as 2 or 1.5 for ordinary incremental growth, but those are implementation details rather than portable guarantees.

`reserve(n)` ensures capacity is at least n without changing size; it does not shrink existing capacity. The crucial pitfall is **iterator invalidation**: a reallocation moves every element, so any pointer, reference or iterator into the vector becomes dangling.

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
- Inserting or deleting anywhere but the end shifts elements: O(n) for an array of n elements.
- Dynamic arrays grow geometrically, which makes append amortised O(1); additive growth would make n appends cost O(n²) in total.
- Python lists hold pointers and grow ~12.5%; ArrayList grows 1.5x; vector grows 2x or 1.5x depending on the library.
- Reallocation invalidates pointers and iterators into a C++ vector.

## Further reading
- [Dynamic array — Wikipedia](https://en.wikipedia.org/wiki/Dynamic_array)
- [Array (data structure) — Wikipedia](https://en.wikipedia.org/wiki/Array_(data_structure))
- [CPython listobject.c (list_resize)](https://github.com/python/cpython/blob/main/Objects/listobject.c)
- [std::vector — cppreference](https://en.cppreference.com/w/cpp/container/vector)
- [ArrayList — Java SE 21 API](https://docs.oracle.com/en/java/javase/21/docs/api/java.base/java/util/ArrayList.html)
- [Row- and column-major order — Wikipedia](https://en.wikipedia.org/wiki/Row-_and_column-major_order)
