---
id: hash-pattern-frequency
title: Frequency maps and bounded alphabets
level: intermediate
minutes: 3
sourceLesson: hash-patterns
summary: Counting separates the input order from the number of appearances of each key.
---

Counting separates the input order from the number of appearances of each key. When the output depends on the original order, keep the input as well as the counts.

## 2. Frequency maps

Here n is input length, u is the number of distinct keys, and k is how many most-frequent keys are requested; log means a logarithm to any fixed base for Big-O. Count first, then answer questions from the counts.

```python
from collections import Counter

def first_unique(s):
    # Counts give multiplicity; the next
    # pass finds the earliest position.
    counts = Counter(s)
    for i, ch in enumerate(s):
        if counts[ch] == 1:
            return i
    return -1

first_unique("swiss")  # 1 ('w')
```

Two passes over a string of n characters, so O(n) total. Related problems:

- **Is `t` an anagram of `s`?** `Counter(s) == Counter(t)`: O(n), versus O(n log n) for sorting both.
- **Top k frequent elements.** Count in O(n), then `counts.most_common(k)`. With u distinct keys, CPython uses a heap when the requested count is at least two but less than the distinct-key count, `max` when requesting one, and a full sort when requesting every distinct key or more. The cost is at most about O(n + u × log(k + 1)), where log is a logarithm (the heap's height grows like the logarithm of its size, k). Bucketing by frequency gets it to O(n).
- **Majority element.** Count, then find the key that appears in more than half of the n positions (the **Boyer–Moore majority vote** algorithm does it in O(1) space, without a map).

> [!tip] Bounded alphabets
> If keys are lowercase letters only, a list of 26 counters (`counts[ord(c) - 97]`) does the same job with no hashing at all, and its space is O(1) in the size of the input.

## Keep order separately from counts

In the example, Counter first records how often each character appears. It does not identify the first unique position by itself. The second pass visits the original string from left to right and returns the earliest index whose count is one. For swiss, the first s fails, w succeeds at position one, and the function returns immediately. For an empty string or a string with no unique character it reaches the final return and reports minus one.

For anagrams, the count map is the canonical description of how many times every character appears. Equal maps mean equal multiplicities, regardless of order. Decide separately what counts as a character: this sample uses Python Unicode code points. Case-folding, punctuation removal or Unicode normalisation are changes to the problem specification and must be applied consistently before counting.

A fixed array of twenty-six counters is appropriate only when every input character is guaranteed to be a lowercase ASCII letter. Applying the offset expression to spaces, accented letters or uppercase letters breaks that assumption. An unrestricted alphabet needs a more general representation. A frequency map is also different from an ordered result: to return the first occurrence, retain the original sequence or remember positions as well.

## Key takeaways
- Counts record multiplicities, while a second input pass preserves position order.
- Counting and comparing anagram frequencies is linear under the stated hashing assumptions.
- Fixed-alphabet arrays need a guaranteed bounded alphabet.

## Further reading
- [collections: Counter — Python docs](https://docs.python.org/3/library/collections.html#collections.Counter)
- [collections: defaultdict — Python docs](https://docs.python.org/3/library/collections.html#collections.defaultdict)
