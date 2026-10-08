---
id: hash-patterns
title: Hashing patterns for problems
level: intermediate
minutes: 13
summary: The hash map patterns behind a large share of coding problems: complement lookup (two-sum), frequency maps, grouping by a canonical key, prefix sums with a map, and sliding windows that track counts.
---

Many problems that look like they need two nested loops have an O(n) solution (n being the length of the input) that walks the input once while a hash map remembers what it has seen. The pattern is always the same trade: spend O(n) memory to turn "search everything I've seen so far" (O(n) each time) into "look it up" (O(1) on average).

Complexity below assumes expected constant-time hash operations and bounded-cost arithmetic/equality; Python arbitrary-size integers can add bit costs. This lesson covers five recurring shapes. Learn to recognise them and a large share of array and string problems become routine.

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
        seen[x] = i
    return None

two_sum([2, 7, 11, 15], 9)  # (0, 1)
two_sum([3, 3], 6)          # (0, 1)
```

Two details matter:

- **Check before you insert.** With `[3, 2, 4]` and target 6, inserting first would let `3` match itself. Checking first means `seen` only ever contains *earlier* elements.
- **Duplicates are fine.** For `[3, 3]`, the first 3 is stored; the second finds it.

Time O(n), space O(n). If the array is already sorted, two pointers from both ends solve it in O(1) extra space, which is the usual follow-up question.

The same "have I seen the complement?" shape solves: pairs with a given difference (look up `x − k` and `x + k`), "does any duplicate exist?" (complement is `x` itself), and "duplicate within distance k" (store each value's last index).

## 2. Frequency maps

Count first, then answer questions from the counts.

```python
from collections import Counter

def first_unique(s):
    counts = Counter(s)
    for i, ch in enumerate(s):
        if counts[ch] == 1:
            return i
    return -1

first_unique("swiss")  # 1 ('w')
```

Two passes over a string of n characters, so O(n) total. Related problems:

- **Is `t` an anagram of `s`?** `Counter(s) == Counter(t)`: O(n), versus O(n log n) for sorting both.
- **Top k frequent elements.** Count in O(n), then `counts.most_common(k)`. With u distinct keys, CPython uses a heap when k is between 2 and u − 1, `max` when k = 1, and a full sort when k is u or more. The cost is at most about O(n + u × log(k + 1)), where log is a logarithm (the heap's height grows like the logarithm of its size, k). Bucketing by frequency gets it to O(n).
- **Majority element.** Count, then find the key that appears in more than half of the n positions (the **Boyer–Moore majority vote** algorithm does it in O(1) space, without a map).

> [!tip] Bounded alphabets
> If keys are lowercase letters only, a list of 26 counters (`counts[ord(c) - 97]`) does the same job with no hashing at all, and its space is O(1) in the size of the input.

## 3. Grouping by a canonical key

> Group words that are anagrams of each other.

Map each item to a **canonical key** that is identical for everything in the same group, then use a `defaultdict(list)`.

```python
from collections import defaultdict

def group_anagrams(words):
    groups = defaultdict(list)
    for w in words:
        key = tuple(sorted(w))
        groups[key].append(w)
    return list(groups.values())

words = ["eat", "tea", "tan",
         "ate", "nat", "bat"]
