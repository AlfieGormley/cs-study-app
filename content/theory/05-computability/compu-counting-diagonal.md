---
id: compu-counting-diagonal
title: Counting machines and diagonalising languages
level: advanced
minutes: 4
summary: Finite machine descriptions can be enumerated.
sourceLesson: compu-halting
---

Wouldn't it be useful to have a tool that reads any program and its input and tells you whether it will finish or run forever? Your continuous-integration pipeline could reject code with infinite loops. Your OS could kill hung processes the moment they hang.

Turing’s 1936 work established foundational undecidability results; the modern halting formulation proved below is a consequence of that framework. Not "we haven't found one yet": no effective algorithm decides halting for every program/input pair in a Turing-complete model with unbounded resources. A closed deterministic machine with a fixed finite state space is different: cycle detection decides halting in principle, though it may be infeasible. The proof uses a single idea, **diagonalisation**, that also shows something even stranger: almost every problem has no algorithm at all.

## Countable and uncountable

A set is **countable** if it is finite or its elements can be listed in a sequence that eventually reaches every element. The natural numbers are countable, and so are the integers: list zero, then one and minus one, then two and minus two, and continue. Every integer gets a finite position even though the list never ends. These two infinite sets have the same size of infinity.

**Turing machines are countable.** Each TM M has a finite description ⟨M⟩, a string over a finite alphabet. List all strings by length, then alphabetically within a length, and skip the ones that aren't valid descriptions. Every TM appears at some finite position. The same goes for Python programs: each is a finite text file.

**Languages are not countable.** This is Cantor's diagonal argument.

## Cantor's diagonal argument

Fix the binary alphabet and list every finite string by length, then alphabetically within each length: the empty string, `0`, `1`, `00`, and so on. Give each string a column. A language has one bit in every column: one if it contains that string, zero otherwise. Even a finite language needs an infinite row, with zeros for all the strings it omits.

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

```formula essential
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
