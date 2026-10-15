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

**Recurrence.** The first decision is which word starts at position i. For each word `w`, if `s` has `w` at position i and the rest can be split, we're done:

```formula
ok[i] = OR of ok[i + |w|]
  for each w with m(w, i)
ok[n] = True
where
ok[i]: True if the suffix of s starting at position i can be split into dictionary words, False otherwise
i: a position in s, from 0 (the start) to n (just past the end)
w: one dictionary word
m(w, i): True if the word w appears in s starting exactly at position i (s.startswith(w, i) in Python)
|w|: the length of w, in characters
OR: logical or, True if at least one of the values is True (False if there are none)
s: the input string
n: the length of s, in characters
True: the Boolean value "yes"
In words: the suffix from i can be split if some dictionary word matches at i and the rest after that word can also be split.
```

The same rule in Python:

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

**Complexity.** Count states and the work per state:

```formula
T = O(nWL + n + W)
M = O(n + W)
where
T: the worst-case running time, counting character comparisons and table steps
M: the extra memory used, in slots (table entries and word references)
n: the length of the string s, in characters; there are n + 1 states
W: the number of words in the dictionary
L: the length of the longest dictionary word, in characters
O(...): Big-O, growing at most in proportion to the expression inside
In words: each of the n + 1 positions tries all W words, and checking a word costs up to L character comparisons.
```

For example, a 1,000-character string with 500 words of up to 10 characters costs at most about 1,000 × 500 × 10 = 5 million character comparisons. The `+ n + W` terms cover setting up the table and copying the word list; reconstruction copies at most n characters. Compare with brute force, which can explore exponentially many splits of a string like `"aaaa...ab"`.

## Reduce the transition work

When the dictionary is large but words are short, try lengths instead of every word: store words in a set, then look up each substring starting at the current position. In Python, creating and hashing a fresh substring costs work proportional to its length. A trie can instead follow consecutive characters without repeatedly constructing each candidate. For a nonempty dictionary, n is the input length, W the dictionary size and L its positive maximum word length. Expected set lookup with slice-and-hash candidates costs O(nL² + WL) character work including dictionary setup; a trie with constant-cost transitions costs O(nL + WL). These are growth bounds and character-work estimates, rather than wall-clock timings.

## Key takeaways
- A suffix state decides whether the rest of the string can be split.
- Nonempty words make every dependency advance to a larger index.
- Record a successful word end to reconstruct one split.

## Further reading
- [Erickson: dynamic programming](https://jeffe.cs.illinois.edu/teaching/algorithms/book/03-dynprog.pdf)
- [MIT algorithms course](https://ocw.mit.edu/courses/6-006-introduction-to-algorithms-spring-2020/)