group_anagrams(words)
# [['eat', 'tea', 'ate'],
#  ['tan', 'nat'], ['bat']]
```

Choosing the key is the whole problem:

| Group by | Key |
|---|---|
| Anagram | sorted letters, or 26 counts |
| Same digits | sorted digit string |
| Shifted lowercase strings (abc, bcd) | length plus adjacent gaps modulo 26 |
| Same row in a grid | the row index |

The key must be hashable, which is why it is `tuple(sorted(w))` rather than `sorted(w)` (a list).

The cost depends on how you build the key. Sorting each word's letters costs more than counting them:

```formula
T_sort = O(n + n × k × log(k + 1))
T_count = O(n × (k + 1))
where
T_sort: the running time with sorted-letter keys
T_count: the running time with 26-count keys (lowercase letters only)
O(…): Big-O, the growth rate of the cost, ignoring constant factors
n: the number of words
k: the length of the longest word, in characters
log: logarithm (any fixed base, since Big-O ignores the constant); log_2(9) ≈ 3.2
In words: sorting a word of k letters costs about k × log k steps, while counting its letters costs about k; the "+ 1" terms only make the formulas correct for empty words.
```

For example, 1,000 words of 8 letters cost on the order of 1,000 × 8 × 3.2 ≈ 25,000 steps with sorting and 9,000 with counting. Big-O hides constant factors, so for short words the difference in real time is small; it matters for long strings.

## 4. Prefix sum plus hash map

> Count the subarrays of `nums` whose sum equals `k`. Values may be negative.

A **prefix sum** is a running total: the sum of the first so-many elements. The sum of any contiguous stretch is then the difference of two prefix sums, so we want pairs of positions i < j with

```formula
P[j] − P[i] = k
⇒ P[i] = P[j] − k
P[2] − P[0] = 3 − 0 = 3
where
P[j]: the prefix sum, the total of the first j elements of nums (P[0] = 0, the empty prefix)
i: the start index of the subarray, counting from 0
j: one past the end index, so the subarray is nums[i] up to nums[j − 1]
k: the target sum
⇒: "which means"; rearranging the first line gives the second
In words: the subarray from i to j − 1 sums to k exactly when an earlier running total equals the current running total minus k; for nums = [1, 2, 1, −1, 2], P = [0, 1, 3, 4, 3, 5], and P[2] − P[0] = 3 is the subarray [1, 2].
```

That is two-sum again, on prefix sums. Walk once, keeping a count of each prefix sum seen so far:

```python
def count_subarrays(nums, k):
    count = p = 0
    seen = {0: 1}  # prefix sum -> times
    for x in nums:
        p += x
        count += seen.get(p - k, 0)
        seen[p] = seen.get(p, 0) + 1
    return count
```

Trace `nums = [1, 2, 1, -1, 2]`, `k = 3`:

```
x   p   need p-3  found  count
1   1   -2        0      0
2   3    0        1      1
1   4    1        1      2
-1  3    0        1      3
2   5    2        0      3
```

The answer is 3: `[1, 2]`, `[2, 1]` and `[1, 2, 1, -1]`.

The **`{0: 1}` seed** represents the empty prefix before the array starts. Without it, subarrays that begin at index 0 (like `[1, 2]`) are missed.

Variants:

- **Longest subarray with sum k**: store the *first* index at which each prefix sum appears, and maximise `j − first[p − k]`.
- **Subarray sum divisible by k**: for nonzero k, key on `p % k` (the remainder, written mod below); two prefixes with equal remainders bound a divisible subarray.
- **Equal numbers of 0s and 1s**: map 0 to −1, then look for subarrays with sum 0.

The divisible-by-k variant rests on one fact about remainders:

```formula
(P[j] − P[i]) mod k = 0
⇔ P[j] mod k = P[i] mod k
(13 − 3) mod 5 = 10 mod 5 = 0
13 mod 5 = 3 mod 5 = 3
where
P[j]: the prefix sum of the first j elements
P[i]: an earlier prefix sum, i < j
k: the divisor, a nonzero integer; here 5
mod: "modulo", the remainder after division, taken from 0 to k − 1
⇔: "exactly when", the statements on either side are both true or both false
In words: a difference is divisible by k exactly when the two numbers leave the same remainder; prefix sums 13 and 3 both leave 3 when divided by 5, so the stretch between them sums to 10, a multiple of 5.
```

So count, for each remainder, how many earlier prefixes had it. (Some languages return negative remainders for negative numbers, so normalise them first.)

> [!warning] Why not a sliding window?
> The usual sum-based two-pointer rule relies on monotonicity, as with nonnegative inputs. Counting all matching windows also needs care with zeros. Arbitrary mixed signs break that monotonicity; prefix sums with a map handle them.

## 5. Sliding window with a map

When the question is about a **contiguous** substring or subarray and a condition on its contents ("no repeats", "at most k distinct", "contains all of these"), move a window `[left, right]` along the input and keep a map describing what is inside it.

### Longest substring without repeating characters

Store each character's last index. When you meet a character already inside the window, jump the left edge past its previous occurrence.

```python
def longest_unique(s):
    last = {}  # char -> last index
    start = best = 0
    for i, ch in enumerate(s):
        if last.get(ch, -1) >= start:
            start = last[ch] + 1
        last[ch] = i
        best = max(best, i - start + 1)
    return best

