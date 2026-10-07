---
id: auto-pumping
title: The pumping lemma
level: intermediate
minutes: 15
summary: Why every long string accepted by a finite automaton contains a loop that can be repeated, and how to turn that into proofs that languages like aⁿbⁿ, palindromes and balanced brackets are not regular.
---

Lesson 1 claimed that no DFA recognises "equal numbers of a's and b's" or "balanced brackets". Claiming is easy. How do you **prove** that no DFA exists, out of the infinitely many you could build?

You cannot try them all. Instead you find a property that every regular language has, then show your language lacks it. The most famous such property is the **pumping lemma**. It comes from one observation: a machine with p states that reads a string of length p or more must visit some state twice.

## The pigeonhole idea

Run a DFA with p states on a string of length n ≥ p. The run visits n + 1 states (including the start). n + 1 > p, so by the pigeonhole principle some state appears twice, and it must happen within the first p symbols.

Look at what happens between the two visits. The machine read some non-empty chunk y and came back to where it was. So it is in a **loop**:

```
          y
        +---+
        v   |
--> ... (q) +  ... --> accept
   x         z
```

Split the string as s = xyz:

- x takes the machine from the start to q,
- y takes it from q back to q,
- z takes it from q to an accepting state.

Because y returns to q, the machine cannot tell how many times it went round. xz (skip the loop), xyz, xyyz and xyyyz all end in the same state. If one is accepted, they all are.

### A concrete loop

Take the 3-state "divisible by 3" DFA from lesson 1 and the string `1111` (15). The run is:

```
state:  0  1  0  1  0
read:     1  1  1  1
```

State 0 repeats after `11`. So x = ε, y = `11`, z = `11`. Pumping gives `11`, `1111`, `111111`, ..., which are 3, 15, 63: all divisible by 3. The DFA says so, because 4ᵏ − 1 is always divisible by 3.

## The lemma

> [!note] Pumping lemma for regular languages
> If L is regular, there is a number p ≥ 1 (the **pumping length**) such that every string s ∈ L with |s| ≥ p can be split as s = xyz where:
> 1. |y| ≥ 1,
> 2. |xy| ≤ p,
> 3. xyⁱz ∈ L for every i ≥ 0.

For any DFA recognising L, p can be taken to be its number of states. Condition 2 holds because the repeat happens within the first p symbols. Note that i = 0 (deleting y) is allowed, and is often the most useful choice.

## Using it: proof by contradiction

The lemma is a statement "if regular, then pumpable". To show L is **not** regular, show that L is not pumpable. The quantifiers matter, so it helps to see the proof as a game against an adversary who claims L is regular:

1. **Adversary** picks p. You don't know it, so treat it as a variable.
2. **You** pick a string s ∈ L with |s| ≥ p. Choose wisely; this is the creative step.
3. **Adversary** picks any split s = xyz with |y| ≥ 1 and |xy| ≤ p. You must beat **every** possible split.
4. **You** pick an i ≥ 0 and show xyⁱz ∉ L.

If you can always win, L is not regular.

## Example 1: aⁿbⁿ

L = { aⁿbⁿ : n ≥ 0 }.

1. Let p be the pumping length.
2. Choose s = aᵖbᵖ. It is in L and has length 2p ≥ p.
3. Any split has |xy| ≤ p. The first p symbols are all a's, so x and y consist only of a's. Say y = aᵏ with k ≥ 1.
4. Pump with i = 2: xy²z = aᵖ⁺ᵏbᵖ. It has more a's than b's, so it is not in L.

Contradiction, so L is not regular.

The choice of s did the work. Putting all the a's in the first p symbols forced y to contain only a's, so we did not need to consider cases.

> [!tip] Why condition 2 is your friend
> |xy| ≤ p pins y inside the first p characters. Pick s so that its first p characters are "all the same kind", and the adversary has no room to manoeuvre.

## Example 2: palindromes

L = palindromes over {a, b}.

1. Choose s = aᵖbaᵖ, a palindrome of length 2p + 1.
2. Again y lies in the first p symbols, so y = aᵏ with k ≥ 1.
3. Pump down, i = 0: aᵖ⁻ᵏbaᵖ. The b is no longer in the middle, so it is not a palindrome.

Contradiction. The same template works for { ww : w ∈ {a, b}* } with s = aᵖbaᵖb.

## Example 3: perfect squares

