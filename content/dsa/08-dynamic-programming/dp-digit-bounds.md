---
id: dp-digit-bounds
title: Count digit properties below a bound
level: advanced
minutes: 4
summary: The tight flag records whether the prefix still matches the bound.
sourceLesson: dp-advanced
---

## Digit DP

> How many integers in [0, N] have digits summing to k? (Or contain no "4", or have no two equal adjacent digits, ...) N can be up to 10¹⁸.

Enumerating every integer up to a bound of 10¹⁸ is impractical. Instead, build the number **digit by digit from the left** and count how many completions satisfy the property.

**State**: `(pos, acc, tight)`

- `pos`: which digit we're placing.
- `acc`: whatever the property needs to remember (here, the digit sum so far).
- `tight`: whether every digit so far has equalled N's digit. If so, the next digit can be at most N's digit at this position; otherwise any digit 0–9 is allowed.

```python
from functools import cache

def count_digit_sum(N, k):
    if (type(N) is not int
            or type(k) is not int):
        raise ValueError("integer bounds")
    if N < 0 or k < 0:
        return 0
    # Work with the bound's decimal digits.
    digits = list(map(int, str(N)))

    # Repeated arguments reuse stored
    # answers.
    @cache
    def go(pos, s, tight):
        # Nonnegative digits cannot lower
        # the sum.
        if s > k:
            return 0
        # Count only a complete matching
        # digit sum.
        if pos == len(digits):
            return 1 if s == k else 0
        # A matching prefix must respect the
        # bound.
        limit = digits[pos] if tight else 9
        return sum(
            go(pos + 1, s + d,
               tight and d == limit)
            for d in range(limit + 1))

    return go(0, 0, True)
```

`count_digit_sum(100, 5)` is 6 (5, 14, 23, 32, 41, 50). `count_digit_sum(2024, 10)` is 120.

**Complexity**: count the states:

```formula
states = positions × sums × 2
states ≤ 20 × 172 × 2 = 6,880
work ≤ states × 10 = 68,800
where
states: the number of possible (pos, s, tight) combinations; the factor 2 is the two values of tight, True and False
positions: digit positions, at most 19 for N ≤ 10^18, plus 1 for the end, so 20
sums: possible digit sums so far, 0 to 9 × 19 = 171, so 172 values
work: an upper bound on digit choices tried, 10 per state (digits 0 to 9)
N: the upper limit of the range being counted
≤: at most
In words: the memo table has one entry per position, running sum and tight flag, and each entry tries at most ten digits.
```

Many of those states are unreachable, and exceeding the target digit sum prunes more. Exact counts may require growing integers.

> [!note] Content gap
> The original microsecond running-time prediction is omitted because no reproducible benchmark supports it.

Two standard moves:

- **Ranges**: count in [L, R] using the counts up to each end:

```formula
count(L, R) = f(R) − f(L − 1)
where
count(L, R): how many integers from L to R inclusive have the property
f(x): how many integers from 0 to x inclusive have the property (f(−1) = 0)
L: the lower end of the range, 0 or more
R: the upper end of the range
In words: everything up to R, minus everything below L, leaves exactly the numbers from L to R.
```

- **Leading zeros**: if the property cares about them (e.g. "no two adjacent equal digits", where 007 shouldn't count as having adjacent zeros), add a `started` flag to the state.

> [!tip] The intuition
> Once you've placed a digit smaller than N's digit, you're "free": every remaining combination is below N. That's why the `tight=False` states are shared between many prefixes and get cached. `tight=True` is a single path that hugs N.

## Key takeaways
- The tight flag records whether the prefix still matches the bound.
- Cache repeated free suffix states instead of enumerating every integer.
- Subtract prefix counts for ranges and track leading-zero state when needed.

## Further reading
- [Digit DP](https://usaco.guide/gold/digit-dp)
- [Python caching](https://docs.python.org/3/library/functools.html)
