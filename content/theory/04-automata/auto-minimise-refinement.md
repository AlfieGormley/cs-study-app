---
id: auto-minimise-refinement
title: Partition refinement and table filling
level: advanced
minutes: 5
sourceLesson: auto-minimisation
summary: Remove unreachable states before counting the minimal machine.
---

## Worked example

This DFA accepts strings over {a, b} that end in ab, but it was built carelessly:

| State | on a | on b |
|---|---|---|
| → A | B | A |
| B | D | C |
| C (accept) | D | A |
| D | B | E |
| E (accept) | B | A |
| F | C | F |

### Step 1: remove unreachable states

Search from A: A reaches B; B reaches D and C; D reaches E. Nothing reaches F, so delete it. Five states remain.

### Step 2: partition refinement (Moore's algorithm)

Start from the coarsest guess, two blocks: accepting and non-accepting. Then repeatedly split any block whose members disagree about which block they go to on some symbol.

Round 0:

The initial non-accepting block contains A, B and D. The accepting block contains C and E. They must remain separate because the empty continuation already distinguishes the two verdicts.

Round 1. For each state, note which block each transition lands in:

```
     on a   on b
A    N      N
B    N      Acc
D    N      Acc
C    N      N
E    N      N
```

A disagrees with B and D (its b goes to N, theirs to Acc), so split N into {A} and {B, D}. C and E agree, so they stay together.

```
{A}   {B, D}   {C, E}
```

Round 2. Recheck with the new blocks. B goes to D on a and C on b; D goes to B on a and E on b. Both land in ({B, D}, {C, E}), so they still agree. C and E both go to {B, D} on a and {A} on b. Nothing splits, so we have a **stable partition**.

The minimal DFA has 3 states:

| Block | Meaning | on a | on b |
|---|---|---|---|
| → {A} | no progress | {B,D} | {A} |
| {B,D} | just saw a | {B,D} | {C,E} |
| {C,E} (accept) | just saw ab | {B,D} | {A} |

That is the same machine the subset construction gave in the NFA units, as uniqueness promises.

### The same thing in Python

```python
def minimise(states, alpha, delta, accept):
    states = tuple(states)
    alpha = tuple(alpha)
    # start: split accepting / non-accepting
    part = {q: q in accept for q in states}
    while True:
        # Keep the block and all successor
        # blocks.
        sig = {q: (part[q],) + tuple(
                   part[delta[(q, c)]]
                   for c in alpha)
               for q in states}
        ids = {}
        # Equal signatures receive one new
        # block.
        new = {q: ids.setdefault(sig[q],
                                 len(ids))
               for q in states}
        old = len(set(part.values()))
        # Refinement cannot merge old
        # blocks.
        if len(ids) == old:
            return new   # stable: no split
        part = new
```

Each state's **refinement signature** is its current block plus the blocks it moves to. States with equal signatures stay together. When a round creates no new blocks, stop. On the example (with F removed) it returns `{A: 0, B: 1, C: 2, D: 1, E: 2}`: three blocks, B with D and C with E.

The DFA must be complete (every transition defined), so add a dead state first if needed. Remove unreachable states before calling this function. It returns state-to-block IDs; constructing the quotient transitions, start and accepting states is a separate step.

## The table-filling algorithm

The textbook alternative (Hopcroft and Ullman) works on pairs. Draw a triangle with one cell per pair of states.

1. Mark every pair where one is accepting and the other is not.
2. Repeat: mark a pair if, on some symbol, its two successors form a pair that is already marked (the rule below).
3. When a full pass marks nothing, every unmarked pair is equivalent.

Propagate a distinction backwards: if one symbol leads to a marked pair, mark the original pair. Prepending that symbol to the known distinguishing suffix explains why the new mark is justified.

For our five states:

```
    A    B    C    D
B   x1
C   x0   x0
D   x1   =    x0
E   x0   x0   =    x0
```

`x0` means marked in step 1 (different acceptance). `x1` means marked in the first pass: for (A, B), reading b gives (A, C), which is already marked. The two unmarked cells are (B, D) and (C, E), the same merges as before.

Table filling is easy to do by hand but takes O(n²) space for n states. It also tells you why each pair differs, which helps when debugging.

## Key takeaways
- Remove unreachable states before counting the minimal machine.
- Refinement splits acceptance blocks to a fixed point; table filling marks distinguishable pairs.

## Further reading
- [Minimization of Automata — Berstel, Boasson, Carton and Fagnot](https://arxiv.org/abs/1010.5318)
