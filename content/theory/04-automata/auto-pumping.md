---
id: auto-pumping
title: The pumping lemma
level: intermediate
minutes: 18
summary: Why every long string accepted by a finite automaton contains a loop that can be repeated, and how to turn that into proofs that languages like aⁿbⁿ, palindromes and balanced brackets are not regular.
---

Lesson 1 claimed that no DFA recognises "equal numbers of a's and b's" or "balanced brackets". Claiming is easy. How do you **prove** that no DFA exists, out of the infinitely many you could build?

You cannot try them all. Instead you find a property that every regular language has, then show your language lacks it. The most famous such property is the **pumping lemma for regular languages**. It comes from one observation: a machine with p states that reads a string of length p or more must visit some state twice.

## The pigeonhole idea

Count the states a run visits. Reading each symbol moves to one new state, and the start state counts too, so a run is always one state longer than the string.

```formula
n ≥ p
n + 1 > p
where
p: the number of states in the DFA
n: the length of the input string, in symbols
≥: is greater than or equal to
>: is greater than
In words: if the string is at least as long as the number of states, the run visits more states than exist, so some state must appear twice.
```

This is the **pigeonhole principle**: put more than p pigeons into p holes and some hole holds two. It also tells you where the repeat happens. The first p symbols already give p + 1 visits, so some state repeats within the first p symbols.

For example, a 3-state DFA reading 5 symbols visits 6 states, so at least one of its 3 states appears twice, and the first repeat comes within the first 3 symbols.

Look at what happens between the two visits. The machine read some non-empty chunk and came back to where it was. So it is in a **loop**:

```
          y
        +---+
        v   |
--> ... (q) +  ... --> accept
   x         z
```

Cut the string into three pieces around the loop:

```formula
s = x · y · z
δ̂(q₀, x) = q
δ̂(q, y) = q
δ̂(q, z) ∈ F
x · y^i · z ∈ L   for all i ≥ 0
where
s: the accepted string
x: the part read before first reaching the repeated state
y: the part read going round the loop, from q back to q; it is not empty
z: the rest of the string, read after the loop
·: concatenation: one string straight after another
q₀: the start state
q: the state that is visited twice
δ̂: "delta hat": δ̂(state, string) is the state you end in after reading the whole string from that state
∈: is an element of
F: the set of accepting states
L: the language the DFA recognises
y^i: i copies of y in a row; y^0 is the empty string, y^2 = y · y
i: how many times you go round the loop, 0, 1, 2, …
≥: is greater than or equal to
In words: x leads to q, y goes from q back to q, and z leads from q to acceptance. Because y returns to q, the machine cannot tell how many times it went round, so repeating y, or deleting it, leaves a string the machine still accepts.
```

So xz (skip the loop), xyz, xyyz and xyyyz all end in the same state. If one is accepted, they all are.

### A concrete loop

Take the 3-state "divisible by 3" DFA from lesson 1 and the string `1111` (15). The run is:

```
state:  0  1  0  1  0
read:     1  1  1  1
```

State 0 repeats after `11`. So the pieces are:

```formula
x = ε     y = "11"     z = "11"
x · y^0 · z = "11"         (3)
x · y^1 · z = "1111"       (15)
x · y^2 · z = "111111"     (63)
v_k = 4^k − 1
where
x, y, z: the three pieces of 1111 around the loop at state 0
ε: Greek epsilon: the empty string
"11": the two-symbol string 1 then 1 (the quotes mark a string of bits, not the number eleven)
·: concatenation: one string straight after another
y^i: i copies of y in a row
k: the number of pairs of 1s in the string after pumping; with i copies of y it is i + 1, because z adds one more pair
v_k: the value, in ordinary numbers, of a binary string of k pairs of 1s, that is 2 × k ones
In words: deleting the loop gives 11 (three), keeping it gives 1111 (fifteen), doubling it gives 111111 (sixty-three). In general k pairs of 1s is worth 4^k − 1, and all of these are divisible by 3.
```

The DFA says so, and arithmetic agrees: 4 leaves remainder 1 when divided by 3, so every power of 4 does too, and subtracting 1 leaves a multiple of 3.

## The lemma

