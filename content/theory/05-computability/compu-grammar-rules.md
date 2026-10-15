---
id: compu-grammar-rules
title: Rewrite rules and context-free grammars
level: basic
minutes: 5
summary: A rewrite rule replaces one variable without inspecting its surroundings.
sourceLesson: compu-cfg
---

Finite automata have a fixed, finite memory. That is why no DFA can recognise `aⁿbⁿ` (some number of a's followed by the same number of b's): to check the b's, it would have to remember an unbounded count of a's.

Yet the languages programmers care about are full of exactly this kind of matching. Every `(` needs a `)`. Every `{` needs a `}`. Nested block structures can have arbitrarily many pending delimiters in the mathematical model; concrete language and markup rules add their own exceptions and constraints. **Context-free grammars** (CFGs) are the next step up the ladder. They can describe nesting, and they are the formal basis of almost every programming-language parser.

## The idea: rewrite rules

A grammar is a set of rewrite rules. You start from a start symbol and keep replacing symbols until only real characters remain.

First, the notation `aⁿbⁿ`. A superscript on a letter means "repeat it that many times", and a **formal language** is just a set of strings. So `aⁿbⁿ` names this language:

```formula
L = { a^n b^n : n ≥ 0 }
L = { ε, "ab", "aabb", "aaabbb", … }
where
L: the language being described: a set of strings
a, b: the two characters (letters) the strings are made of
n: a whole number 0, 1, 2, … saying how many copies
a^n: the letter a written n times in a row, so a^3 is "aaa" and a^0 is the empty string
ε: epsilon, the empty string: a string with no characters at all
{ … : … }: set-builder notation: the set of everything of the form before the colon, for every value allowed by the condition after it
≥: is greater than or equal to
…: and so on, following the same pattern
In words: L is every string made of some number of a's followed by exactly the same number of b's, including the empty string.
```

Here is a grammar for that language, as two rewrite rules, and a derivation that uses them:

```formula
S → a S b
S → ε
S ⇒ a S b ⇒ a a S b b ⇒ a a b b
where
S: the start variable: a placeholder that must eventually be rewritten away
a, b: terminals: real characters that appear in the final string
ε: epsilon, the empty string (rewriting S to ε just deletes it)
→: "may be rewritten as": the left side may be replaced by the right side
⇒: one rewriting step, applying one rule to the current string
In words: S may be replaced by a S b or deleted; using the first rule twice and then the second turns S into aabb.
```

Read the rules as: "an S is either an `a`, then another S, then a `b`; or it is the empty string ε". A vertical bar between alternatives is the usual shorthand for “or”; it combines the two displayed rules on one line. Inside a grammar, letters written side by side (`aSb`) simply follow each other; nothing is multiplied.

Each `⇒` in the derivation is one rule application, called a **derivation step**. For `aabb` that is three steps: two enclosing-pair rules, then one empty-string rule. In general:

```formula
D(n) = n + 1
where
D(n): the number of rule applications in this grammar
n: the nonnegative number of a symbols, equal to the number of b symbols
In words: Each enclosing pair uses one rule and finishing uses one empty-string rule.
```

Every time an `a` is added, a matching `b` is added on the other side. The grammar never has to count; the structure of the rule does the matching for it.

## Key takeaways

- Each wrapping rule contributes one a symbol and one matching b symbol.
- Terminal strings arise by repeatedly rewriting from the start variable.
- Equal blocks require one wrapping step per pair and one final empty-string step.

## Further reading

- [Sipser: grammars, parse trees and pushdown automata](https://ocw.mit.edu/courses/18-404j-theory-of-computation-fall-2020/resources/mit18_404f20_lec4-1/)
