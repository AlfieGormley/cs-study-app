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

CPython over-allocates by about **12.5%** plus a small constant. When a list needs room for more elements, `list_resize` in the CPython source picks the new capacity like this:

```formula reference
new ≈ n + n / 8 + 6
where
new: the new capacity (number of pointer slots) CPython allocates
n: the number of elements the list must now hold
≈: approximately: in the real code n/8 is rounded down to a whole number and the result is rounded down to a multiple of 4
In words: CPython makes room for the elements needed, plus about an eighth more, plus a few spare slots so small lists don't resize on every append. That is a growth factor of only about 1.125, much milder than doubling.
```

The source comments give the capacity sequence for one-at-a-time appends as 0, 4, 8, 16, 24, 32, 40, 52, 64, 76... Two details are worth knowing, both specific to the CPython version you run (checked here against the 3.14 source):

- A large bulk extension, where the requested growth is bigger than the proposed spare room, gets almost no spare capacity.
- A conventional GIL-enabled build resizes with `realloc`, which can sometimes extend the block in place; the free-threaded build allocates new storage and copies the references across.

The mild factor saves memory while still giving amortised O(1) append, as the previous unit showed for any factor above 1. `sys.getsizeof` on a list reveals backing-capacity jumps for your particular build.

For a list of n elements:

- `append` and `pop()` are amortised O(1).
- `insert(0, x)` and `pop(0)` are O(n). Use `collections.deque` for a queue (covered later in this module).
- For dense numbers, `array.array` or NumPy store raw values contiguously, which is far more compact and cache-friendly.

### Java `ArrayList`

`ArrayList` wraps an `Object[]`. A default-constructed list allocates its 10-slot backing array lazily, on the first `add`. When it fills, OpenJDK 21 grows it by about **1.5x**: the source asks for the old capacity plus half of it, rounded down (written `old + (old >> 1)`, where `>> 1` shifts the bits right one place). From 10 slots that gives 15, then 22, then 33. A larger required minimum or the array-size limit can override that. `ensureCapacity(n)` or `new ArrayList<>(n)` pre-sizes it to hold n elements.

Because Java generics only hold objects, `ArrayList<Integer>` stores references to boxed `Integer` objects. An `int[]` of a million elements is about 4 MB; an `ArrayList<Integer>` of a million is several times that (the exact figure depends on the JVM's object layout), plus the pointer chasing.

> [!analogy] Real-world analogy: An address book versus a row of houses
> An address book has equal-sized lines, each holding the address of a house somewhere in town. A terrace of identical houses, by contrast, *is* the row of homes.
>
> **How it maps:** A Python `list` or Java `ArrayList<Integer>` is the address book: its contiguous slots hold references, and each value lives in its own object elsewhere on the heap. A C++ `vector<int>`, Java `int[]` or NumPy array is the terrace: the values themselves sit side by side. Reading every value from the address book means a trip to each house, which is the extra indirection and cache cost.
>
> **Where it stops:** Several address-book lines can name the same house, just as several list slots can reference one object, and the reference model is what lets a Python list hold mixed types. Real memory cost also includes object headers and allocator overhead that the picture leaves out.

### C++ `std::vector`

`vector` stores elements directly and contiguously. The standard requires amortised constant `push_back` but leaves the growth factor to the implementation: current library sources show libstdc++ and libc++ doubling the capacity and MSVC's library growing it by half for ordinary one-at-a-time growth, but those are implementation details rather than portable guarantees.

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
