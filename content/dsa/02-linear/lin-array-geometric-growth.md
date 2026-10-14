---
id: lin-array-geometric-growth
title: Why geometric growth amortises copying
level: basic
minutes: 5
sourceLesson: lin-arrays
summary: Multiply capacity by a constant factor greater than one to bound total copying.
---

A dynamic array distinguishes its live length from its backing capacity. When a full array grows, old elements may need copying. This unit counts that copying across a sequence of appends; allocation costs and allocator-specific in-place growth are outside the model.

### Why growth must be geometric

Copying n elements is O(n) work, so you might expect appends to be slow. The trick is *how much* to grow. To compare growth policies, count the total number of element copies that resizing makes while you append n elements one at a time.

If capacity **doubles** each time, starting from capacity 1, the resizes copy 1, then 2, then 4, and so on, each resize copying the whole old array:

```formula
copies = 1 + 2 + 4 + ... + C / 2
copies = C − 1
copies < 2n
where
copies: the total number of element copies made by all the resizes together
C: the final capacity, the smallest power of two that is at least n
n: the positive number of elements appended, at least one
In words: each resize copies as many elements as all the earlier resizes put together, plus one, so the grand total is always just under the final capacity, which is less than twice the number of elements.
```

For example, 17 appends end at capacity 32 after copying 1 + 2 + 4 + 8 + 16 = 31 elements, fewer than 2 × 17 = 34. Spread over n appends, that is fewer than two copies per append: **amortised O(1)**. *Amortised* means averaged over a long run of operations: an occasional append is expensive, but the total for n appends is still proportional to n.

Growing by any constant factor greater than 1 works. Going backwards from the last resize, each earlier resize copied 1/r as many elements as the one after it, so the copies form a shrinking **geometric series**:

```formula
copies ≈ C / r + C / r^2 + C / r^3 + ...
copies ≈ C / (r − 1)
where
copies: the total number of element copies made by all the resizes together
C: the final capacity
r: the growth factor: each resize multiplies the capacity by r, which must be greater than 1 (2 means doubling, 1.5 means grow by half)
≈: approximately equal to; integer rounding and the small starting capacity are ignored
In words: the total copying is the final capacity divided by (growth factor − 1). A factor close to 1 grows gently, saving memory, but copies more in total.
```

The series is stated in terms of final capacity, not arbitrary stopping length. At a full-capacity endpoint:

```formula
C = n
copies ≈ n / (r − 1)
where
C: final capacity, in element slots
n: appended element count
r: fixed geometric growth factor, greater than one
copies: copied element count during resizing
≈: approximate equality ignoring rounding and the initial capacity
In words: When all final slots are filled, the capacity and live length agree.
```

Just after a resize, the final capacity can instead approach the growth factor times the live length. The table describes full-capacity endpoints:

| Growth factor | Copies when n fills final capacity |
|---|---|
| 2 | about one copy per final item |
| 1.5 | about two copies per final item |
| 1.125 | about eight copies per final item |

For instance, with factor 1.5 and a million elements: 1,000,000 / (1.5 − 1) = 2,000,000 copies. Every factor gives a total proportional to n, so append stays amortised O(1); smaller factors just pay a larger constant.

Growing by a constant *amount* (say +10 slots) does not work. Each resize now copies only 10 more elements than the last, so the copies form an **arithmetic series** whose total grows with the square of n:

```formula
resizes ≈ n / c
copies ≈ c + 2c + ... + n
copies ≈ n^2 / (2c)
where
resizes: how many times the array has to grow
copies: the total number of element copies made by all the resizes together
n: the positive number of elements appended, at least one
c: the fixed number of slots added at each resize, e.g. 10
≈: approximately equal to; small end effects are ignored
In words: adding a fixed number of slots means a resize every c appends, and each one copies everything so far, so total copying grows with n squared.
```

With ten-slot increments and a million appends, the approximation gives fifty billion copies, against about a million for doubling. That is O(n²), **quadratic** time.

> [!warning] Amortised is not worst case
> An individual append that triggers a resize is O(n). If you append to a 10-million-element vector in a latency-sensitive loop, that one append copies 10 million elements. When you know the final size, reserve it up front.

## Key takeaways
- Multiply capacity by a constant factor greater than one to bound total copying.
- Distinguish a full-capacity endpoint from stopping just after a resize.

## Further reading
- [Dynamic array — Wikipedia](https://en.wikipedia.org/wiki/Dynamic_array)
