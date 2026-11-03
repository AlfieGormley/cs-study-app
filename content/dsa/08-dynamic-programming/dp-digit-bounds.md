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

**Complexity**: count the states. For a bound up to 10¹⁸ there are at most 20 positions (including the end), at most 172 possible digit sums (0 to 171) and 2 values of `tight`: a few thousand states (at most 6,880), each trying at most ten digits. Many of those states are unreachable, and exceeding the target digit sum prunes more. Compare that with enumerating up to 10¹⁸ numbers.

Two standard moves:

- **Ranges**: count in [L, R] using the counts up to each end:

```formula reference
count(L, R) = f(R) − f(L − 1)
where
count(L, R): how many integers from L to R inclusive have the property
f(x): how many integers from 0 to x inclusive have the property (f(−1) = 0)
L: the lower end of the range, 0 or more
R: the upper end of the range
In words: count everything from zero up to the upper end, then subtract everything from zero up to one below the lower end; what is left is exactly the range.
```

- **Leading zeros**: if the property cares about them (e.g. "no two adjacent equal digits", where 007 shouldn't count as having adjacent zeros), add a `started` flag to the state.

> [!tip] The intuition
> Once you've placed a digit smaller than N's digit, you're "free": every remaining combination is below N. That's why the `tight=False` states are shared between many prefixes and get cached. `tight=True` is a single path that hugs N.

> [!analogy] Real-world analogy: words that come before "dog" in a dictionary
> To list the three-letter words that come before "dog" alphabetically, look at the first letter. Start with a, b or c and any two letters may follow. Start with d and you are still pinned: the second letter can be at most o, and if it is exactly o, the third letter is pinned too.
>
> **How it maps:** "dog" is the bound N and each letter is a digit. Still matching the bound's letters so far is `tight=True`, so the next letter is capped by the bound's letter. Once you pick a smaller letter, you are free (`tight=False`), and every "free" continuation from the same position looks the same, which is what the cache reuses.
>
> **Where it stops:** a dictionary also lists shorter words, and "do" comes before "dog". Digit DP pads every number to the same length with leading zeros, so it needs a separate `started` flag whenever leading zeros would change the property being counted.

## Key takeaways
- The tight flag records whether the prefix still matches the bound.
- Cache repeated free suffix states instead of enumerating every integer.
- Subtract prefix counts for ranges and track leading-zero state when needed.

## Further reading
- [Digit DP](https://usaco.guide/gold/digit-dp)
- [Python caching](https://docs.python.org/3/library/functools.html)
