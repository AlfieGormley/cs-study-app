---
id: compu-grammar-trees
title: Generating strings and reading parse trees
level: basic
minutes: 3
summary: Parse trees record grouping; grammar structure controls precedence and associativity.
sourceLesson: compu-cfg
---

## Generating a string is not the same as parsing it

A grammar generates a string by rewriting variables until only terminals remain. A partly rewritten string is a **sentential form**. Searching these forms can find derivations, but a bound on terminal characters alone does not always make the search terminate: rules may keep adding variables without adding terminals.

To decide membership for an arbitrary context-free grammar, use a terminating parser such as CYK, introduced shortly. To understand the grouping of a particular derivation, inspect its parse tree.

## Parse trees

A derivation is a sequence; a **parse tree** shows the structure. Each internal node is a variable, its children are the right-hand side of the rule used, and reading the leaves left to right gives the string.

For arithmetic, a classic grammar is:

```formula essential
E → E "+" T | T
T → T "*" F | F
F → "(" E ")" | "id"
where
E, T, F: grammar variables for expressions, terms and factors; E is the start variable
→: may be rewritten as
|: separates alternative right-hand sides
"+", "*": terminal operator tokens for addition and multiplication
"(", ")": terminal parentheses
"id": a terminal identifier token
In words: Expressions group multiplication inside terms before joining terms with addition.
```

The parse tree for `id + id * id` is:

```
          E
        / | \
       E  +  T
       |   / | \
       T  T  *  F
       |  |     |
       F  F     id
       |  |
       id id
```

The tree puts `id * id` lower down, so it is grouped first. That is operator precedence, encoded purely by the shape of the grammar: `*` lives at the T level, beneath `+` at the E level. The expression rule is left-recursive: its recursive expression comes before the plus token. This makes repeated addition left-associative, grouping the first two operands together.

A **leftmost derivation** always rewrites the leftmost variable. There is a one-to-one match between parse trees and leftmost derivations, so "how many parse trees" and "how many leftmost derivations" are the same question.

## Key takeaways

- A terminal-length bound alone does not make arbitrary derivation search terminate.
- Parse trees record grouping; precedence and associativity depend on grammar structure.

## Further reading

- [Sipser: grammars, parse trees and pushdown automata](https://ocw.mit.edu/courses/18-404j-theory-of-computation-fall-2020/resources/mit18_404f20_lec4-1/)
