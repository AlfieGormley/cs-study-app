---
id: hash-pattern-canonical-key
title: Grouping by a hashable canonical key
level: intermediate
minutes: 3
sourceLesson: hash-patterns
summary: A grouping key should be identical exactly for items you intend to group together.
---

A grouping key should be identical exactly for items you intend to group together. Hashability is necessary for storing the key, but it does not by itself make the chosen grouping rule correct.

## 3. Grouping by a canonical key

> Group words that are anagrams of each other.

Map each item to a **canonical key** that is identical for everything in the same group, then use a `defaultdict(list)`.

```python
from collections import defaultdict

def group_anagrams(words):
    groups = defaultdict(list)
    for w in words:
        # Same letters and counts, same key.
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

The cost depends on how you build the key. For n words of up to k letters, sorting each word's letters costs about k log k steps per word, while counting its letters into 26 slots costs about k. So the counting key is asymptotically cheaper: O(nk) rather than O(nk log k). Big-O hides constant factors, though, and for short words the sorted tuple is often just as fast in practice; the difference matters for long strings, and timings need measuring.

## Test the key against the grouping rule

The words eat and tea yield the same sorted-letter tuple, while tan yields a different tuple. A tuple can be hashed because these character elements are hashable. A list from sorted cannot be a dictionary key. Converting the list to a tuple fixes the representation without changing the sorted-letter rule.

For a lowercase-only alphabet, a tuple of twenty-six counts is another canonical key. It ignores order while preserving multiplicity: two copies of a letter must not be treated as one. A set of letters would incorrectly merge words that have the same distinct letters but different counts.

The table’s shifted-string example includes length deliberately. Adjacent gaps alone give an empty sequence for every single-character string and for an empty string; length distinguishes those cases. Always check empty inputs, repeated characters and different lengths before trusting a proposed canonical key. A key with avoidable collisions at the semantic level creates wrong groups even if the hash table resolves its internal hash collisions correctly.

## Key takeaways
- A canonical key must encode precisely the intended equivalence.
- Use hashable tuples rather than lists as map keys.
- Key construction can dominate the hash lookup cost.

## Further reading
- [collections: Counter — Python docs](https://docs.python.org/3/library/collections.html#collections.Counter)
- [collections: defaultdict — Python docs](https://docs.python.org/3/library/collections.html#collections.defaultdict)
