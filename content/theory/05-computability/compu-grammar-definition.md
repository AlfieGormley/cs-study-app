---
id: compu-grammar-definition
title: What makes a grammar context-free
level: basic
minutes: 3
summary: A CFG rewrites one variable at a time and defines a language of terminal strings.
sourceLesson: compu-cfg
---

The previous unit generated equal a and b blocks by wrapping a start variable in matching letters. Here we identify the formal parts that make those rules a context-free grammar.

## The formal definition

A context-free grammar has four finite parts: placeholder variables, terminal symbols, rewrite rules and one designated start variable. Variables and terminals are disjoint. Each rule replaces exactly one variable with a string of variables and terminals, possibly empty. Its language contains every all-terminal string reachable from the start.

The tuple below is a compact reference for those parts:

```formula reference
G = (V, Σ, R, S)
A → w   with A ∈ V
L(G) = { w ∈ Σ* : S ⇒* w }
where
G: the grammar
V: a finite set of variables (non-terminals), such as S, E, T
Σ: sigma, the alphabet: a finite set of terminals (the actual characters), sharing nothing with V
R: a finite set of rules, each of the form A → w
S: the start variable, one particular member of V
A: the single variable on the left of a rule
w: any string of variables and terminals on the right of a rule (possibly the empty string ε); in L(G), a string of terminals only
→: "may be rewritten as"
∈: is a member of
Σ*: sigma-star: every finite string of terminals, including the empty string ε
⇒*: derives in zero or more rewriting steps
L(G): the language of G: the set of terminal strings that S can be rewritten into
{ … : … }: set-builder notation: the set of all w that satisfy the condition after the colon
In words: a grammar has variables, terminals, rules that each rewrite one variable, and a start variable; its language is every all-terminal string you can reach from the start.
```

The **variables** (non-terminals) are placeholders that still need rewriting. The **terminals** are the real characters of the finished string. Each **rule** rewrites one variable. For the equal-block grammar from the previous unit, the variable set contains just the start symbol, the terminal alphabet contains the letters a and b, and the rule set holds the two displayed rules. A language is **context-free** if some CFG generates it.

> [!note] Why "context-free"?
> The left-hand side of every rule is a single variable. So you may rewrite A no matter what surrounds it: its context is irrelevant. *Context-sensitive* grammars can restrict a replacement to specified surrounding symbols: for example, rewriting a variable only when it lies between an a and a b. Their rules do not shorten the string, apart from a controlled start-to-empty exception in conventions admitting the empty string. Those are strictly more powerful.

Every regular language is context-free (a DFA translates directly into a grammar: each transition becomes a terminal followed by the variable corresponding to the destination state, and each accepting state gets an empty-string rule), but not the other way round: `aⁿbⁿ` is context-free and not regular.

## Key takeaways

- A CFG has finite variable and terminal sets, finite productions and one start variable.
- A production rewrites one variable regardless of its surroundings.
- Every regular language is context-free; equal unbounded a and b blocks show the converse fails.

## Further reading

- [Sipser: grammars, parse trees and pushdown automata](https://ocw.mit.edu/courses/18-404j-theory-of-computation-fall-2020/resources/mit18_404f20_lec4-1/)