longest_unique("abcabcbb")  # 3 ("abc")
longest_unique("abba")      # 2
```

The `>= start` check matters. In `"abba"`, when the final `a` arrives, its last index (0) is to the left of the current window (which starts at 2, after the second `b`). Without the check, `start` would jump *backwards* to 1 and the answer would wrongly be 3.

### Longest substring with at most k distinct characters

Here the map holds counts of characters in the window, and its size is the number of distinct characters.

```python
def longest_k_distinct(s, k):
    if type(k) is not int or k < 0:
        raise ValueError("nonnegative k")
    counts = {}
    left = best = 0
    for right, ch in enumerate(s):
        counts[ch] = counts.get(ch, 0) + 1
        while len(counts) > k:
            out = s[left]
            counts[out] -= 1
            if counts[out] == 0:
                del counts[out]
            left += 1
        best = max(best, right - left + 1)
    return best

longest_k_distinct("eceba", 2)  # 3 ("ece")
```

Deleting keys whose count hits zero is essential: otherwise `len(counts)` overstates the number of distinct characters. Each character enters and leaves the window at most once, so for a string of n characters the inner `while` loop does O(n) work in total, not per step. Total: O(n).

The same skeleton solves "minimum window containing all characters of t" (track how many required characters are satisfied) and "find all anagrams of p in s" (a fixed-size window compared with `Counter(p)`).

## Sets for O(1) membership

Sometimes all you need is fast membership. **Longest consecutive sequence** (`[100, 4, 200, 1, 3, 2]` → 4, for 1, 2, 3, 4) looks like it needs sorting, O(n log n) for n numbers. With a set it is O(n):

```python
def longest_consecutive(nums):
    s = set(nums)
    best = 0
    for x in s:
        if x - 1 not in s:  # x starts a run
            y = x
            while y + 1 in s:
                y += 1
            best = max(best, y - x + 1)
    return best
```

The `x − 1 not in s` test means each run is walked only from its start, so every element is visited a constant number of times.

## Recognising the pattern

| Clue in the problem | Pattern |
|---|---|
| "two elements that sum to" | complement lookup |
| "how many times", "most frequent" | frequency map |
| "group", "anagrams", "same pattern" | canonical key |
| "subarray sum", negatives allowed | prefix sum + map |
| "longest/shortest substring with" | sliding window + map |

> [!note] The cost
> Every pattern here trades O(n) extra memory for speed, and every O(1) is the *average* case. In an interview, say so; on a real system with adversarial input, remember lesson 2.

## Key takeaways
- The core move: replace "search what I've seen" with "look it up in a map", turning O(n²) into O(n) for n input items, at the cost of O(n) space.
- Two-sum: check for `target − x` before inserting `x`, so an element never pairs with itself.
- Grouping: pick a hashable canonical key (sorted letters, a count tuple) that is identical within a group.
- Subarray sum equals k: count prefix sums in a map seeded with `{0: 1}`; it works with negative numbers where sliding windows do not.
- Sliding windows keep a map of the window's contents; delete zero-count keys and guard against moving the left edge backwards.

## Further reading
- [Prefix sum — Wikipedia](https://en.wikipedia.org/wiki/Prefix_sum)
- [collections: Counter — Python docs](https://docs.python.org/3/library/collections.html#collections.Counter)
- [collections: defaultdict — Python docs](https://docs.python.org/3/library/collections.html#collections.defaultdict)
- [Time complexity of Python operations — Python wiki](https://wiki.python.org/moin/TimeComplexity)
- [Hash table — Wikipedia](https://en.wikipedia.org/wiki/Hash_table)
