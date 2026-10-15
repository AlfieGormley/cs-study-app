---
id: compu-tm-variants
title: Equivalent machine models and finite runs
level: intermediate
minutes: 5
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

The multi-tape simulation stores all k tapes on one, separated by markers, with a dot over each simulated head. Each simulated step sweeps the used tape once, which is O(t) cells after t steps:

```formula
T_1(t) = t × O(t) = O(t^2)
where
T_1(t): the number of single-tape steps needed to simulate the multi-tape machine
t: the number of steps the multi-tape (k-tape) machine takes, at least the input length
O(…): big-O: grows no faster than the expression inside, up to a constant factor
In words: t simulated steps, each costing one sweep over at most about t cells, give a quadratic slowdown.
```

For example, let n be the input length. A three-tape machine taking a quadratic number of steps has an O(n⁴) single-tape simulation under this theorem. Slower, but still polynomial, which is why the variants agree on which problems are solvable at all.

Nondeterministic TMs are simulated by trying all branches **breadth-first**. Depth-first would be wrong: it could follow an infinite branch forever while an accepting branch sits elsewhere. This matters for power, not just speed. This simulation establishes an upper bound, not a proof that exponential slowdown is necessary. Whether every language accepted in nondeterministic polynomial time has a deterministic polynomial-time decider is P versus NP.

## Why this model, when no one builds one

Turing-machine notation is mainly a mathematical and educational model rather than an ordinary application language. The model's value is that it is **simple enough to prove things about** and **expressive enough to model effective computation**. A modern CPU is a finite-state machine (registers, caches) attached to a large memory. With an effective instruction set and suitably costed operations, unbounded memory gives a model equivalent in computability to a TM; polynomial simulation claims also require an appropriate cost model. So a theorem like "no TM can decide X" becomes "no effective procedure can decide X for all inputs in the unbounded model", using the Church–Turing thesis.

## Pitfalls

- **Reject is not loop.** A recogniser may never answer "no". If you want a decider, you must prove it halts on every input.
- **The tape is infinite, but each halting run uses finitely much.** The bounds are in the formula below.
- **Implicit reject** (no matching rule) is a common convention, as in the simulator above. Be clear which convention a textbook uses.

```formula
C_visit ≤ t + 1
C_used ≤ |w| + t + 1
where
C_visit: the number of distinct cells the head visits
C_used: the number of cells involved at all, counting cells that held input
t: the number of steps (single-cell moves) in the run
|w|: the length of the input w, in symbols
≤: is at most
In words: the head starts on one cell and reaches at most one new cell per step, so a finite run touches finitely many cells.
```

For a run of ten steps on a 4-symbol input, the head visits at most 11 cells, and at most 15 cells are involved.

## Key takeaways

- Multiple tapes and nondeterminism preserve recognisability; simulations may change running time.
- Fair breadth-first search avoids getting trapped on a single infinite branch.
- A finite run visits finitely many cells even though arbitrarily much tape is available.

## Further reading

- [Sipser: TM variants and the Church–Turing thesis](https://ocw.mit.edu/courses/18-404j-theory-of-computation-fall-2020/resources/mit18_404f20_lec6-1/)
