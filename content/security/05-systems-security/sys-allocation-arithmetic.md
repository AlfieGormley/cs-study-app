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

Assume both `count` and `size_t` are 32-bit unsigned types, and `sizeof(item)` is 16. C's unsigned arithmetic does not fail when a result is too big: it keeps only the lowest 32 bits of the result (this is called modular arithmetic).

```formula
S = (ns) mod 2^32
ns = 0x10000001 × 16 = 0x100000010
ns = 268,435,457 × 16 = 4,294,967,312
S = 4,294,967,312 − 4,294,967,296
S = 16 B = 0x10 B
where
S: the byte count actually passed to malloc, in bytes (B)
n: the item count read from the file header (count in the code); here 0x10000001, which is 268,435,457
s: the size of one item in bytes, sizeof(item); 16 here
mod: modulo, the remainder after dividing; a value mod 2^32 keeps only its lowest 32 bits
2^32: 32 copies of 2 multiplied together, 4,294,967,296: the number of different values a 32-bit unsigned type can hold
0x10000001: a hexadecimal (base-16) number, marked by the 0x prefix; each hex digit is 4 bits
B: byte, 8 bits
In words: the true product needs 33 bits, so the 32-bit size type drops the top bit (subtracting 2^32 once), and 268,435,457 items of 16 bytes become a request for just 16 bytes.
```

Only 16 bytes are requested. Allocation may fail; if it succeeds, attempting all those item writes exceeds the allocation and invokes undefined behaviour.

The standard check avoids the multiplication altogether. The product fits only if it is no larger than `SIZE_MAX`, the largest value `size_t` can hold. Dividing both sides by the item size gives a test that cannot itself overflow:

```formula
ns ≤ M
n ≤ ⌊M / s⌋
M = 2^32 − 1 = 4,294,967,295
⌊M / s⌋ = ⌊4,294,967,295 / 16⌋
⌊M / s⌋ = 268,435,455
where
n: the item count (count in the code)
s: the size of one item in bytes, sizeof(item); 16 here
M: SIZE_MAX, the largest value size_t can hold; 2^32 − 1 for a 32-bit size_t
2^32: 32 copies of 2 multiplied together, 4,294,967,296
⌊ ⌋: floor: round down to a whole number; C discards the fractional remainder for the non-negative values used here
≤: less than or equal to
In words: a count is safe only if it is at most SIZE_MAX divided by the item size, rounded down; with 16-byte items that is 268,435,455, so the count 268,435,457 above is rejected.
```

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
