---
id: auto-dfa-partial-complement
title: Partial DFAs and safe complementation
level: basic
minutes: 3
sourceLesson: auto-dfa
summary: A missing transition rejects through an implicit dead state.
---

## Dead states and partial DFAs

Strictly, the transition function must be defined for every (state, symbol) pair: it must be **total**. A DFA where that holds is a **complete DFA**. In practice people draw **partial DFAs** and leave missing arrows implied. A missing arrow means "go to a **dead state**" (also called a trap or sink): a non-accepting state that loops to itself on every symbol. Once you fall in, you can never accept.

Here is a DFA for unsigned decimals such as `42` and `3.14`: one or more digits, optionally followed by a dot and one or more digits. `d` stands for an ASCII digit, 0 through 9.

| State | on d | on . |
|---|---|---|
| → S | WHOLE | dead |
| WHOLE (accept) | WHOLE | DOT |
| DOT | FRAC | dead |
| FRAC (accept) | FRAC | dead |

- `3.14`: S → WHOLE → DOT → FRAC → FRAC. Accept.
- `3.`: ends in DOT, which is not accepting. Reject.
- `.5`: S on `.` goes to dead. Reject.
- `1.2.3`: FRAC on `.` goes to dead. Reject.

This is exactly the regex `[0-9]+(\.[0-9]+)?`, and lexers for programming languages are built from automata like this one for every token type.

## Complementing safely

To recognise the complement over the same alphabet, first make all missing transitions explicit by adding a rejecting dead state that loops on every symbol. Then swap accepting and non-accepting states, including the dead state. For the decimal machine, `.5` must be accepted by the complement even though its first dot makes the original partial run stop.

## Key takeaways
- A missing transition rejects through an implicit dead state.
- Make the transition function total before swapping accepting status to form a complement.

## Further reading
- [MIT: finite automata and regular expressions](https://ocw.mit.edu/courses/18-404j-theory-of-computation-fall-2020/resources/lecture-1-introduction-finite-automata-regular-expressions/)
