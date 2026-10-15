---
id: cache-short-field-layout
title: Choose AoS, SoA and compact fields
level: intermediate
minutes: 4
sourceLesson: cache-arch-friendly-code
summary: Store frequently scanned fields densely to avoid fetching unused record fields.
---

This unit builds on the earlier cache lessons and focuses on choose aos, soa and compact fields. Keep each example’s stated hardware geometry and model assumptions when applying its result.

## Array of structs vs struct of arrays

How you group fields decides how many useful bytes each line brings in.

```c
// AoS: assume 4-byte floats, sizeof = 32
struct Particle {
    float x, y, z;
    float vx, vy, vz;
    float mass, charge;
};
struct Particle p[N];

// SoA: one contiguous array per field.
// A pass over x and vx skips other fields.
struct Particles {
    float x[N], y[N], z[N];
    float vx[N], vy[N], vz[N];
    float mass[N], charge[N];
};
```

Assume 4-byte floats, a 32-byte Particle, aligned cold 64-byte lines, and each needed line fetched once. Consider a pass that only does `x += vx * dt`. The following counts cover data brought into the cache, excluding later dirty write-backs and extra hardware traffic:

- **AoS**: each particle's 32 bytes come in together, but only 8 (x and vx) are used. 75% of every line is wasted. For 1,000,000 particles, the loop drags 1,000,000 × 32 bytes = 32 MB through the cache.
- **SoA**: `x[]` and `vx[]` are dense arrays, so every byte fetched is used: 8 MB read. Contiguous values can also support vectorisation; for example, a 256-bit AVX vector holds eight 32-bit floats when that instruction set is available.

AoS can be useful when accessing most fields of one record together; SoA can still win for some vectorised whole-record workloads. Columnar storage, including the Parquet file format, applies the related idea of grouping values by column, but a file format is not itself an in-memory C SoA structure.

A middle path is **hot/cold splitting**: keep the frequently used fields in a compact struct, and move rarely used ones (names, debug info) behind a pointer or into a parallel array.

## Other habits that help

- Consider contiguous numeric storage. C++ `std::vector` (apart from specialised representations such as `vector<bool>`), Rust `Vec`, conventional HotSpot Java primitive arrays and contiguous NumPy arrays keep element storage together. NumPy views need not be contiguous. Reference containers such as CPython lists and Java `ArrayList<Integer>` add indirection; elements can share objects.
- Inspect struct alignment and padding. On an ABI with 8-byte doubles and 8-byte double alignment, a `char` followed by a `double` can require 7 padding bytes. Reordering can help, but may merely move padding to the end; compare `sizeof` and offsets rather than assuming sorting by size shrinks every record.
- **Fuse loops** that walk the same arrays so data is reused while hot, instead of streaming the arrays twice.
- Shrink the data. `float` instead of `double`, `int32` indices instead of pointers, bitsets instead of `bool` arrays.
- Measure. `perf stat -e cache-misses,L1-dcache-load-misses` on Linux, or Instruments on macOS, tells you whether a change actually reduced misses.

Python’s `array.array('d')` is another dense numeric representation: it stores C doubles rather than object references. Check its `itemsize` for the platform; NumPy `float64` specifically uses eight bytes. Conventional HotSpot primitive arrays contain values inline, while `ArrayList<Integer>` contains references to boxed objects. A managed language’s abstract array semantics do not by themselves specify every runtime’s physical placement.

## Pitfalls

- Optimising cold code. Restructuring data only matters in loops that dominate run time; profile first.
- Loop blocking for the wrong level or size. A tile that fits L1 on one machine may not on another; libraries tune or detect sizes.
- Trusting the compiler to fix loop order. Compilers can interchange simple loops, but aliasing (a pair of pointers that might overlap) often stops them.

## Key takeaways
- Store frequently scanned fields densely to avoid fetching unused record fields.
- Compare actual layout, alignment, indirection and hot-loop measurements before choosing a representation.

## Further reading
- [CMU: Cache memories and matrix locality](https://www.cs.cmu.edu/afs/cs/academic/class/15213-m19/www/lectures/12-cache-memories.pdf)
- [Memory part 5: What programmers can do, Ulrich Drepper (LWN)](https://lwn.net/Articles/255364/)
- [Row- and column-major order — Wikipedia](https://en.wikipedia.org/wiki/Row-_and_column-major_order)
- [Loop nest optimization — Wikipedia](https://en.wikipedia.org/wiki/Loop_nest_optimization)
- [AoS and SoA — Wikipedia](https://en.wikipedia.org/wiki/AoS_and_SoA)
- [The N-dimensional array: memory layout — NumPy docs](https://numpy.org/doc/stable/reference/arrays.ndarray.html)
- [Computer Systems: A Programmer's Perspective (CS:APP)](https://csapp.cs.cmu.edu/)
