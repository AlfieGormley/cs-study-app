---
id: dp-word-break
title: Word break with reconstruction
level: basic
minutes: 5
summary: A suffix state decides whether the rest of the string can be split.
sourceLesson: dp-method
---

## Worked example 1: word break

> Given a string `s` and nonempty dictionary words, can `s` be split into a sequence of dictionary words? If so, return one split.

**State.** `ok[i]` is True if the suffix `s[i:]` can be split into words.

**Recurrence.** The first decision is which word starts at position i. The suffix from i can be split if some dictionary word matches exactly at i **and** the rest after that word can also be split. In Python:

```python
ok[i] = any(s.startswith(w, i)
            and ok[i + len(w)]
            for w in words)
```

**Base case.** `ok[n] = True`: the empty suffix is trivially split (into zero words).

**Order.** `ok[i]` depends on larger indices, so loop `i` from the final character index down to zero.

**Answer.** `ok[0]`. To reconstruct, store `nxt[i]`, the end of the word chosen at i.

```python
def word_break(s, words):
    # Reuse the same word collection each
    # pass.
    words = tuple(words)
    if any(not isinstance(w, str) or not w
           for w in words):
        raise ValueError("nonempty words")
    n = len(s)
    ok = [False] * (n + 1)
    nxt = [None] * (n + 1)
    # The empty suffix needs no words.
    ok[n] = True
    # Larger suffix positions are ready
    # first.
    for i in range(n - 1, -1, -1):
        for w in words:
            j = i + len(w)
            # Match one word and a
            # splittable suffix.
            if s.startswith(w, i) and ok[j]:
                # Save the successful next
                # boundary.
                ok[i], nxt[i] = True, j
                break
    # No full split exists from the
    # beginning.
    if not ok[0]:
        return None
    out, i = [], 0
    while i < n:
        # Recover the stored word choice.
        out.append(s[i:nxt[i]])
        i = nxt[i]
    return out
```

Trace `s = "catsanddog"`, words `["cat", "cats", "and", "sand", "dog"]`:

```
i  suffix       ok   via
10 ""           T    base
7  "dog"        T    dog -> 10
6  "ddog"       F
4  "anddog"     T    and -> 7
3  "sanddog"    T    sand -> 7
0  "catsanddog" T    cat -> 3
```

(Positions 1, 2, 5, 8 and 9 are False.) Following `nxt[i]` from position zero gives `["cat", "sand", "dog"]`. With "cats" listed first you'd get `["cats", "and", "dog"]`; both are valid.

**Complexity.** Count states and the work per state. Let n be the string length, W the number of dictionary words and L the longest word's length. There are n + 1 states; each tries all W words, and each `startswith` check compares up to L characters. So the work is O(nWL), with O(n + W) extra memory. A 1,000-character string with 500 words of up to 10 characters needs at most about 5 million character comparisons. Brute force, by contrast, can explore exponentially many splits of a string like `"aaaa...ab"`.

## Reduce the transition work

The states are fixed; the cost per state is what you can improve. When the dictionary is large but words are short, try **lengths** instead of words: put the words in a set and, at each position, look up the substrings of length 1 to L. The number of candidates per position now depends on L, not on W.

In Python, each candidate slice is a fresh string that costs work proportional to its length to build and hash, so this is O(nL²) character work plus O(WL) to build the set. A trie (prefix tree) avoids rebuilding slices: walk it one character at a time from position i and stop when no branch continues, for O(nL) plus O(WL) to build it. These are growth estimates, not timings.

## Key takeaways
- A suffix state decides whether the rest of the string can be split.
- Nonempty words make every dependency advance to a larger index.
- Record a successful word end to reconstruct one split.

## Further reading
- [Erickson: dynamic programming](https://jeffe.cs.illinois.edu/teaching/algorithms/book/03-dynprog.pdf)
- [MIT algorithms course](https://ocw.mit.edu/courses/6-006-introduction-to-algorithms-spring-2020/)