L = { aⁿ : n is a perfect square }. Only one symbol, so the trick is arithmetic.

1. Choose s = aᵖ², length p².
2. y = aᵏ with 1 ≤ k ≤ p.
3. Pump up, i = 2: the length becomes p² + k.
4. p² < p² + k ≤ p² + p < p² + 2p + 1 = (p + 1)².

So p² + k lies strictly between two consecutive squares and is not a square. Contradiction.

## Example 4: more a's than b's

L = { aⁱbʲ : i > j }. Pumping up only adds more a's, which keeps the string in L. So pump **down**.

1. Choose s = aᵖ⁺¹bᵖ.
2. y = aᵏ, k ≥ 1.
3. i = 0 gives aᵖ⁺¹⁻ᵏbᵖ. Since k ≥ 1, the number of a's is at most p, which is not more than p. Not in L.

The lesson: try both directions. Different languages break under different i.

## Shortcuts with closure properties

Regular languages are closed under intersection, union, complement and more. That gives a second tool.

L = "strings over {a, b} with equally many a's and b's". The same aᵖbᵖ witness proves non-regularity directly. Closure gives another proof:

1. Suppose L were regular.
2. a*b* is regular.
3. Then L ∩ a*b* would be regular, because regular languages are closed under intersection.
4. But L ∩ a*b* = { aⁿbⁿ }, which we proved is not regular.

Contradiction. Balanced brackets fall the same way: intersect with the regular language consisting of zero or more opening brackets followed by zero or more closing brackets to get (ⁿ)ⁿ, which is aⁿbⁿ in disguise.

## What it means in practice

- **Regex cannot parse nested structure.** HTML, JSON, arithmetic expressions and balanced brackets all contain aⁿbⁿ-style matching. A true regex can handle a fixed maximum depth, but not arbitrary nesting. Use a parser (a pushdown automaton, next module).
- **Some engines go beyond regular.** Perl, PCRE and .NET support recursion or balancing groups and can match balanced brackets. These features go beyond formal regular expressions. Their performance depends on the engine and pattern; recognizing balanced brackets itself can be done in linear time with a parser.
- **Counting has to be bounded.** "At most 3 levels of nesting" or "length ≤ 255" is regular; "same number of opening and closing tags" is not.

## Pitfalls

- **The lemma does not prove regularity.** It is "regular ⟹ pumpable". Some non-regular languages are pumpable. For example L = { aⁱbʲcᵏ : i = 0 or j = k } satisfies the lemma with p = 1, yet L ∩ ab*c* = { abⁿcⁿ } shows it is not regular. The Myhill–Nerode theorem (next lesson) gives an exact test.
- **You do not choose the split.** A proof that says "let y = a" only handles one split. You must show every legal split fails.
- **You do not choose p.** Writing "let p = 5" proves nothing. Keep p symbolic.
- **Pick s with |s| ≥ p.** A string shorter than p is outside the lemma's promise.
- **Finite languages are always regular**, so you cannot prove a finite language non-regular. Every finite language trivially satisfies the lemma, with p longer than its longest string.

## Key takeaways
- A DFA with p states reading p or more symbols must repeat a state; the substring between the repeats is a loop y that can be repeated or removed.
- Pumping lemma: if L is regular, every s ∈ L with |s| ≥ p splits as xyz with |y| ≥ 1, |xy| ≤ p and xyⁱz ∈ L for all i ≥ 0.
- To prove non-regularity, play the game: you choose s and i; the adversary chooses p and the split, and you must beat every split.
- Choose s so its first p symbols are uniform; try both i = 0 and i = 2.
- Closure properties often give shorter proofs: intersect with a regular language to reduce to aⁿbⁿ.
- Pumpable does not mean regular; use Myhill–Nerode for an exact test.

## Further reading
- [Pumping lemma for regular languages — Wikipedia](https://en.wikipedia.org/wiki/Pumping_lemma_for_regular_languages)
- [Pigeonhole principle — Wikipedia](https://en.wikipedia.org/wiki/Pigeonhole_principle)
- [Myhill–Nerode theorem — Wikipedia](https://en.wikipedia.org/wiki/Myhill%E2%80%93Nerode_theorem)
- [MIT OpenCourseWare 18.404J Theory of Computation (Sipser)](https://ocw.mit.edu/courses/18-404j-theory-of-computation-fall-2020/)
