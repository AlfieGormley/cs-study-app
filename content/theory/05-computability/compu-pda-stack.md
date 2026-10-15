---
id: compu-pda-stack
title: A finite control with an unbounded stack
level: intermediate
minutes: 4
summary: A PDA reads input and manipulates only the top of its stack.
sourceLesson: compu-pda-pumping
---

A grammar *generates* strings. To *recognise* them you want a machine. For regular languages that machine is a finite automaton. For context-free languages it is a finite automaton with one extra piece of memory: an unbounded **stack**.

This unit defines the **pushdown automaton** (PDA). The following units simulate it and prove where its power runs out.

## Intuition: a stack is exactly enough for nesting

To check `aⁿbⁿ`, push a token for each `a`, then pop one for each `b`. Accept if the stack empties exactly when the input ends.

```
input:  a  a  b  b
stack: A$ AA$ A$ $   (after each symbol)
push A, push A, pop, pop -> $ remains
then pop $ on an epsilon move: accept
```

The stack gives unbounded memory, but with a strict restriction: you may only look at the top. That is exactly what nesting needs, because the most recently opened bracket is the first one that must close. It is also exactly how your program's call stack works.

## The formal definition

One PDA convention is a 6-tuple (a list of six parts in a fixed order), starting with an empty stack. The examples abbreviate an initial epsilon move that pushes the bottom marker $, and the simulator starts after that move:

```formula
P = (Q, Σ, Γ, δ, q_0, F)
q_0 ∈ Q     F ⊆ Q
δ(q, a, X) = { (r, Y), … }
a, X → Y
where
P: the pushdown automaton
Q: a finite set of states
Σ: sigma, the input alphabet: the characters the input string may contain
Γ: gamma, the stack alphabet: the symbols that may be pushed (it may differ from Σ)
δ: delta, the transition function: given the current situation, it lists the allowed moves
q_0: the start state
F: the set of accepting states
∈: is a member of
⊆: is a subset of: every member of F is also in Q
q, r: states, the current one and the next one
a: the input character read on this move, or ε to read nothing
X: the symbol popped from the top of the stack, or ε to leave the stack alone
Y: the string pushed in its place, or ε to push nothing
ε: epsilon, the empty string: "nothing" on that side of the move
{ (r, Y), … }: a set of possible moves, each a pair of next state and string to push
→: on the diagram label, separates what is read and popped (left) from what is pushed (right)
In words: a PDA is a finite set of states plus a stack; each move reads an input character (or nothing), pops a stack symbol (or nothing), pushes a string and changes state.
```

So δ(q, a, X) means "in state q, reading input a with X on top of the stack, the machine may move to r and replace X with Y". The diagram labels use that same read/pop/push convention. For example, the a-labelled loop below reads an a, pops nothing and pushes an A.

The standard PDA is **nondeterministic**: δ returns a *set* of moves, and the PDA accepts if *any* sequence of choices ends in an accepting state with all input read.

A PDA for `aⁿbⁿ` uses a bottom marker `$`:

```
     a,ε→A        b,A→ε
      ┌─┐          ┌─┐
      ▼ │          ▼ │
  ──▶ p ── ε,ε→ε ─▶ q ── ε,$→ε ─▶ (f)
```

Start with `$` on the stack. In state p, push an A per `a`. Jump (nondeterministically) to q, pop an A per `b`. When `$` is on top, move to accepting state f.

## Key takeaways

- A PDA reads input and manipulates only the top of its stack.
- Acceptance requires all input consumed; this module uses final-state acceptance.
- Nondeterministic acceptance needs one successful branch.

## Further reading

- [Sipser: grammars, parse trees and pushdown automata](https://ocw.mit.edu/courses/18-404j-theory-of-computation-fall-2020/resources/mit18_404f20_lec4-1/)
