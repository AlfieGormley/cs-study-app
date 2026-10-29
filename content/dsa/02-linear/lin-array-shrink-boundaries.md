---
id: lin-array-shrink-boundaries
title: Shrinking without resize thrashing
level: basic
minutes: 3
sourceLesson: lin-arrays
summary: Leave a gap between growth and shrink thresholds.
---

Growing a dynamic array pays for occasional copying by leaving spare room for later operations. Shrinking must also leave room between resize boundaries; otherwise a push and pop can undo each other’s expensive allocation. Here n denotes the current number of live elements.

## Shrinking and other pitfalls

- **Shrink thrash.** If you double when full and halve as soon as a pop leaves the array half full or less, a workload that alternates push and pop right at the boundary resizes on every operation. The standard fix is to halve only when the array falls to a **quarter** full, so many cheap operations must happen between any two resizes. CPython's lists reallocate to shrink only when the length drops below half the allocated size, and then keep some room to spare. From CPython 3.14.9 and 3.15.1 (October 2026), a list with 32 or fewer allocated slots is no longer shrunk at all; details like this vary by version.
- **Wasted capacity.** After growth, up to half the slots (with doubling) may be empty. C++ shrink_to_fit makes a nonbinding request to reduce capacity; Java trimToSize reduces backing capacity to size. Allocators and garbage collectors determine when memory is reclaimed or returned to the OS.
- **Off-by-one errors.** The last valid index is one less than the array length. In C there is no bounds check, so reading or writing `a[len]` has undefined behavior, which can corrupt memory, crash or behave unpredictably, a classic source of security bugs.

> [!analogy] Real-world analogy: A thermostat with a dead band
> A heating thermostat that switches on below 20 °C and off above 20 °C would click on and off every few seconds as the room hovers around 20 °C. Real thermostats leave a gap, say on at 19.5 °C and off at 20.5 °C, so each switch is followed by a calm stretch.
>
> **How it maps:** Growing when full and shrinking when half full puts the two switching points at the same length after a resize, so alternating push and pop toggles the expensive resize every time. Shrinking only at a quarter full is the dead band: after any resize, many cheap operations must happen before the next one.
>
> **Where it stops:** Switching a boiler costs about the same each time, whereas each resize copies every live element, so its cost grows with the array. The array's thresholds are exact element counts, not noisy temperature readings.

## Key takeaways
- Leave a gap between growth and shrink thresholds.
- Capacity reclamation and bounds safety are separate from append amortisation.

## Further reading
- [Dynamic array — Wikipedia](https://en.wikipedia.org/wiki/Dynamic_array)
- [CPython listobject.c (list_resize)](https://github.com/python/cpython/blob/main/Objects/listobject.c)
- [std::vector — cppreference](https://en.cppreference.com/w/cpp/container/vector)
- [ArrayList — Java SE 21 API](https://docs.oracle.com/en/java/javase/21/docs/api/java.base/java/util/ArrayList.html)
