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

You can reason about a grid's size without building it. Each cell is a vertex, and each row and each column has one link fewer than it has cells, so the 3 × 3 grid above, with its walls removed, has 9 cells and 12 edges. Walls only remove vertices and edges. A large four-direction grid has about two undirected edges per cell (each cell has up to four neighbours, and every edge is shared by two cells), so it is sparse. Generating neighbours avoids storing predictable edges; precomputing them can still help some repeated workloads.

### State spaces

The vertices can be abstract **states**. In a sliding-tile puzzle, a state is a board arrangement and an edge is one legal move. In "word ladder" (turn COLD into WARM one letter at a time), a state is a word and an edge links words differing by one letter. In a lock with four dials, a state is a 4-digit code with 8 neighbours (each dial up or down).

> [!analogy] Real-world analogy: a chess player thinking ahead
> A chess player never writes down every possible position before a game. Looking at the board in front of them, they work out which moves are legal and what each one would lead to.
>
> **How it maps:** a board position is a vertex, a legal move is an edge, and the rules of chess are the `neighbours` function that generates edges on demand. The full graph of positions exists only implicitly.
>
> **Where it stops:** a player prunes most moves by judgement. A search such as BFS generates every legal move from each state it expands, and it must remember which states it has already seen, because different move orders often reach the same position.

State spaces can be astronomically large: the 15-puzzle has about 10¹³ reachable states. Search often generates states as needed; even then exhaustive BFS can be infeasible. BFS, DFS and A* can use a `neighbours(state)` function instead of stored adjacency.

> [!tip] Spotting a graph problem
> Ask: "What are the states, and what moves take me from one to another?" If the answer is clear, you have a graph. BFS minimises the number of unit-cost moves when the reachable search space is manageable.

## Key takeaways
- Generate predictable grid edges as needed.
- A search vertex must encode a complete state, not just its visible position.

## Further reading
- [Sedgewick and Wayne, Algorithms 4th ed.: 4.1 Undirected graphs](https://algs4.cs.princeton.edu/41graph/)
- [Implicit graph — Wikipedia](https://en.wikipedia.org/wiki/Implicit_graph)
