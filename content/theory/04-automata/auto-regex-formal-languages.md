---
id: auto-regex-formal-languages
title: Formal regex languages and their limits
level: intermediate
minutes: 4
sourceLesson: auto-thompson
summary: Formal regexes combine empty language, empty string and symbols using union, concatenation and star.
---

A tool such as grep -E can compile (a|b)*abb and scan input using the resulting matcher. Throughput depends on the tool, data, hardware and I/O. Between the pattern and the scan is a compiler. It parses the regex into a tree, turns the tree into an automaton, and runs the automaton over the text.

A standard first step of that compiler is **Thompson's construction**, published by Ken Thompson in 1968. It is short enough to write from memory, it produces an NFA linear in the size of the regex, and every piece of it is one of the three operations that define regular expressions.

## What a regular expression is, formally

Strip away the syntax sugar and a regular expression (regex) starts with three building blocks: no possible string, the empty string, or one alphabet symbol. Combine them by choosing either expression, joining one after another, or repeating zero or more times. These operations describe a language without prescribing a particular matching algorithm.

The formal notation is available as a reference:

```formula reference
L(∅) = ∅
L(ε) = {ε}
L(a) = {a}   for a ∈ Σ
L(R|S) = L(R) ∪ L(S)
L(R · S) = { x · y : x ∈ L(R), y ∈ L(S) }
L(R*) = {ε} ∪ L(R) ∪ L(R · R) ∪ …
where
L( ): the language of a regex: the set of strings it matches
∅: the empty set. As a regex it matches nothing at all
ε: Greek epsilon: the empty string. As a regex it matches only the empty string
{ }: the set of the items listed inside
a: any single symbol of the alphabet
Σ: capital Greek sigma: the input alphabet
∈: is an element of
R, S: any two smaller regular expressions
|: union (alternation): match R or S
∪: set union: every string in either set
·: concatenation: one thing straight after another. In regex syntax it is written by placing R and S side by side, as RS
x, y: a string matched by R and a string matched by S
*: the Kleene star: zero or more copies of R, one after another
…: and so on, with three, four, … copies
In words: the only building blocks are "nothing", "the empty string" and single symbols; the only ways to combine them are "either", "one then the other" and "repeat any number of times, including zero".
```

For example:

`a|b` chooses one symbol; `ab` requires a followed by b; `a*` allows any number of a characters, including none.

Read the basic syntax this way. R and S stand for smaller regular expressions; the empty string is written ε and the empty language ∅.

| Regex | Language |
|---|---|
| ∅ | no strings at all |
| ε | just the empty string |
| One alphabet symbol | just that one-symbol string |
| R \| S | strings matched by either expression |
| RS | a string from R followed by a string from S |
| R* | zero or more successive strings from R |

Everything else in everyday regex syntax is shorthand, as long as it stays regular:

- `R+` is `RR*`.
- `R?` is `R|ε`.
- `[a-c]` is `a|b|c`.
- `R{2,3}` is `RR|RRR`.
- In a formal wildcard notation, . can denote the union of the alphabet. Real regex engines commonly exclude newline unless a dot-all option is enabled.

General backreferences can express non-regular languages. The pattern (a+)b\1 matches some a's, a b, then exactly the same text as the first group again:

This pattern requires equally long a-runs on the two sides of b, with no upper bound. A finite automaton cannot remember an arbitrary first run accurately enough to compare the second.

Some individual backreference patterns are still regular: (a+)\1 matches positive even-length runs of a, equivalent to (aa)+. Engines such as RE2 reject the feature syntactically rather than proving regularity separately for each pattern.

Precedence, highest first: star, then concatenation, then union. So `ab|c*` means `(ab)|(c*)`, not `a(b|c)*`.

### Kleene's theorem

Stephen Kleene proved in 1956 that regular expressions and finite automata describe exactly the same languages:

- Every regex has an NFA (and hence a DFA) recognising its language. Thompson's construction is one proof.
- Every DFA has an equivalent regex. State elimination, in its later dedicated unit, is one proof.

That equivalence is why the languages are called *regular*: the regex view and the machine view are two descriptions of one class.

## Key takeaways
- Formal regexes combine empty language, empty string and symbols using union, concatenation and star.
- General backreferences can describe non-regular languages, although individual backreference patterns may be regular.

## Further reading
- [Russ Cox: simple and fast regular-expression matching](https://swtch.com/~rsc/regexp/regexp1.html)
- [MIT: regexes to finite automata](https://ocw.mit.edu/courses/18-404j-theory-of-computation-fall-2020/resources/mit18_404f20_lec2-1/)
