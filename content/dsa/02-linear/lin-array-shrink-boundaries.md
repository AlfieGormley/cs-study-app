---
id: lin-array-shrink-boundaries
title: Shrinking without resize thrashing
level: basic
minutes: 2
sourceLesson: lin-arrays
summary: Leave a gap between growth and shrink thresholds.
---

Growing a dynamic array pays for occasional copying by leaving spare room for later operations. Shrinking must also leave room between resize boundaries; otherwise a push and pop can undo each other’s expensive allocation. Here n denotes the current number of live elements.

## Shrinking and other pitfalls

- **Shrink thrash.** If you double when full and halve when below half full, a workload that alternates push and pop right at the boundary resizes on every operation. The standard fix is to halve only when the array falls to a **quarter** full. CPython shrinks only when length drops below half the allocated size, and then reallocates with room to spare.
- **Wasted capacity.** After growth, up to half the slots (with doubling) may be empty. C++ shrink_to_fit makes a nonbinding request to reduce capacity; Java trimToSize reduces backing capacity to size. Allocators and garbage collectors determine when memory is reclaimed or returned to the OS.
- **Off-by-one errors.** The last valid index is one less than the array length. In C there is no bounds check, so reading or writing `a[len]` has undefined behavior, which can corrupt memory, crash or behave unpredictably, a classic source of security bugs.

## Key takeaways
- Leave a gap between growth and shrink thresholds.
- Capacity reclamation and bounds safety are separate from append amortisation.

## Further reading
- [Dynamic array — Wikipedia](https://en.wikipedia.org/wiki/Dynamic_array)
- [CPython listobject.c (list_resize)](https://github.com/python/cpython/blob/main/Objects/listobject.c)
- [std::vector — cppreference](https://en.cppreference.com/w/cpp/container/vector)
- [ArrayList — Java SE 21 API](https://docs.oracle.com/en/java/javase/21/docs/api/java.base/java/util/ArrayList.html)
