---
id: lin-array-runtime-layouts
title: Array layouts in Python, Java and C++
level: basic
minutes: 4
sourceLesson: lin-arrays
summary: Python lists and Java generic lists store references; vector stores values directly.
---

The previous units established contiguous slots and amortised growth. The slot may contain a raw value or a reference to a separate object: the language runtime decides. Details below refer to CPython and OpenJDK 21 where named, rather than every implementation of Python or Java.

## Real implementations

### Python `list`

A Python list is a dynamic array of **pointers** to objects (8 bytes each on a conventional 64-bit CPython build), not of the values themselves. `[1, 2, 3]` stores three pointers to three separate `int` objects elsewhere on the heap.

CPython over-allocates by about **12.5%** plus a small constant. When a list needs room for n elements, `list_resize` in the CPython source picks the new capacity like this:

```formula
new ≈ n + n / 8 + 6
where
new: the new capacity (number of pointer slots) CPython allocates
n: the number of elements the list must now hold
≈: approximately: in the real code n/8 is rounded down to a whole number and the result is rounded down to a multiple of 4
In words: make room for the elements needed, plus an eighth more (12.5%), plus a few spare slots so small lists don't resize on every append.
```

For nine required elements, the extra eighth rounds down to one, producing capacity sixteen. For seventeen, it rounds down to two: the provisional twenty-five slots round down to twenty-four. For incremental single-item growth, the source comments give the capacity sequence as 0, 4, 8, 16, 24, 32, 40, 52, 64, 76... For a fixed CPython build, sys.getsizeof on an ordinary list can reveal backing-capacity changes. For a large bulk extension, CPython can instead suppress most spare capacity when the requested growth exceeds the proposed spare room. The mild factor saves memory; a conventional GIL-enabled CPython build can use `realloc` to extend a block in place when the allocator permits. The free-threaded build’s resize path instead allocates replacement storage and copies references.

For a list of n elements:

- `append` and `pop()` are amortised O(1).
- `insert(0, x)` and `pop(0)` are O(n). Use `collections.deque` for a queue (covered later in this module).
- For dense numbers, `array.array` or NumPy store raw values contiguously, which is far more compact and cache-friendly.

### Java `ArrayList`

`ArrayList` wraps an `Object[]`. A default-constructed list allocates its 10-slot backing array lazily, on the first `add`, and uses roughly **1.5x** incremental growth in OpenJDK 21. A larger required minimum or an array-size limit can change that result. The source writes this as `old + (old >> 1)`; `>> 1` shifts the bits right by one place, which halves a whole number and drops any remainder:

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

## Key takeaways
- Python lists and Java generic lists store references; vector stores values directly.
- Reserve space before keeping C++ pointers into a vector.

## Further reading
- [CPython listobject.c (list_resize)](https://github.com/python/cpython/blob/main/Objects/listobject.c)
- [std::vector — cppreference](https://en.cppreference.com/w/cpp/container/vector)
- [ArrayList — Java SE 21 API](https://docs.oracle.com/en/java/javase/21/docs/api/java.base/java/util/ArrayList.html)
