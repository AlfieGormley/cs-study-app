---
id: sort-selection-hybrid-fallback
title: Selection fallbacks and library guarantees
level: advanced
minutes: 2
sourceLesson: sort-selection
summary: Introselect needs a work budget and an appropriate fallback for its claimed worst-case bound.
---

This unit builds on the preceding sorting units. Here n is the number of input elements; Big O bounds growth up to a constant factor, and logarithms are base two unless stated otherwise.

### Practical costs and hybrids

The constant factor is large: sorting every group of 5, the extra recursive call and the partition add up to extra work compared with classical randomized selection; exact constants depend on the implementation, and the list-building version above also allocates heavily. So in practice median of medians is a **fallback**, not a default:

- **Introselect** (Musser, 1997) runs quickselect, and if it is not shrinking the range fast enough, switches to a fallback. A carefully budgeted linear-time fallback gives a linear worst-case bound; a heap fallback may give O(n log n). C++ requires only average linear complexity for ordinary std::nth_element and does not mandate an algorithm. NumPy documents O(n) worst-case introselect.
- **Floyd–Rivest** (1975) picks the pivot from a small random sample and achieves the expected comparison count below, close to the theoretical optimum. It is used for large in-memory selection.

```formula
C ≈ n + min(k, n − k)
C ≈ 10^6 + 5 × 10^5 = 1.5 × 10^6
where
C: the expected comparisons Floyd–Rivest makes (lower-order terms dropped)
n: the number of elements; a million (10^6) here
k: the rank wanted (0-based); the median, k = 500,000, here
min: the smaller of its two inputs
10^6: ten to the power 6, a million; 5 × 10^5 is half a million
≈: approximately equal to
In words: one look at every element, plus extra work proportional to the distance from the nearer end, so the median costs about 1.5 comparisons per element.
```

NumPy’s `partition` puts the requested rank in its sorted position. Values before it are no larger and values after it no smaller, but neither side is fully sorted. The function returns a partitioned copy; an ndarray’s in-place `partition` method has a different mutation contract.


## Key takeaways
- Introselect needs a work budget and an appropriate fallback for its claimed worst-case bound.
- The C++ and NumPy selection APIs promise different complexity contracts.

## Further reading
- [Partition guarantees — NumPy documentation](https://numpy.org/doc/stable/reference/generated/numpy.partition.html)
- [nth_element — C++ working draft](https://eel.is/c++draft/alg.nth.element)
- [Expected time bounds for selection — Floyd and Rivest](https://people.csail.mit.edu/rivest/pubs/FR75a.pdf)
