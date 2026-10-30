---
id: sort-search-insertion-bounds
title: Insertion bounds, counts and duplicates
level: intermediate
minutes: 3
sourceLesson: sort-binary-search
summary: The lower bound is the first not-less position and the upper bound the first greater position.
---

This unit builds on the preceding search units. Here n is the number of input elements; Big O bounds growth up to a constant factor, and logarithms are base two unless stated otherwise.

### Version 2: lower_bound (half-open interval)

Finding *some* match is often not enough. You want the **first** position where x could go: the **binary-search lower bound** (often called lower_bound), the index of the first element at least as large as the search value. This is what Python's `bisect_left` and C++'s `std::lower_bound` return.

**Invariant:** all elements before `lo` are smaller than the search value, and all elements at or beyond `hi` are at least the search value. The candidate insertion indices include both endpoints, even though the remaining element range excludes `hi`.

```python
def lower_bound(a, x):
    lo, hi = 0, len(a)
    while lo < hi:
        mid = (lo + hi) // 2
        # All keys through mid are too
        # small.
        if a[mid] < x:
            lo = mid + 1   # a[mid] < x
        else:
            # Keep mid as a possible
            # insertion point.
            hi = mid       # a[mid] >= x
    return lo
```

When the endpoints meet, every preceding key is smaller than the search value and every following key is at least that value. That is the answer by definition. Note `hi = len(a)`, not `len(a) - 1`: the answer can be "after everything".

Trace: find lower_bound of 8 in `[1, 3, 5, 7, 9, 11, 13]`.

```
lo hi mid a[mid]
0  7  3   7    7 < 8   -> lo = 4
4  7  5   11   11 >= 8 -> hi = 5
4  5  4   9    9 >= 8  -> hi = 4
lo == hi == 4: insert 8 at index 4
```

The **binary-search upper bound** (upper_bound: the first element > x, `bisect_right`) is identical except the test becomes `a[mid] <= x`.

```
input: [1, 3, 3, 3, 5, 8]
target 3: lower result 1, upper result 4
three copies: 4 - 1 = 3
target 4: both results 4; zero copies
```

> [!analogy] Real-world analogy: shelving another copy of a book
> A library shelf holds three copies of the same title among other books in title order. A new copy could go just before the existing copies or just after them; both keep the shelf in order. The gap between those two spots is exactly the three existing copies.
>
> **How it maps:** "just before the copies" is the binary-search lower bound (the first book not earlier than the title), "just after" is the binary-search upper bound (the first book later than it), and the distance between them counts the equal keys. If the title is not on the shelf, both spots are the same place.
>
> **Where it stops:** on a real shelf you can push books aside to make room. In an array, inserting at the found position still means shifting every later element, so finding the spot is logarithmic but inserting is linear.

lower_bound and upper_bound together answer most real questions: does x exist (`lo < n and a[lo] == x`), how many copies, where to insert while keeping order, and range queries ("all orders between 10:00 and 11:00" is `[lower_bound(10:00), lower_bound(11:00))`).

Java’s `Arrays.binarySearch` returns a match index if present. If absent, its negative result encodes the insertion point: negate the insertion point and subtract one. For `[10, 20, 30, 40]`, searching for 25 has insertion point 2 and returns −3.


For a nearest-value query, inspect the lower-bound position and the position immediately before it, when they exist. One is the first not-less value and the other the largest smaller value, so a closer candidate cannot hide farther away. Return the smaller absolute distance; decide how ties should be broken. A count over a value interval likewise comes from subtracting its two insertion-bound indices, rather than scanning every matching element.

## Key takeaways
- The lower bound is the first not-less position and the upper bound the first greater position.
- Their difference counts equal keys, and insertion positions may be after the entire array.

## Further reading
- [Insertion-bound searches — Python bisect](https://docs.python.org/3/library/bisect.html)
