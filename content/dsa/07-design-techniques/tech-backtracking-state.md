---
id: tech-backtracking-state
title: Choose, explore and unchoose
level: intermediate
minutes: 2
sourceLesson: tech-backtracking
summary: Backtracking walks an implicit decision tree depth first.
---

Some problems don't have a clever formula. You simply have to try possibilities: every subset, every ordering, every placement. **Backtracking** is the disciplined way to do that.

Backtracking makes one choice at a time, follows it as far as it can, and when it reaches a dead end it undoes the most recent choice and tries the next option. Marking everything on the current path stops it going round in circles.

> [!analogy] Real-world analogy: a maze and a piece of chalk
> Walking a maze, at each junction you pick a corridor and chalk a mark on it. At a dead end you walk back to the last junction, rub out the mark and try the next corridor.
>
> **How it maps:** a junction is a decision point; picking a corridor is "choose", walking on is "explore", and walking back and rubbing out the mark is "unchoose". The chalk marks are the shared path state, and trying every corridor in a fixed order makes the search systematic, so no route is missed or repeated.
>
> **Where it stops:** a maze is a fixed physical place. A backtracking search tree usually isn't stored anywhere: the next choices are generated on the fly, the tree can be astronomically large, and the program must also restore any extra bookkeeping (counters, sets of used values), not just the path.

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