> [!note] Pumping lemma for regular languages
> If a language is regular, there is a number, its **pumping length**, such that every string in the language at least that long can be cut into three pieces: a non-empty middle piece that lies within the first pumping-length symbols, and that can be repeated any number of times, or deleted, without leaving the language.

In symbols:

```formula
L ∈ REG   ⟹   ∃ p ≥ 1 such that
∀ s ∈ L with |s| ≥ p,
∃ x, y, z with s = x · y · z and:
  1.  |y| ≥ 1
  2.  |x · y| ≤ p
  3.  x · y^i · z ∈ L   for all i ≥ 0
where
L: the language
REG: the class of regular languages, those recognised by some DFA
⟹: implies: if the left side is true, the right side is true
∃: there exists: at least one such thing can be found
∀: for all: whichever one you pick
p: the pumping length, a whole number at least 1
s: any string in L
x, y, z: three pieces of s; y is the pumped piece
·: concatenation: one string straight after another
| |: vertical bars around a string mean its length
∈: is an element of
≥: is greater than or equal to
≤: is less than or equal to
y^i: i copies of y in a row; y^0 is the empty string
i: how many copies of y to use, 0, 1, 2, …
In words: if L is regular, then any long enough string in L has a non-empty piece near its start that can be repeated or deleted while staying in L.
```

For any DFA recognising L, p can be taken to be its number of states. Condition 2 holds because the repeat happens within the first p symbols. Note that i = 0 (deleting y) is allowed, and is often the most useful choice.

For example, with the 3-state divisible-by-3 DFA a pumping length of 3 works, and the split of `1111` above has a loop piece of length 2, lying inside the first 3 symbols.

## Using it: proof by contradiction

The lemma is a statement "if regular, then pumpable". To show L is **not** regular, show that L is not pumpable: then it cannot be regular, a **proof by contradiction**. The quantifiers ("for every", "there exists") matter, so it helps to see the proof as a game against an adversary who claims L is regular:

```formula
∀ p ≥ 1   ∃ s ∈ L with |s| ≥ p :
∀ x, y, z with s = x · y · z,
  |y| ≥ 1 and |x · y| ≤ p :
∃ i ≥ 0 with x · y^i · z ∉ L
where
p: the pumping length, chosen by the adversary
s: the string you choose
L: the language you want to prove non-regular
x, y, z: the split, chosen by the adversary
·: concatenation
| |: the length of a string
∈: is an element of
∉: is not an element of
≥: is greater than or equal to
≤: is less than or equal to
y^i: i copies of y in a row
i: the number of copies, chosen by you
∀: for all: the adversary's moves, which you must handle whatever they are
∃: there exists: your moves, where you only need one that works
In words: whatever p the adversary names, you name a long string in L, and whatever legal split they then make, you find a number of copies of y that throws the string out of L.
```

As a game:

1. **Adversary** picks the pumping length. You don't know it, so treat it as a variable.
2. **You** pick a long enough string in L. Choose wisely; this is the creative step.
3. **Adversary** picks any legal split. You must beat **every** possible split.
4. **You** pick the number of copies of the middle piece and show the result is not in L.

If you can always win, L is not regular.

## Example 1: a's followed by the same number of b's

The language is every string of some a's followed by exactly as many b's:

