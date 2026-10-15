---
id: auto-pumping-closure-limits
title: Closure proofs and the limits of pumping
level: intermediate
minutes: 4
sourceLesson: auto-pumping
summary: Intersecting with a regular language can isolate a known non-regular matching-count language.
---

## Shortcuts with closure properties

Regular languages are closed under intersection, union, complement and more: combining regular languages with these operations always gives a regular language. That gives a second tool.

Let L be the strings over {a, b} with equally many a's and b's. The same p a's then p b's witness proves non-regularity directly. Closure gives another proof:

```formula
L ∩ a*b* = { a^n b^n : n ≥ 0 }
where
a, b: the two input symbols
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

- **The lemma does not prove regularity.** It is "regular implies pumpable", not the other way round. Some non-regular languages are pumpable; an example follows this list. The Myhill–Nerode theorem (in the later minimisation units) gives an exact test.
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
- Intersecting with a regular language can isolate a known non-regular matching-count language.
- Pumpability is necessary for regularity but is not sufficient.

## Further reading
- [MIT: the regular pumping lemma and automata to regexes](https://ocw.mit.edu/courses/18-404j-theory-of-computation-fall-2020/resources/mit18_404f20_lec3-1/)
