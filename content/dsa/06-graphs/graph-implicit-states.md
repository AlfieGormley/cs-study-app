---
id: graph-implicit-states
title: Implicit grids and state spaces
level: basic
minutes: 3
sourceLesson: graph-fundamentals
summary: Generate predictable grid edges as needed.
---

Graph vertices need not be objects stored in a database. They can be cells or legal configurations, with a rule that generates the next possible states.

## Implicit graphs

Often the graph is never stored at all. You have a rule that, given a vertex, generates its neighbours on demand. This is an **implicit graph**.

### Grids

A maze or image is a grid where each cell is a vertex and neighbours are the adjacent cells.

```
grid       neighbours of (1,1)
S . #           (0,1)
. . .     (1,0) (1,1) (1,2)
# . E           (2,1)
```

```python
DIRS = [(1, 0), (-1, 0), (0, 1), (0, -1)]

def neighbours(grid, r, c):
    # Precondition: rectangular grid.
    if not grid or not grid[0]:
        return
    R, C = len(grid), len(grid[0])
    if not (0 <= r < R and 0 <= c < C):
        return
    if grid[r][c] == "#":
        return
    for dr, dc in DIRS:
        nr, nc = r + dr, c + dc
        if (0 <= nr < R and 0 <= nc < C
                and grid[nr][nc] != '#'):
            # Produce a legal cell without
            # storing edges.
            yield nr, nc
```

You can count a grid's size without building it. Each row has one link fewer than it has cells, and so does each column:

```formula
n = RC
m = R(C − 1) + C(R − 1)
n = 3 × 3 = 9
m = 3 × 2 + 3 × 2 = 12
where
R: the number of rows in the grid
C: the number of columns
n: the number of vertices (cells)
m: the number of undirected edges when you can move up, down, left or right
In words: a wall-free grid has one vertex per cell, and each row and each column contributes one edge fewer than its length.
```

The worked lines are the 3 × 3 grid above with its walls removed: 9 cells and 12 edges. Walls only remove vertices and edges, so a grid with walls has at most those counts. Large four-direction grids have about twice as many undirected edges as cells, so they are sparse. Generating neighbours avoids storing predictable edges; precomputing them can still help some repeated workloads.

### State spaces

The vertices can be abstract **states**. In a sliding-tile puzzle, a state is a board arrangement and an edge is one legal move. In "word ladder" (turn COLD into WARM one letter at a time), a state is a word and an edge links words differing by one letter. In a lock with four dials, a state is a 4-digit code with 8 neighbours (each dial up or down).

State spaces can be astronomically large: the 15-puzzle has about 10¹³ reachable states. Search often generates states as needed; even then exhaustive BFS can be infeasible. BFS, DFS and A* can use a `neighbours(state)` function instead of stored adjacency.

> [!tip] Spotting a graph problem
> Ask: "What are the states, and what moves take me from one to another?" If the answer is clear, you have a graph. BFS minimises the number of unit-cost moves when the reachable search space is manageable.

## Key takeaways
- Generate predictable grid edges as needed.
- A search vertex must encode a complete state, not just its visible position.

## Further reading
- [Primary reference for this unit](https://algs4.cs.princeton.edu/41graph/)
- [Implicit graph — Wikipedia](https://en.wikipedia.org/wiki/Implicit_graph)
