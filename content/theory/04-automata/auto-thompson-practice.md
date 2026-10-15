---
id: auto-thompson-practice
title: Compiler choices and regex pitfalls
level: intermediate
minutes: 3
sourceLesson: auto-thompson
summary: Counted repetition can make a compact pattern compile into a large machine.
---

The earlier construction builds epsilon-NFA fragments with one entry and one exit. Here we examine implementation choices and the boundary cases those fragments must handle.

## Where this shows up

- **lex and flex** compile token patterns into an NFA in this way, then determinise it ahead of time into a table-driven DFA. GNU grep may select DFA, fixed-string search or other matching strategies depending on options and pattern features.
- **RE2, Go's `regexp` and Rust's `regex`** compile into an NFA-like program of instructions (match a byte, split into two matching threads, jump) that is Thompson's NFA in a different notation. Russ Cox's articles show this "Pike VM" view.
- **Alternatives** exist. The Glushkov (or position) automaton has no ε-arrows and one state per symbol occurrence plus a start, which suits bit-parallel matching. **Brzozowski derivatives** build a DFA directly from the regex by repeatedly asking "what is left to match after reading this symbol?"

## Pitfalls

- **Precedence bugs.** `^ab|cd$` means `(^ab)|(cd$)`, not `^(ab|cd)$`. Many real validation bugs come from this.
- **Counted repetition is expansion.** `(a|b){1000}` becomes a thousand copies of the fragment, and `x{1,1000}` likewise. RE2 limits counted repetitions for this reason: its syntax rejects `{n}` when n exceeds 1000. Other engines have different limits and representations.
- **Star of something that matches the empty string.** `(a*)*` is legal, but the NFA has ε-cycles. Set simulation handles that fine because ε-closure visits each state once. A naive recursive backtracker without a zero-progress guard may loop; practical engines commonly detect empty repetitions, although other patterns can still cause excessive backtracking.

> [!note] Evidence gap
> A previous fixed grep throughput figure is omitted because no reproducible hardware, input and tool configuration was available.

## Key takeaways
- Counted repetition can make a compact pattern compile into a large machine.
- Visited-state epsilon closure terminates even when nested stars introduce epsilon cycles.

## Further reading
- [Russ Cox: simple and fast regular-expression matching](https://swtch.com/~rsc/regexp/regexp1.html)
- [MIT: regexes to finite automata](https://ocw.mit.edu/courses/18-404j-theory-of-computation-fall-2020/resources/mit18_404f20_lec2-1/)
