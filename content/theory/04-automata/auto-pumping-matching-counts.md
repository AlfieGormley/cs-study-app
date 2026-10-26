---
id: auto-pumping-matching-counts
title: Pumping matching counts and copied strings
level: intermediate
minutes: 5
sourceLesson: auto-pumping
summary: Uniform first symbols force the pumped piece into one run.
---

## Example 1: a's followed by the same number of b's

The language is every string of some a's followed by exactly as many b's. To expose the missing memory, put all the a characters first. Any legal loop near the beginning then changes the a count without touching the b count.

```formula essential
L = { a^n b^n : n ≥ 0 }
s = a^p b^p,   |s| = 2p ≥ p
y = a^k,   1 ≤ k ≤ p
x · y^2 · z = a^{p + k} b^p ∉ L
where
L: the language
a, b: the two symbols
a^n: n copies of a in a row, so a^3 = aaa; a^0 is the empty string
n: any whole number 0 or more
p: the pumping length, whatever the adversary chose; a positive integer measured in input symbols
s: the string we choose: p a's then p b's
| |: the length of a string
x, y, z: the adversary's split of s
y^2: y twice
k: the length of y; an integer count, non-negative unless a positive lower bound is stated
·: concatenation
∈, ∉: is, and is not, an element of
≥, ≤: greater than or equal to, less than or equal to
In words: choose p a's followed by p b's. Any legal y lies in the first p symbols, which are all a's, so y is a block of k a's. Repeating it gives more a's than b's, which is not in L.
```

Step by step:

1. Let p be the pumping length.
2. Choose s as p a's then p b's. It is in L and has length 2p, which is at least p.
3. Any split has x and y within the first p symbols. Those are all a's, so y is k a's, with k at least 1.
4. Pump with two copies of y: the result has p + k a's and only p b's, so it is not in L.

Contradiction, so L is not regular. For instance, if the adversary chose pumping length 3 and pumped piece `aa`, the string `aaabbb` pumps to `aaaaabbb`, with 5 a's and 3 b's.

The choice of s did the work. Putting all the a's in the first p symbols forced y to contain only a's, so we did not need to consider cases.

> [!tip] Why condition 2 is your friend
> Condition 2 pins the pumped piece inside the first p characters. Pick a string whose first p characters are "all the same kind", and the adversary has no room to manoeuvre.

## Example 2: palindromes

A **palindrome** reads the same forwards and backwards, like `abba` or `aabaa`. Let L be the palindromes over {a, b}.

Choose a palindrome with a long a-run, one b, and the same a-run again. Make each run as long as the proposed pumping length. Every legal pumped piece lies entirely in the first run. Deleting it shortens only that side, so b is no longer in the middle and the result is not a palindrome.

For example, deleting the first a from `aabaa` gives `abaa`, which no longer reads the same backwards. The general argument works regardless of how long the legal piece is.

The same template works for the language of "doubled" strings, a string followed by an exact copy of itself:

Choose a block consisting of a pumping-length run of a characters followed by b, then write that entire block twice. This is a doubled string, and its initial run forces the pumped piece to contain only a characters.

Again the pumped piece lies entirely in the first a-run. Deleting it leaves exactly two b characters and the final character is b. If the result had two identical halves, each half would contain one b and end at that b. The two a-runs would then have to be equal, but only the first was shortened. No choice of a new halfway point repairs this mismatch.

## Key takeaways
- Uniform first symbols force the pumped piece into one run.
- Deleting or repeating one side breaks equal counts, palindromes and the chosen doubled-string witness.

## Further reading
- [MIT: the regular pumping lemma and automata to regexes](https://ocw.mit.edu/courses/18-404j-theory-of-computation-fall-2020/resources/mit18_404f20_lec3-1/)
