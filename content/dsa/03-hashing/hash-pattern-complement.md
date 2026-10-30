---
id: hash-pattern-complement
title: Two-sum and complement lookup
level: intermediate
minutes: 3
sourceLesson: hash-patterns
summary: For each number, look up the one partner that completes the target in a map of earlier values, turning a quadratic pair search into one pass.
---

Many problems that look like they need two nested loops have an O(n) solution (n being the length of the input) that walks the input once while a hash map remembers what it has seen. The trade is always the same: spend O(n) memory to turn "search everything I've seen so far" (O(n) each time) into "look it up" (O(1) on average).

These bounds assume expected constant-time hash operations and bounded-cost arithmetic and equality. The units that follow cover the other recurring shapes; recognising *what the map remembers* matters more than memorising a particular loop.

## 1. Complement lookup: two-sum

> Given `nums` and `target`, return the indices of two numbers that add up to `target`.

A brute-force search checks every pair: O(n²) for an array of n numbers. The insight: for each number, the partner you need is fixed. It is the target minus the current number, its complement. If the target is 9 and you are looking at 2, only a 7 can complete the pair, so you need one lookup, not a search.

Instead of searching for the complement, ask a map whether you have already seen it.

```python
def two_sum(nums, target):
    seen = {}  # value -> index
    for i, x in enumerate(nums):
        if target - x in seen:
            return seen[target - x], i
        # Store after checking: no
        # self-pair.
        seen[x] = i
    return None

two_sum([2, 7, 11, 15], 9)  # (0, 1)
two_sum([3, 3], 6)          # (0, 1)
```

Two details matter:

- **Check before you insert.** With `[3, 2, 4]` and target 6, inserting first would let `3` match itself. Checking first means `seen` only ever contains *earlier* elements.
- **Duplicates are fine.** For `[3, 3]`, the first 3 is stored; the second finds it.

Time O(n), space O(n). If the array is already sorted, two pointers from both ends solve it in O(1) extra space, which is the usual follow-up question.

The same "have I seen the complement?" shape solves: pairs with a given difference (look up `x - k` and `x + k`), "does any duplicate exist?" (complement is `x` itself), and "duplicate within distance k" (store each value's last index).

## Key takeaways
- Check the complement before recording the current value.
- The map must contain only earlier input indices.
- Duplicates can form a pair when they occur at distinct positions.

## Further reading
- [Time complexity of Python operations — Python wiki](https://wiki.python.org/moin/TimeComplexity)
- [Hash table — Wikipedia](https://en.wikipedia.org/wiki/Hash_table)
