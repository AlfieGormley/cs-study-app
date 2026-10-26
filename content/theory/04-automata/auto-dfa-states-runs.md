---
id: auto-dfa-states-runs
title: DFA states, transitions and runs
level: basic
minutes: 3
sourceLesson: auto-dfa
summary: A complete DFA specifies exactly one transition for every state and symbol.
---

## What the machine needs to remember

A DFA carries one current state through the input. Each state summarises the past well enough to decide what to do with the next symbol. For even parity, it needs only "even so far" or "odd so far", not the entire string.

Its five ingredients are the finite set of **automaton states**, an **input alphabet**, a **transition function**, one **start state** and a set of **accepting states**. The transition function gives exactly one next state for every state and input symbol.

Begin each independent run in the start state. Read one symbol and follow its transition, then repeat. Test acceptance only after all input has been read. Visiting an accepting state midway does not end the run; later input can move elsewhere. On empty input, the start state itself decides.

> [!analogy] Real-world analogy: A board-game counter
> A counter marks your current square; a drawn card tells you where to move next.
>
> **How it maps:** The square represents the current state and each card an input symbol. A fixed rule tells you the next square. The finishing square determines acceptance.
>
> **Where it stops:** A DFA has no dice or player choice, and its verdict is checked when the input ends, not as soon as it visits a special square.

## Reference notation

Mathematicians describe a DFA by listing its five ingredients in a fixed order, a 5-tuple. Any DFA, however big, is fully pinned down by these five things:

```formula reference
M = (Q, Σ, δ, q₀, F)
δ : Q × Σ → Q
q₀ ∈ Q
F ⊆ Q
where
M: the machine, the DFA being described
( , , , , ): round brackets with commas: an ordered list of components (a tuple); here there are five, so it is a 5-tuple
Q: the finite set of automaton states
Σ: capital Greek sigma: the input alphabet, the finite set of symbols the DFA can read
δ: Greek delta: the transition function. δ(q, c) is the one state to move to from state q on reading symbol c
×: the Cartesian product: Q × Σ is the set of every (state, symbol) pair
→: maps to: δ takes a pair from the set on the left and returns one element of the set on the right
q₀: "q nought": the start state, where every run begins
∈: is an element of
F: the set of accepting states (also called final states)
⊆: is a subset of: every element of F is also in Q; F may be empty or all of Q
In words: a DFA has a finite set of states, an alphabet, a rule giving exactly one next state for every state and symbol, one start state, and a chosen set of accepting states.
```

For the even-parity machine in the next unit:

The parity states are E (even so far) and O (odd so far). Start in E. A 1 swaps states; a 0 leaves the state alone. Only E accepts.

The language of a DFA is the set of all strings whose complete runs end in accepting states.

For example, the even-parity machine reads 1011 and finishes in O (traced in the next parity-cycle unit). O is not accepting, so 1011 is not in the machine's language.

"Deterministic" means there is never a choice: for every state and every symbol there is exactly one move. So a DFA's run on a given string is a single path, and it takes exactly n steps for a string of length n.

## Key takeaways
- A complete DFA gives exactly one transition for every state and input symbol.
- A run applies that function once per symbol and tests the final state for acceptance.

## Further reading
- [MIT: finite automata and regular expressions](https://ocw.mit.edu/courses/18-404j-theory-of-computation-fall-2020/resources/lecture-1-introduction-finite-automata-regular-expressions/)
