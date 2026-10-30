---
id: graph-astar-grid
title: A* priorities and a grid implementation
level: intermediate
minutes: 3
sourceLesson: graph-shortest-paths
summary: A* orders by cost already paid plus estimated remaining cost.
---

Dijkstra’s min-heap ordering was covered earlier. This unit uses heapq and `INF = float("inf")`, as in that implementation. The grid has four-direction movement at unit cost; a # character is a wall.

## A* search

Dijkstra settles vertices by distance from the source; obstacles, weights and connectivity shape the explored region. If you want one specific target and can **estimate** how far you are from it, you can steer the search.

A* orders the min-heap by a priority that adds a guess of the remaining distance to the distance already travelled:

```formula essential
f(v) = g(v) + h(v)
where
v: a vertex waiting in the min-heap
g(v): the known cost from the start to v (Dijkstra's dist)
h(v): the heuristic: an estimate of the remaining cost from v to the goal
f(v): the estimated total cost of the best path through v; the min-heap pops the smallest
In words: A* expands the vertex that looks cheapest overall, counting both the distance already travelled and a guess at the distance still to go.
```

A vertex six steps from the start and estimated four from the goal has priority ten, so it is expanded before one three steps from the start and estimated nine from the goal (priority twelve). On a grid the usual estimate is the Manhattan distance, the number of up/down/left/right steps ignoring walls. From row 2, column 7 to a goal at row 5, column 3 that is 3 rows plus 4 columns: 7 moves.

```formula reference
h(p) = |r_p − r_goal| + |c_p − c_goal|
where
p: the current cell
r_p, c_p: p's row and column
r_goal, c_goal: the goal's row and column
|x|: the absolute value of x: x without its minus sign
h(p): the estimated remaining cost, in moves
In words: count the rows and the columns you still have to cross; walls can only make the real path longer.
```

> [!analogy] Real-world analogy: a walker heading for a hilltop mast
> A walker trying to reach a mast on a distant hill picks, at each junction, the path that looks best overall: how far they have already walked plus how far the mast still looks as the crow flies.
>
> **How it maps:** distance already walked is g, the crow-flies distance to the mast is the heuristic h, and choosing the junction with the smallest total is popping the smallest f. The estimate pulls the search towards the goal instead of spreading evenly in every direction like Dijkstra.
>
> **Where it stops:** the walker commits to one route. A* keeps every partly explored route in its min-heap and can switch back to an older one when a wall or river makes the current direction more expensive than it looked, which is what keeps it optimal with a suitable heuristic.

```python
def astar(grid, start, goal):
    if not grid or not grid[0]:
        return None
    R, C = len(grid), len(grid[0])
    if any(len(row) != C for row in grid):
        raise ValueError("ragged grid")

    def h(p):  # Manhattan distance
        return (abs(p[0] - goal[0])
                + abs(p[1] - goal[1]))

    def ok(r, c):
        return (0 <= r < R and 0 <= c < C
                and grid[r][c] != '#')

    if not ok(*start) or not ok(*goal):
        return None
    g = {start: 0}
    pq = [(h(start), start)]
    while pq:
        f, u = heapq.heappop(pq)
        if u == goal:
            return g[u]
        if f > g[u] + h(u):
            continue  # stale
        r, c = u
        for v in ((r + 1, c), (r - 1, c),
                  (r, c + 1), (r, c - 1)):
            if not ok(*v):
                continue
            ng = g[u] + 1
            # Reopen a cell after a cheaper
            # route.
            if ng < g.get(v, INF):
                g[v] = ng
                f = ng + h(v)
                heapq.heappush(pq, (f, v))
    return None
```

## Key takeaways
- A* orders by cost already paid plus estimated remaining cost.
- The grid implementation rejects blocked endpoints and ragged inputs.
- Manhattan distance fits four-way unit-cost movement.

## Further reading
- [A* search algorithm — Wikipedia](https://en.wikipedia.org/wiki/A*_search_algorithm)
- [Introduction to A* — Red Blob Games](https://www.redblobgames.com/pathfinding/a-star/introduction.html)
