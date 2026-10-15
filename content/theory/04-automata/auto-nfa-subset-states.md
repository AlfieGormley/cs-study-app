---
id: auto-nfa-subset-states
title: Building reachable subset states
level: intermediate
minutes: 4
sourceLesson: auto-nfa
summary: Each DFA state represents a set of possible NFA states.
---

## The subset construction

The earlier NFA simulator already runs a DFA in disguise. Its "state" at each moment is a set of NFA states, and there are only finitely many such sets. So build a DFA whose states are those sets. The rules, in symbols:

```formula
S₀ = E({q₀})
T = E( ⋃_{q ∈ S} δ(q, c) )
S ∈ F_D   if   S ∩ F ≠ ∅
|Q_D| ≤ 2^m
where
S₀: the start state of the new DFA
E: the ε-closure: a set of states plus everything reachable from it by ε-arrows alone
q₀: the start state of the NFA
S: one DFA state, which is a set of NFA states
q: one NFA state inside S
c: one input symbol
δ: the NFA's transition function: δ(q, c) is the set of states q can move to on c
⋃_{q ∈ S}: big union: gather the results for every q in S into a single set
∈: is an element of
T: the DFA state reached from S on symbol c
F: the NFA's accepting states
∩: intersection: the states in both sets
≠: is not equal to
∅: the empty set
F_D: the DFA's set of accepting states
Q_D: the DFA's set of states
| |: vertical bars around a set mean its cardinality: the number of elements
≤: is less than or equal to
m: the number of NFA states; an integer count, non-negative unless a positive lower bound is stated
2^m: 2 to the power m: how many subsets a set of m states has
In words: start from the closure of the NFA's start state; from any set, on any symbol, move every member and take the closure of the result; a set accepts if it contains at least one NFA accepting state. Since each DFA state is a subset of the m NFA states, there can be at most 2^m of them.
```

As a procedure:

1. Make the closure of the NFA's start state the DFA start state.
2. For each unprocessed DFA state and each symbol, compute the next set with the rule above. Add it if it is new.
3. Mark a DFA state accepting if it contains any NFA accepting state.
4. Stop when no new sets appear. Only build sets you can actually reach.

This is also called the **powerset construction**.

### Worked example: ending in ab

Start with {0}.

| DFA state | on a | on b | Accept? |
|---|---|---|---|
| → {0} | {0, 1} | {0} | no |
| {0, 1} | {0, 1} | {0, 2} | no |
| {0, 2} | {0, 1} | {0} | yes |

Only 3 of the eight (two to the power three) possible subsets are reachable. Rename them and you have an ordinary DFA:

| DFA state | Meaning | on a | on b |
|---|---|---|---|
| → A = {0} | no progress | B | A |
| B = {0, 1} | just saw a | B | C |
| C = {0, 2} (accept) | just saw ab | B | A |

### Worked example: the ε-NFA

For "length divisible by 2 or 3", the reachable subsets are {s, p0, r0}, {p1, r1}, {p0, r2}, {p1, r0}, {p0, r1}, {p1, r2} and {p0, r0}. That is 7 DFA states: the start, then six sets that track the length's remainder after dividing by 2 and its remainder after dividing by 3, together. The start and {p0, r0} turn out to be equivalent, so the minimal DFA has 6 states: one per remainder of the length after dividing by 6.

## Key takeaways
- Each DFA state represents a set of possible NFA states.
- A subset accepts if any member accepts; the empty subset is a dead state when reachable.

## Further reading
- [MIT: nondeterminism and closure properties](https://ocw.mit.edu/courses/18-404j-theory-of-computation-fall-2020/resources/mit18_404f20_lec2-1/)
- [Rabin and Scott: finite automata (1959)](https://www.cse.chalmers.se/~coquand/AUTOMATA/rs.pdf)
