---
id: hash-pattern-complement
title: Two-sum and complement lookup
level: intermediate
minutes: 3
sourceLesson: hash-patterns
summary: Keep the map invariant explicit: it contains only earlier input positions.
---

Keep the map invariant explicit: it contains only earlier input positions. That makes the one-pass lookup both fast and safe when the target can be twice the current value.

Many problems that look like they need two nested loops have an O(n) solution (n being the length of the input) that walks the input once while a hash map remembers what it has seen. The pattern is always the same trade: spend O(n) memory to turn "search everything I've seen so far" (O(n) each time) into "look it up" (O(1) on average).

Complexity below assumes expected constant-time hash operations and bounded-cost arithmetic/equality; Python arbitrary-size integers can add bit costs. The next units cover the remaining recurring shapes. Recognising what the map remembers is more useful than memorising a particular loop.



## 1. Complement lookup: two-sum

> Given `nums` and `target`, return the indices of two numbers that add up to `target`.

A brute-force search checks every pair: O(n²) for an array of n numbers. The insight: for each number, the partner you need is fixed:

```formula
y = T − x
y = 9 − 2 = 7
where
y: the complement, the value that would pair with x to reach the target
T: the target sum (`target` in the code), here 9
x: the current number (`x` in the code), here 2
In words: if the target is 9 and you are looking at 2, the only number that can complete the pair is 7, so you need one lookup, not a search.
```

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
