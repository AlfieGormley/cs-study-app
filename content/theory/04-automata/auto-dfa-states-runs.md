---
id: auto-dfa-states-runs
title: DFA states, transitions and runs
level: basic
minutes: 5
sourceLesson: auto-dfa
summary: A complete DFA specifies exactly one transition for every state and symbol.
---

## The formal definition

Mathematicians describe a DFA by listing its five ingredients in a fixed order, a 5-tuple. Any DFA, however big, is fully pinned down by these five things:

```formula
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

For the even-parity machine in the next parity-cycle unit, the five parts are:

```formula
Q = {E, O}     Σ = {0, 1}
q₀ = E         F = {E}
δ(E, 1) = O    δ(O, 1) = E
δ(E, 0) = E    δ(O, 0) = O
where
Q: the set of automaton states
E: the state meaning "an even number of 1s so far"
O: the state meaning "an odd number of 1s so far"
Σ: the input alphabet, here the two bits
q₀: the start state
F: the set of accepting states
δ: the transition function: δ(state, symbol) is the next state
{ }: the set of the items listed inside
In words: two states, E and O; a 1 swaps between them and a 0 leaves the state alone; start in E, and accept if you end in E.
```

In words, the five parts of any DFA are:

- a finite set of **automaton states**;
- the **input alphabet**;
- the **transition function**, which, given a state and a symbol, names exactly one next state;
- the **start state**;
- the **accepting states** (final states).

To run it on a string, begin in the start state and apply the transition function once per symbol. If you finish in an accepting state, the DFA **accepts**; otherwise it **rejects**. The set of strings it accepts is called the language of M:

```formula
L(M) = { w ∈ Σ* : δ̂(q₀, w) ∈ F }
where
L(M): the language recognised by the machine M: the set of strings it accepts
M: the DFA
{ w ∈ Σ* : … }: set-builder notation: the set of all strings w in Σ* that make the condition after the colon true. The colon reads "such that"
w: any string over the alphabet
Σ*: every finite string over the alphabet Σ, including the empty string
δ̂: "delta hat": the extended transition function. δ̂(q, w) is the state you end in after starting at q and applying δ once per symbol of w, left to right. For the empty string it stays put
q₀: the start state
∈: is an element of
F: the set of accepting states
In words: the language of M is exactly the set of strings that, read from the start state, leave the machine in an accepting state.
```

For example, the even-parity machine reads 1011 and finishes in O (traced in the next parity-cycle unit). O is not accepting, so 1011 is not in the machine's language.

"Deterministic" means there is never a choice: for every state and every symbol there is exactly one move. So a DFA's run on a given string is a single path, and it takes exactly n steps for a string of length n.

## Key takeaways
- A complete DFA gives exactly one transition for every state and input symbol.
- A run applies that function once per symbol and tests the final state for acceptance.

## Further reading
- [MIT: finite automata and regular expressions](https://ocw.mit.edu/courses/18-404j-theory-of-computation-fall-2020/resources/lecture-1-introduction-finite-automata-regular-expressions/)
