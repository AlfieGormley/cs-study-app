---
id: compu-pda-equivalence
title: Grammar–PDA equivalence and compiler boundaries
level: intermediate
minutes: 3
summary: Grammars and pushdown recognisers define the same language class.
sourceLesson: compu-pda-pumping
---

A grammar generates terminal strings; the previous unit’s PDA simulator recognises strings by exploring stack configurations. The equivalence theorem connects those two descriptions and explains which compiler checks fit this model.

## PDAs and CFGs are equivalent

**Theorem.** A language is context-free if and only if some PDA recognises it.

- **From CFG to PDA.** Push the start variable. Repeatedly: if the top is a variable A, nondeterministically replace it with the right-hand side of a grammar rule for that variable; if the top is a terminal, pop it while reading the same input character. Accept on an empty stack only after all input has been consumed. The stack holds the not-yet-matched part of a leftmost derivation.
- **From PDA to CFG.** First normalise the PDA so acceptance occurs with an empty stack and moves push or pop one symbol. Variables A_pq then describe computations from state p with an empty stack to state q with an empty stack. Pair matching pushes and pops and concatenate such balanced subcomputations. This sketch omits the full normalisation and rule construction.

So grammars and pushdown automata are two views of the same class, the way regular expressions and DFAs are.

## Where this shows up

- **Nested syntax** in JSON, XML and programming languages motivates stack parsing; complete language rules may require further checks. For a deterministic context-free grammar, an LR parser is a DPDA whose stack holds states and symbols.
- **Not everything in a language is context-free.** "Every variable is declared before use" resembles { w c w }, which is not context-free. Compilers check it in a separate semantic pass with a symbol table. C's `typedef` makes even *parsing* context-dependent (`a * b;` is a declaration if `a` is a type name), which motivates techniques such as the "lexer hack" to supply symbol-table information during parsing; not every C compiler uses the same technique.
- **Static analysis** of recursive programs uses pushdown models, because matching calls with returns is a nesting problem.

## Key takeaways

- CFG generation and nondeterministic PDA recognition define the same languages.
- Deterministic context-free languages admit suitable LR grammars under end-of-input conventions.
- Name binding and declaration checks require semantic analysis beyond ordinary context-free syntax.

## Further reading

- [Sipser: grammars, parse trees and pushdown automata](https://ocw.mit.edu/courses/18-404j-theory-of-computation-fall-2020/resources/mit18_404f20_lec4-1/)
- [Context-free language closure properties — further reference](https://en.wikipedia.org/wiki/Context-free_language)
