---
id: lin-array-geometric-growth
title: Why geometric growth amortises copying
level: basic
minutes: 4
sourceLesson: lin-arrays
summary: Multiply capacity by a constant factor greater than one to bound total copying.
---

A dynamic array distinguishes its live length from its backing capacity. When a full array grows, the old elements must be copied into the new block. This unit counts that copying across a long run of appends; allocation costs and allocator-specific in-place growth are outside the model.

### Why growth must be geometric

Copying n elements is O(n) work, so you might expect appends to be slow. The trick is *how much* to grow. To compare growth policies, count the total number of element copies that resizing makes while you append n elements one at a time.

If capacity **doubles** each time, starting from capacity 1, the resizes copy 1, then 2, then 4, and so on, each resize copying the whole old array. Every resize copies one more element than all the earlier resizes put together, so the grand total stays just under the final capacity:

```formula reference
copies = 1 + 2 + 4 + ... + C / 2
copies = C − 1
copies < 2n
where
copies: the total number of element copies made by all the resizes together
C: the final capacity, the smallest power of two that is at least n
n: the positive number of elements appended, at least one
In words: each resize copies as many elements as all the earlier resizes put together, plus one, so the grand total is always just under the final capacity, which is less than twice the number of elements.
```

For example, 17 appends end at capacity 32 after 31 copies, fewer than two per append. Spread over n appends, that is fewer than two copies per append: **amortised O(1)**. *Amortised* means averaged over a long run of operations: an occasional append is expensive, but the total for n appends is still proportional to n.

### Any constant factor works; the factor sets the trade-off

Growing by any constant factor greater than 1 works. Going backwards from the last resize, each earlier resize copied a fixed fraction as many elements as the one after it, so the copies form a shrinking **geometric series** whose total is a constant multiple of the final capacity.

```formula reference
copies ≈ C / (r − 1)
where
copies: the total number of element copies made by all the resizes together
C: the final capacity
r: the growth factor: each resize multiplies the capacity by r, which must be greater than 1 (2 means doubling, 1.5 means grow by half)
≈: approximately equal to; integer rounding and the small starting capacity are ignored
In words: total copying is a fixed multiple of the final capacity. The closer the growth factor is to 1, the larger that multiple: doubling copies about one element per final slot, growing by half copies about two.
```

The copy counts in the table describe the moment the array has just filled its final capacity. Just after a resize, the capacity can instead approach the growth factor times the live length, so the copies per live item are higher; that is also when the most capacity sits empty, as the last column shows.

| Growth factor | Copies per final item | Most capacity left empty |
|---|---|---|
| 2 | about one | about a half |
| 1.5 | about two | about a third |
| 1.125 | about eight | about a ninth |

Every factor gives a total proportional to n, so append stays amortised O(1). The choice is a trade-off: a smaller factor wastes less memory just after growing but pays a larger copying constant.

### Fixed increments fail

Growing by a constant *amount* (say +10 slots) does not work. A resize now happens every ten appends, and each one copies everything stored so far, so the copies form an **arithmetic series** that grows with the square of n:

```formula reference
copies ≈ n^2 / (2c)
where
copies: the total number of element copies made by all the resizes together
n: the positive number of elements appended, at least one
c: the fixed number of slots added at each resize, e.g. 10
≈: approximately equal to; small end effects are ignored
In words: adding a fixed number of slots means a resize every few appends, and each one copies everything so far, so total copying grows with the square of the number of appends. A bigger fixed step only divides that total by a constant.
```

With ten-slot increments and a million appends, that is about fifty billion copies, against about a million for doubling. That is O(n²), **quadratic** time.

> [!warning] Amortised is not worst case
> An individual append that triggers a resize is O(n). If you append to a 10-million-element vector in a latency-sensitive loop, that one append copies 10 million elements. When you know the final size, reserve it up front.

## Key takeaways
- Multiply capacity by a constant factor greater than one to bound total copying.
- A smaller factor trades extra copying for less empty capacity; a fixed increment makes total copying quadratic.

## Further reading
- [Dynamic array — Wikipedia](https://en.wikipedia.org/wiki/Dynamic_array)