```formula
L = { a^n b^n : n ≥ 0 }
s = a^p b^p,   |s| = 2 × p ≥ p
y = a^k,   1 ≤ k ≤ p
x · y^2 · z = a^{p + k} b^p ∉ L
where
L: the language
a, b: the two symbols
a^n: n copies of a in a row, so a^3 = aaa; a^0 is the empty string
n: any whole number 0 or more
p: the pumping length, whatever the adversary chose
s: the string we choose: p a's then p b's
| |: the length of a string
x, y, z: the adversary's split of s
y^2: y twice
k: the length of y
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

Contradiction, so L is not regular. For instance, if the adversary chose p = 3 and y = `aa`, the string `aaabbb` pumps to `aaaaabbb`, with 5 a's and 3 b's.

The choice of s did the work. Putting all the a's in the first p symbols forced y to contain only a's, so we did not need to consider cases.

> [!tip] Why condition 2 is your friend
> Condition 2 pins the pumped piece inside the first p characters. Pick a string whose first p characters are "all the same kind", and the adversary has no room to manoeuvre.

## Example 2: palindromes

A **palindrome** reads the same forwards and backwards, like `abba` or `aabaa`. Let L be the palindromes over {a, b}.

```formula
s = a^p b a^p,   |s| = 2 × p + 1
y = a^k,   1 ≤ k ≤ p
x · y^0 · z = a^{p − k} b a^p ∉ L
where
s: the string we choose: p a's, one b, p a's; a palindrome
L: the palindromes over {a, b}
a, b: the two symbols
a^p: p copies of a in a row
p: the pumping length
| |: the length of a string
x, y, z: the adversary's split
k: the length of y
y^0: zero copies of y, so y is deleted
·: concatenation
∉: is not an element of
≤: is less than or equal to
In words: y must be a block of a's from the left side, and deleting it leaves fewer a's before the b than after it, so the result is not a palindrome.
```

The b is no longer in the middle, so it is not a palindrome. Contradiction. With p = 2 and y = `a`, for example, `aabaa` becomes `abaa`.

The same template works for the language of "doubled" strings, a string followed by an exact copy of itself:

```formula
L₂ = { w · w : w ∈ {a, b}* }
s = a^p b a^p b
where
L₂: the language of doubled strings
w: any string over {a, b}
·: concatenation
{a, b}*: every string of a's and b's, including the empty string
∈: is an element of
a^p: p copies of a
p: the pumping length
s: the string to choose, which is w · w with w = a^p b
In words: the doubled-string language is not regular either; choose p a's and a b, written twice.
```

Again y must be a block of a's from the first run. Deleting it shortens the first run but not the second, so the string can no longer be split into two identical halves.

## Example 3: perfect squares

Let L be the strings of a's whose length is a **perfect square** (0, 1, 4, 9, 16, …). Only one symbol, so the trick is arithmetic.

```formula
s = a^{p²},   |s| = p²
y = a^k,   1 ≤ k ≤ p
|x · y^2 · z| = p² + k
p² < p² + k ≤ p² + p < (p + 1)²
where
s: the string we choose: p² a's
a: the only symbol
p: the pumping length
p²: p squared, p × p
| |: the length of a string
x, y, z: the adversary's split
y^2: y twice, so one extra copy
k: the length of y
·: concatenation
<: is less than
≤: is less than or equal to
(p + 1)²: the next perfect square after p², equal to p² + 2 × p + 1
In words: one extra copy of y adds between 1 and p symbols, which lands strictly between p² and the next square, so the new length is not a square.
```

So p² + k lies strictly between two consecutive squares and is not a square. Contradiction. With p = 3: lengths 10, 11 or 12, all between 9 and 16.

## Example 4: more a's than b's

Let L be the strings of a's then b's with more a's than b's. Pumping up only adds more a's, which keeps the string in L. So pump **down**.

```formula
L = { a^i b^j : i > j }
s = a^{p + 1} b^p
y = a^k,   k ≥ 1
x · y^0 · z = a^{p + 1 − k} b^p ∉ L
where
L: the language
a, b: the two symbols
i, j: the numbers of a's and b's
>: is greater than
s: the string we choose: one more a than b
p: the pumping length
x, y, z: the adversary's split
k: the length of y, at least 1
y^0: zero copies of y, so y is deleted
·: concatenation
∉: is not an element of
≥: is greater than or equal to
In words: deleting y leaves at most p a's against p b's, so there are no longer more a's than b's.
```

Since k is at least 1, the number of a's is at most p, which is not more than p. Not in L. For example, with p = 3, `aaaabbb` loses at least one a and becomes, say, `aaabbb`.

The lesson: try both directions. Different languages break under different numbers of copies.

## Shortcuts with closure properties

Regular languages are closed under intersection, union, complement and more: combining regular languages with these operations always gives a regular language. That gives a second tool.

Let L be the strings over {a, b} with equally many a's and b's. The same p a's then p b's witness proves non-regularity directly. Closure gives another proof:

```formula
L ∩ a*b* = { a^n b^n : n ≥ 0 }
where
L: strings with equally many a's and b's
∩: intersection: the strings in both languages
a*b*: the regular language "any number of a's, then any number of b's"
*: the Kleene star: zero or more copies
a^n b^n: n a's followed by n b's
n: any whole number 0 or more
≥: is greater than or equal to
In words: the strings with equal counts that also have all their a's before their b's are exactly the a's-then-equal-b's strings from Example 1.
```

1. Suppose L were regular.
2. a*b* is regular.
3. Then their intersection would be regular, because regular languages are closed under intersection.
4. But that intersection is the language from Example 1, which we proved is not regular.

Contradiction. Balanced brackets fall the same way: intersect with the regular language consisting of zero or more opening brackets followed by zero or more closing brackets, and you get n opening brackets followed by n closing ones, which is Example 1 in disguise.

## What it means in practice

- **Regex cannot parse nested structure.** HTML, JSON, arithmetic expressions and balanced brackets all contain Example 1-style matching. A true regex can handle a fixed maximum depth, but not arbitrary nesting. Use a parser (a pushdown automaton, next module).
- **Some engines go beyond regular.** Perl, PCRE and .NET support recursion or balancing groups and can match balanced brackets. These features go beyond formal regular expressions. Their performance depends on the engine and pattern; recognising balanced brackets itself can be done in linear time with a parser.
- **Counting has to be bounded.** "At most 3 levels of nesting" or "at most 255 characters long" is regular; "same number of opening and closing tags" is not.

## Pitfalls

- **The lemma does not prove regularity.** It is "regular implies pumpable", not the other way round. Some non-regular languages are pumpable; an example follows this list. The Myhill–Nerode theorem (next lesson) gives an exact test.
- **You do not choose the split.** A proof that says "let y be a" only handles one split. You must show every legal split fails.
- **You do not choose the pumping length.** Writing "let p be 5" proves nothing. Keep p symbolic.
- **Pick a long enough string.** A string shorter than the pumping length is outside the lemma's promise.
- **Finite languages are always regular**, so you cannot prove a finite language non-regular. Every finite language trivially satisfies the lemma, with a pumping length longer than its longest string.

The pumpable but non-regular example:

```formula
L = { a^i b^j c^k : i = 0 or j = k }
L ∩ a · b* · c* = { a b^n c^n : n ≥ 0 }
where
L: the language
a, b, c: the three symbols
i, j, k: the numbers of a's, b's and c's
a^i: i copies of a in a row
∩: intersection: the strings in both languages
a · b* · c*: the regular language "one a, then any number of b's, then any number of c's"
*: the Kleene star: zero or more copies
·: concatenation
n: any whole number 0 or more
≥: is greater than or equal to
In words: L passes the pumping test with pumping length 1 (pump the first symbol), yet intersecting it with a simple regular language leaves "one a, then equal numbers of b's and c's", which is not regular. So L is not regular either.
```

## Key takeaways
- A DFA with p states reading p or more symbols must repeat a state; the substring between the repeats is a loop that can be repeated or removed.
- The pumping lemma for regular languages: if a language is regular, every long enough string in it splits into three pieces, with a non-empty middle piece inside the first pumping-length symbols that can be repeated or deleted while staying in the language.
- To prove non-regularity, play the game: you choose the string and the number of copies; the adversary chooses the pumping length and the split, and you must beat every split.
- Choose a string whose first p symbols are uniform; try both deleting the piece (zero copies) and doubling it (two copies).
- Closure properties often give shorter proofs: intersect with a regular language to reduce to "n a's then n b's".
- Pumpable does not mean regular; use Myhill–Nerode for an exact test.

## Further reading
- [Pumping lemma for regular languages — Wikipedia](https://en.wikipedia.org/wiki/Pumping_lemma_for_regular_languages)
- [Pigeonhole principle — Wikipedia](https://en.wikipedia.org/wiki/Pigeonhole_principle)
- [Myhill–Nerode theorem — Wikipedia](https://en.wikipedia.org/wiki/Myhill%E2%80%93Nerode_theorem)
- [MIT OpenCourseWare 18.404J Theory of Computation (Sipser)](https://ocw.mit.edu/courses/18-404j-theory-of-computation-fall-2020/)
