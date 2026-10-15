---
id: dp-lis-ending-states
title: Increasing subsequences by ending position
level: intermediate
minutes: 3
summary: Fixing the end position supplies the value needed to extend a subsequence.
sourceLesson: dp-1d
---

## Longest increasing subsequence

> Find the length of the longest strictly increasing subsequence (not necessarily next to each other).

For `[10, 9, 2, 5, 3, 7, 101, 18]`, one LIS is `[2, 3, 7, 18]`, length 4.

### A quadratic DP over end positions

- **State**: `L[i]` records length of the longest increasing subsequence **ending at** index i.
- **Recurrence**: the element before `a[i]` is some earlier `a[j] < a[i]`, or there is none and `a[i]` stands alone.
- **Answer**: `max(L)`, not `L[n-1]`, because the LIS can end anywhere.

```formula
L[i] = 1 + max(0, L[j] for j < i
         with a[j] < a[i])
answer = max(L[0], ..., L[n − 1])
where
L[i]: the length of the longest strictly increasing subsequence that ends with element i
i: an index into the array, 0 to n − 1
j: an earlier index, smaller than i
a[i]: the element at index i
max: the largest of the listed values; the 0 covers the case where no earlier element is smaller
answer: the length of the longest increasing subsequence anywhere in the array
n: the number of elements in the array
In words: element i either starts a new subsequence of length 1, or extends the longest subsequence ending at a smaller, earlier element.
```

For the input `[10, 9, 2, 5, 3, 7]`, the final value 7 can follow the earlier values 2, 5 or 3. Their ending lengths are 1, 2 and 2:

```formula
L[5] = 1 + max(1, 2, 2) = 3
where
L[i]: the longest strictly increasing subsequence ending at zero-based index i
i: an input position; here position five holds the value seven
max: the largest listed value
In words: Append seven to a best earlier subsequence of length two, making length three.
```

```python
def lis_quadratic(a):
    # Each element alone is a subsequence.
    L = [1] * len(a)
    for i in range(len(a)):
        for j in range(i):
            # Extend only a smaller earlier
            # value.
            if a[j] < a[i]:
                L[i] = max(L[i], L[j] + 1)
    return max(L, default=0)
```

For the example, `L = [1, 1, 1, 2, 2, 3, 4, 4]`, so the answer is 4.

"Ending at i" is a common trick: "the best subsequence in `a[:i]`" doesn't give you a usable recurrence, because you need to know the last element to decide whether `a[i]` can extend it. Fixing the end fixes that.

To reconstruct, store `parent[i] = j` for the j that gave the best value and follow parents back from the argmax.

## Key takeaways
- Fixing the end position supplies the value needed to extend a subsequence.
- The best subsequence can end anywhere.
- Parent links can reconstruct the chosen subsequence.

## Further reading
- [Python bisect](https://docs.python.org/3/library/bisect.html)
- [Longest increasing subsequence](https://cp-algorithms.com/sequences/longest_increasing_subsequence.html)
