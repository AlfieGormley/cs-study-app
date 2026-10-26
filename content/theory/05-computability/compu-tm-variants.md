---
id: compu-tm-variants
title: Equivalent machine models and finite runs
level: intermediate
minutes: 3
summary: Multiple tapes and nondeterminism preserve recognisability; simulations may change running time.
sourceLesson: compu-turing-machines
---

## Robustness: the variants are all equivalent

The definition seems arbitrary. Why one tape? Why not stay put? The remarkable fact is that the reasonable variants all recognise exactly the same languages:

| Variant | Simulated by 1-tape TM |
|---|---|
| Stay-put moves | trivially (R then L) |
| Two-way infinite tape | fold it in half |
| A fixed number k of tapes | Standard quadratic step bound when the run is at least as long as the input |
| Nondeterministic | Fair search; exponential upper bound in a branch-time bound |
| Random-access machine with suitable bit-cost or bounded-word operations | polynomial slowdown |

The multi-tape simulation stores all the tapes on one, separated by markers, with a marker for each simulated head. To simulate a step, it sweeps the representation to collect the scanned symbols and update them. The representation grows as the simulated run reaches more cells, so the sweep gets longer. For a fixed number of tapes, this gives a quadratic upper bound in simulated steps, provided the run is at least as long as the input. The reference formula records that bound:

```formula reference
T_1(t) = t × O(t) = O(t^2)
where
T_1(t): the number of single-tape steps needed to simulate the multi-tape machine
t: the number of steps the multi-tape (k-tape) machine takes, at least the input length
O(…): big-O: grows no faster than the expression inside, up to a constant factor
In words: each simulated step sweeps a representation whose length grows with the simulated runtime, giving a quadratic upper bound on the total simulation work.
```

The important distinction is between computability and cost: simulation preserves what can be solved, but need not preserve runtime. This polynomial overhead also means that single-tape and fixed-multitape machines agree on which problems have polynomial-time algorithms. It is an upper bound for a general simulation, not a lower bound for every particular problem.

Nondeterministic TMs are simulated by trying all branches **breadth-first**. Depth-first would be wrong: it could follow an infinite branch forever while an accepting branch sits elsewhere. This matters for power, not just speed. This simulation establishes an upper bound, not a proof that exponential slowdown is necessary. Whether every language accepted in nondeterministic polynomial time has a deterministic polynomial-time decider is P versus NP.

## Why this model, when no one builds one

Turing-machine notation is mainly a mathematical and educational model rather than an ordinary application language. The model's value is that it is **simple enough to prove things about** and **expressive enough to model effective computation**. A modern CPU is a finite-state machine (registers, caches) attached to a large memory. With an effective instruction set and suitably costed operations, unbounded memory gives a model equivalent in computability to a TM; polynomial simulation claims also require an appropriate cost model. So a theorem like "no TM can decide X" becomes "no effective procedure can decide X for all inputs in the unbounded model", using the Church–Turing thesis.

## Pitfalls

- **Reject is not loop.** A recogniser may never answer "no". If you want a decider, you must prove it halts on every input.
- **The tape is infinite, but each halting run uses finitely much.** The head starts on one cell and reaches at most one new cell per step. Each step also writes at most one cell, in addition to the initially written input.
- **Implicit reject** (no matching rule) is a common convention, as in the simulator above. Be clear which convention a textbook uses.

A deterministic machine that repeats its complete configuration repeats its future behaviour too. A halting run therefore cannot revisit the same configuration, although it may revisit individual states or tape cells many times.

## Key takeaways

- Multiple tapes and nondeterminism preserve recognisability; simulations may change running time.
- Fair breadth-first search avoids getting trapped on a single infinite branch.
- A finite run visits finitely many cells even though arbitrarily much tape is available.

## Further reading

- [Sipser: TM variants and the Church–Turing thesis](https://ocw.mit.edu/courses/18-404j-theory-of-computation-fall-2020/resources/mit18_404f20_lec6-1/)
