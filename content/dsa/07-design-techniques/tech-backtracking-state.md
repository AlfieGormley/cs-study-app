---
id: tech-backtracking-state
title: Choose, explore and unchoose
level: intermediate
minutes: 2
sourceLesson: tech-backtracking
summary: Backtracking walks an implicit decision tree depth first.
---

Some problems don't have a clever formula. You simply have to try possibilities: every subset, every ordering, every placement. **Backtracking** is the disciplined way to do that.

Picture walking a maze with a piece of chalk. At each junction you pick a corridor and mark it. If you reach a dead end, you walk back to the last junction, rub out the mark and try the next corridor. With systematic choice enumeration and a mark for every cell on the current path, you can enumerate simple routes without following a cycle forever. The path is working search state; access to the maze and any extra constraints still requires storage.

## The state-space tree

Every backtracking problem is a walk over an implicit tree of decisions, its **state-space tree**. Each level is one decision; each edge is one choice; each leaf is a complete candidate.

Generating subsets of `[1, 2, 3]`: at each level decide "include this element or not".

```
                  []
          +1 /         \ skip
          [1]           []
       +2/   \       +2/  \
     [1,2]   [1]    [2]    []
     /  \    / \    / \    / \
 [123][12][13][1][23][2] [3] []
```

The tree has 2³ = 8 leaves, one per subset. Backtracking is a **depth-first** traversal of this tree that builds the current path incrementally and undoes it on the way back.

## The template: choose, explore, unchoose

Almost every backtracking solution has this shape:

```python
def backtrack(state):
    # These helpers are a problem-specific
    # sketch.
    if is_complete(state):
        # Store an independent completed
        # result.
        record(state)
        return
    for choice in choices(state):
        if not is_valid(state, choice):
            continue          # prune
        make(state, choice)   # choose
        backtrack(state)      # explore
        # Restore every mutation before the
        # next choice.
        undo(state, choice)   # unchoose
```

- **Choose** modifies one shared piece of state (append to a path, mark a cell used).
- **Explore** recurses with that choice in place.
- **Unchoose** restores the state *exactly* so that the next choice starts from the same position.

Simple path append/pop updates cost amortised O(1), avoiding a full path copy at each node. Constraint checks and richer updates can cost more; shared mutation alone does not make them constant-time. The abstract helpers in this template are problem-specific.

## Key takeaways
- Backtracking walks an implicit decision tree depth first.
- Undo every mutation so sibling branches begin in exactly the same state.

## Further reading
- [Backtracking — Erickson](https://jeffe.cs.illinois.edu/teaching/algorithms/book/02-backtracking.pdf)
- [Python itertools](https://docs.python.org/3/library/itertools.html)
