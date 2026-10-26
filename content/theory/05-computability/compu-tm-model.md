---
id: compu-tm-model
title: Read-write tapes, recognisers and deciders
level: intermediate
minutes: 5
summary: A TM can revisit and rewrite any cell reached by its head.
sourceLesson: compu-turing-machines
---

A PDA's memory is a stack: unbounded, but you can only touch the top. Remove that restriction, so the machine can move freely over its memory and rewrite any cell, and you get a **Turing machine** (TM).

Alan Turing described it in 1936 by imagining a human clerk working with pencil and paper. The clerk has a finite rule book (states), looks at one square at a time, may write or erase a symbol, and may move one square left or right. Everything you would call "an algorithm" can be performed this way. That claim is the subject of the later lessons on the Church–Turing thesis. This unit is about the machine itself.

## The machine

```
   ... _  _  1  0  1  1  _  _ ...   tape
                ▲
             ┌──┴──┐
             │  q  │  finite control
             └─────┘
```

- An **infinite tape** divided into cells. The input is written on it at the start; every other cell holds the blank `_`.
- A **head** that reads one cell, writes a symbol there, and moves one cell left (L) or right (R).
- A **finite control**: the current state.

The finite transition table chooses a write, a head movement and a next state from the current state and scanned symbol. Input symbols are also tape symbols; the blank and extra markers belong only to the tape alphabet. Accept and reject are distinct halting states with no outgoing moves. The seven-part notation below records these ingredients as a reference:

```formula reference
M = (Q, Σ, Γ, δ, q_0, q_accept, q_reject)
Σ ⊆ Γ     _ ∈ Γ     _ ∉ Σ
Q′ = Q − {q_accept, q_reject}
δ: Q′ × Γ → Q × Γ × {L, R}
δ(q, a) = (r, b, D)
where
M: the Turing machine
Q: a finite set of states
Σ: sigma, the input alphabet: the characters an input may contain
Γ: gamma, the tape alphabet: everything that may ever be written on the tape, including Σ, the blank and extra markers such as X
δ: delta, the transition function: the machine's rule book
q_0: the start state
q_accept: the accepting state; entering it stops the machine with "yes"
q_reject: the rejecting state, different from q_accept; entering it stops the machine with "no"
_: the blank symbol, filling every cell not holding input
⊆: is a subset of: every member of Σ is also in Γ
∈, ∉: is a member of, is not a member of
Q′: the working states: every state except the two halting ones (halting states have no rules)
−: set difference: Q with those two states removed
{ }: curly braces: the set of the things listed inside
→: in the line δ: Q′ × Γ → Q × Γ × {L, R}, the arrow separates what δ takes as input (left) from what it gives back (right)
×: Cartesian product: all ordered pairs (or triples) with one item from each set
L, R: the two head moves: one cell left, one cell right
q, r: the current state and the next state
a, b: the symbol read under the head and the symbol written in its place
D: the direction the head then moves, L or R
In words: a TM is a finite set of states plus a tape; in each working state, the symbol under the head decides what to write, which way to move and which state to enter next.
```

In the next unit's binary increment machine, the carry state on a one uses this move: write zero, move left and stay in the carry state. The Python dictionaries list the three actions in the order write, move, next state.

A **TM configuration** is a snapshot: state, tape contents and head position. It is often written `1 0 q 1 1`, meaning the tape is `1011`, the machine is in state q, and the head is on the third symbol.

> [!note] Three outcomes, not two
> On a given input a TM can **accept**, **reject**, or **loop forever**. A DFA completes one transition per input symbol. A PDA can have infinite epsilon-move branches; a decision algorithm for CFL membership still exists. A TM has no such guarantee. That third outcome is the source of every undecidability result in this module.

## Recognisers and deciders

- A TM M **recognises** language L if M accepts exactly the strings in L. On strings outside L it may reject *or loop*. Such languages are **Turing-recognisable** (also called recursively enumerable).
- M **decides** L if it recognises L *and* halts on every input. Such languages are **decidable** (also called recursive languages).

Every decidable language is recognisable. Whether the reverse holds is the question addressed by the later undecidability lessons. (It does not.)

## Key takeaways

- A TM can revisit and rewrite any cell reached by its head.
- Accept and reject halt; an infinite run is a third outcome.
- A recogniser may loop on non-members, whereas a decider must halt on every input.

## Further reading

- [Sipser: CFL pumping lemma and Turing machines](https://ocw.mit.edu/courses/18-404j-theory-of-computation-fall-2020/resources/mit18_404f20_lec5-1/)
