---
id: sys-allocation-arithmetic
title: Check arithmetic before allocating
level: intermediate
minutes: 4
sourceLesson: sys-memory-bugs
summary: Unsigned wraparound is defined arithmetic, but a wrapped allocation size can lead to invalid accesses.
---

## Integer overflow leading to a small allocation

Size arithmetic can suffer integer wraparound. Consider:

```c
/* BUG: product may wrap before malloc. */
/* count comes from a file header. */
item *arr = malloc(count * sizeof(item));
/* No allocation-failure check here. */
for (uint32_t i = 0; i < count; i++)
    read_item(&arr[i]);
```

Assume both `count` and `size_t` are 32-bit unsigned types, and `sizeof(item)` is 16. C's unsigned arithmetic does not fail when a result is too big: it keeps only the lowest 32 bits of the result and silently drops the rest (this is called modular arithmetic). With a hostile header the numbers look like this:

```c
/* 32-bit size_t, sizeof(item) == 16   */
/* count       = 0x10000001            */
/* true bytes  = 0x100000010 (33 bits) */
/* malloc gets = 0x00000010 = 16 bytes */
```

About 268 million items should need about 4 GiB, but the 33rd bit is dropped and `malloc` is asked for just 16 bytes. Allocation may fail; if it succeeds, the loop's item writes run far past that 16-byte allocation, a heap overflow with undefined behaviour.

> [!analogy] Real-world analogy: a car odometer rolling over
> A five-digit mileage counter that reads 99,990 shows 00,006 after another 16 miles. Nothing breaks and no warning appears: the counter simply has no digit for the carry.
>
> **How it maps:** The counter's digits are the 32 bits of `size_t`. The lost carry is the 33rd bit of `count * sizeof(item)`. A buyer trusting the low reading is `malloc` trusting the small wrapped size.
>
> **Where it stops:** An odometer counts in decimal and its rollover is obvious to a person; unsigned C arithmetic is binary, and nothing in the program notices unless the code checks before multiplying.

The standard check avoids the multiplication altogether. The product fits only if it is no larger than `SIZE_MAX`, the largest value `size_t` can hold. Dividing `SIZE_MAX` by the item size gives the largest safe count, and that division cannot itself overflow. With a 32-bit `size_t` and 16-byte items the largest safe count is 268,435,455, so the count 268,435,457 (`0x10000001`) above is rejected.

Fixes:

- Check before multiplying: `if (count > SIZE_MAX / sizeof(item)) fail;`
- On documented implementations such as glibc, `calloc(count, sizeof(item))` and `reallocarray` reject size overflow. `reallocarray` is POSIX, not ISO C. Check allocation failure before dereferencing; define a policy for zero counts.
- Reject absurd values early: a sane maximum for `count` is good input validation anyway.

## Key takeaways
- Unsigned wraparound is defined arithmetic, but a wrapped allocation size can lead to invalid accesses.
- Check the count against SIZE_MAX divided by the item size before multiplying.
- Apply application-specific count limits and handle allocation failure and zero-count policy even when overflow is rejected.

## Further reading
- [C11 committee draft: objects and library contracts](https://www.open-std.org/jtc1/sc22/wg14/www/docs/n1570.pdf)
- [Allocating cleared space — glibc](https://sourceware.org/glibc/manual/latest/html_node/Allocating-Cleared-Space.html)
- [reallocarray — POSIX](https://pubs.opengroup.org/onlinepubs/9799919799/functions/reallocarray.html)
