---
id: compu-counting-diagonal
title: Counting machines and diagonalising languages
level: advanced
minutes: 5
summary: Finite machine descriptions can be enumerated.
sourceLesson: compu-halting
---

Wouldn't it be useful to have a tool that reads any program and its input and tells you whether it will finish or run forever? Your continuous-integration pipeline could reject code with infinite loops. Your OS could kill hung processes the moment they hang.

Turing’s 1936 work established foundational undecidability results; the modern halting formulation proved below is a consequence of that framework. Not "we haven't found one yet": no effective algorithm decides halting for every program/input pair in a Turing-complete model with unbounded resources. A closed deterministic machine with a fixed finite state space is different: cycle detection decides halting in principle, though it may be infeasible. The proof uses a single idea, **diagonalisation**, that also shows something even stranger: almost every problem has no algorithm at all.

## Countable and uncountable

A set is **countable** if it is finite or its elements can be listed in a sequence that eventually reaches every element:

```formula
e_1, e_2, e_3, …
ℕ = {0, 1, 2, 3, …}
ℤ = {…, −2, −1, 0, 1, 2, …}
e_1, e_2, e_3, e_4, e_5 = 0, 1, −1, 2, −2
where
e_1, e_2, e_3, e_4, e_5: the 1st, 2nd, 3rd, 4th and 5th items in the list; in general e_i is the i-th item, for a whole number i = 1, 2, 3, …
ℕ: the natural numbers: 0, 1, 2, 3, … (some books start at 1)
ℤ: the integers: the whole numbers, negative, zero and positive
…: and so on, following the same pattern
In words: a set is countable when you can number its members 1st, 2nd, 3rd, … without missing any; the integers can be listed by alternating positive and negative.
```

The natural numbers are countable, and so are the integers: the list 0, 1, −1, 2, −2, … reaches any integer, say −7, at a finite position (the 15th). Countable sets are the "smallest" infinite sets: ℕ and ℤ have the same size of infinity.

**Turing machines are countable.** Each TM M has a finite description ⟨M⟩, a string over a finite alphabet. List all strings by length, then alphabetically within a length, and skip the ones that aren't valid descriptions. Every TM appears at some finite position. The same goes for Python programs: each is a finite text file.

**Languages are not countable.** This is Cantor's diagonal argument.

## Cantor's diagonal argument

Fix the alphabet {0, 1} and list all strings in order of length. A language L is any set of these strings, so you can describe L by an infinite row of bits:

```formula
s_1 = ε   s_2 = 0   s_3 = 1   s_4 = 00   …
bit_i(L) = 1   if s_i ∈ L
bit_i(L) = 0   if s_i ∉ L
where
s_1, s_2, s_3, s_4: the first four binary strings in the list
s_i: the i-th string in the list (shortest first, then in numerical order within each length)
ε: epsilon, the empty string, which comes first because it has length 0
L: a language: any set of binary strings, finite or infinite
bit_i(L): the i-th bit of L's row: 1 if L contains the i-th string, 0 if not
i: a position in the list, 1, 2, 3, …
∈, ∉: is a member of, is not a member of
In words: every language is a yes/no answer for each string in the list, so it can be written as an infinite sequence of bits.
```

For example, the language "strings that start with 1" begins 0, 0, 1, 0, … because its first member is the third listed string, the one-character string `1`.

**Claim.** No list L₁, L₂, L₃, … contains every language.

**Proof.** Take any such list and write the rows in a table:

```
        s₁  s₂  s₃  s₄  ...
  L₁   [1]  0   1   1
  L₂    0  [0]  0   1
  L₃    1   1  [1]  0
  L₄    0   1   0  [0]
  ...
```

Build a new language D by flipping the diagonal:

```formula
D = { s_i : s_i ∉ L_i }
D ≠ L_i   for every i
where
D: the diagonal language being built
s_i: the i-th string in the list of all binary strings
L_i: the i-th language in the supposed complete list
i: a position, 1, 2, 3, …
∉: is not a member of
≠: is not equal to
{ … : … }: set-builder notation: the set of all s_i that satisfy the condition after the colon
In words: D contains the i-th string exactly when the i-th language does not, so D disagrees with every listed language somewhere.
```

In the table, the diagonal reads 1, 0, 1, 0, so D's row starts 0, 1, 0, 1. Compare D with any row Lᵢ. At column i they disagree, because D was defined to disagree there. Thus D differs from every listed language, so D is missing from the list. Since the list was arbitrary, no list contains every language. ∎

**Consequence.** There are countably many TMs but uncountably many languages, so all but countably many languages are not recognised by any TM. Each TM recognises one language; there are simply not enough TMs to go round.

That is an existence proof. It doesn't name a specific unsolvable problem. The halting problem does.

## Key takeaways

- Finite machine descriptions can be enumerated.
- Flipping a diagonal constructs a language missing from any proposed list of all languages.
- There are uncountably many languages, so all but countably many have no recogniser.

## Further reading

- [Sipser: undecidability and diagonalisation](https://ocw.mit.edu/courses/18-404j-theory-of-computation-fall-2020/resources/mit18_404f20_lec8-1/)
