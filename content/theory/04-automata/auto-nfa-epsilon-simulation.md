---
id: auto-nfa-epsilon-simulation
title: Epsilon closure and free transitions
level: intermediate
minutes: 3
sourceLesson: auto-nfa
summary: Epsilon closure includes the starting states and every state reachable without consuming input.
---

## ε-transitions and ε-closure

An ε-transition lets the machine change state for free. They make it easy to glue machines together: "do this OR that" becomes a start state with ε-arrows into two sub-machines.

The **ε-closure** of a set of states is that set plus everything reachable from it using only ε-arrows (zero or more of them). When simulating, you take the closure at the start and after every symbol.

Following zero arrows is allowed, so closure always includes the original states. Follow the arrows in their direction and keep going until no new states appear; an arrow labelled with a real symbol is excluded.

Example: accept strings of a's whose length is divisible by 2 **or** by 3.

Accept the input if either cycle returns to its accepting position. The empty string qualifies because both cycles start there.

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

Before reading anything, the current set contains s, p0 and r0. Since p0 and r0 accept, the empty string is accepted.

After one a the set is {p1, r1}: reject. After two, {p0, r2}: accept. The accepted lengths are 0, 2, 3, 4, 6, 8, 9, 10, 12, and so on.

## Key takeaways
- Epsilon closure includes every starting state and all states reachable without consuming input.
- Epsilon branches combine the divisible-by-two and divisible-by-three languages using existential acceptance.

## Further reading
- [MIT: nondeterminism and closure properties](https://ocw.mit.edu/courses/18-404j-theory-of-computation-fall-2020/resources/mit18_404f20_lec2-1/)
- [Rabin and Scott: finite automata (1959)](https://www.cse.chalmers.se/~coquand/AUTOMATA/rs.pdf)
