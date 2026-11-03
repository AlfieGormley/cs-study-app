---
id: adv-string-naive-waste
title: Why naive string search repeats work
level: advanced
minutes: 3
summary: Repeated prefixes make naive matching retry the same successful comparisons.
sourceLesson: adv-string-algorithms
---

Here n is the text or indexed-string length, m is the pattern length, and positions count from zero. Costs count constant-time character and word operations unless noted.

The naive matcher tries each possible start and compares characters from the beginning of the pattern. If a mismatch occurs late, it may repeat almost all those comparisons at the next start. In the worst case this costs O(nm), where n is text length and m is pattern length.

Searching for `aaaab` inside a long run of `a`s exposes the waste: each attempt rechecks four successful comparisons before failing on the `b`. Early mismatches can make naive matching much cheaper, but repetitive input removes that advantage.

The algorithms in this lesson avoid that waste in different ways. **KMP** and the **Z-function** reuse previous matches instead of restarting the search at every position. **Rabin–Karp** compares hashes instead of strings. **Suffix arrays** pre-process the text once so that many later queries are fast.

## The waste in naive matching

Suppose we search for `abab` and have matched `aba` before a mismatch:

```
text:    a b a c ...
pattern: a b a b
               ^ mismatch
```

Naive matching slides the pattern one place and starts again from scratch. But we already know the last three text characters were `aba`. The end of what we matched (`a`) is also a start of the pattern, so the next possible match can begin there, with one character already matched. Nothing before it can work.

KMP precomputes, for every prefix of the pattern, exactly this "how much can I keep?" number.

## Key takeaways

- Repeated prefixes make naive matching retry the same successful comparisons.
- A string border tells a matcher which already-matched characters it can retain.

## Further reading
- [Prefix function and KMP — cp-algorithms](https://cp-algorithms.com/string/prefix-function.html)
- [Z-function — cp-algorithms](https://cp-algorithms.com/string/z-function.html)
