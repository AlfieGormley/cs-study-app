---
id: auto-pumping-matching-counts
title: Pumping matching counts and copied strings
level: intermediate
minutes: 5
sourceLesson: auto-pumping
summary: Uniform first symbols force the pumped piece into one run.
---

## Example 1: a's followed by the same number of b's

The language is every string of some a's followed by exactly as many b's:

```formula
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

```formula
s = a^p b a^p,   |s| = 2p + 1
y = a^k,   1 ≤ k ≤ p
x · y^0 · z = a^{p − k} b a^p ∉ L
where
s: the string we choose: p a's, one b, p a's; a palindrome
L: the palindromes over {a, b}
a, b: the two symbols
a^p: p copies of a in a row
p: the pumping length; a positive integer measured in input symbols
| |: the length of a string
x, y, z: the adversary's split
k: the length of y; an integer count, non-negative unless a positive lower bound is stated
y^0: zero copies of y, so y is deleted
·: concatenation
∉: is not an element of
≤: is less than or equal to (the first comparison makes k at least 1)
In words: y must be a block of a's from the left side, and deleting it leaves fewer a's before the b than after it, so the result is not a palindrome.
```

The b is no longer in the middle, so it is not a palindrome. Contradiction. With p = 2 and y = `a`, for example, `aabaa` becomes `abaa`.

The same template works for the language of "doubled" strings, a string followed by an exact copy of itself:

```formula
L₂ = { w · w : w ∈ {a, b}* }
s = a^p b a^p b
where
L₂: the language of doubled strings
a, b: the two input symbols
w: any string over {a, b}
·: concatenation
{a, b}*: every string of a's and b's, including the empty string
∈: is an element of
a^p: p copies of a
p: the pumping length; a positive integer measured in input symbols
s: the string to choose, which is w · w with w = a^p b
In words: the doubled-string language is not regular either; choose p a's and a b, written twice.
```

Again y must be a block of a's from the first run. Deleting it shortens the first run but not the second, so the string can no longer be split into two identical halves.

## Key takeaways
- Uniform first symbols force the pumped piece into one run.
- Deleting or repeating one side breaks equal counts, palindromes and the chosen doubled-string witness.

## Further reading
- [MIT: the regular pumping lemma and automata to regexes](https://ocw.mit.edu/courses/18-404j-theory-of-computation-fall-2020/resources/mit18_404f20_lec3-1/)
