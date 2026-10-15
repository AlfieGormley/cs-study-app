---
id: auto-nfa-epsilon-simulation
title: Epsilon closure and free transitions
level: intermediate
minutes: 4
sourceLesson: auto-nfa
summary: Epsilon closure includes the starting states and every state reachable without consuming input.
---

## ε-transitions and ε-closure

An ε-transition lets the machine change state for free. They make it easy to glue machines together: "do this OR that" becomes a start state with ε-arrows into two sub-machines.

The **ε-closure** of a set of states is that set plus everything reachable from it using only ε-arrows (zero or more of them). When simulating, you take the closure at the start and after every symbol.

```formula
E(S) = { r : q ⇒_ε r for some q ∈ S }
S ⊆ E(S)
where
E(S): the ε-closure of S, written ε-closure(S) in the prose and code
S: a set of NFA states
q: a state in S
r: a stand-in for any state of the NFA
ε: Greek epsilon: the empty string; an ε-arrow is a move that reads no input
⇒_ε: "can reach using only ε-arrows": following zero or more ε-arrows leads from the left state to the right one
∈: is an element of
{ r : … }: the set of all states r that make the condition after the colon true
⊆: is a subset of: every state of S is in its own closure, because following zero ε-arrows is allowed
In words: the ε-closure of a set of states is every state you can reach from it without reading any input, including the states you started in.
```

Example: accept strings of a's whose length is divisible by 2 **or** by 3.

```formula
L = { a^k : k mod 2 = 0 or k mod 3 = 0 }
where
L: the language being recognised
a: the only input symbol
a^k: k copies of a in a row, for example a^3 = aaa; a^0 is the empty string
k: the length of the string, a whole number 0, 1, 2, …
mod: the remainder after whole-number division, so 9 mod 2 = 1
{ … : … }: the set of all strings of that form that make the condition after the colon true
In words: accept a run of a's when its length is even, or a multiple of 3, or both.
```

```
      ε           a
 (s) ---> ((p0)) <---> (p1)
  |
  |   ε          a        a
  +-----> ((r0)) ---> (r1) ---> (r2)
             ^                   |
             +-------- a --------+
```

The start state s has ε-arrows to a 2-cycle and a 3-cycle.

```formula
E({s}) = {s, p0, r0}
where
E: the ε-closure: every state reachable without reading input
s: the start state
p0, r0: the accepting "count is 0 so far" states of the 2-cycle and the 3-cycle
{ }: the set of the states listed inside
In words: before reading anything, the machine is already in s, p0 and r0 at once. Two of those accept, so the empty string is accepted.
```

After one a the set is {p1, r1}: reject. After two, {p0, r2}: accept. The accepted lengths are 0, 2, 3, 4, 6, 8, 9, 10, 12, and so on.

## Key takeaways
- Epsilon closure includes every starting state and all states reachable without consuming input.
- Epsilon branches combine the divisible-by-two and divisible-by-three languages using existential acceptance.

## Further reading
- [MIT: nondeterminism and closure properties](https://ocw.mit.edu/courses/18-404j-theory-of-computation-fall-2020/resources/mit18_404f20_lec2-1/)
- [Rabin and Scott: finite automata (1959)](https://www.cse.chalmers.se/~coquand/AUTOMATA/rs.pdf)
