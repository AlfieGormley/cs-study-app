---
id: graph-relaxation-heap
title: Relaxation and a lazy Dijkstra min-heap
level: intermediate
minutes: 4
sourceLesson: graph-shortest-paths
summary: Relaxation improves a distance only when an edge yields a cheaper route.
---

BFS finds the path with the fewest edges. Once edges carry weights (kilometres, milliseconds, pounds), the fewest edges is no longer the cheapest. A motorway detour of 3 roads can beat a single slow lane.

This lesson covers the single-source problem: the cheapest distance from one source s to every other vertex. Assume finite graphs, finite numeric weights and valid adjacency entries for every vertex. The Python min-heap examples require mutually orderable vertex labels to break distance ties. Arithmetic and expected dictionary access are treated as constant-time. Throughout, n is the number of vertices, m the number of edges, w(u, v) the weight of the edge from u to v, and O(…) is Big O notation: how the running time grows with n and m, ignoring constant factors. Every algorithm here is built on one operation.

## Relaxation

Keep a tentative distance `dist[v]` for every vertex, starting at infinity (0 for the source). The following fragment belongs inside a traversal with distances and parents already initialised. To **relax** an edge u→v of weight w is to ask "is going via u better than what I have?":

```formula
dist(v) ← min(dist(v), dist(u) + w)
dist(v) ← min(9, 3 + 4) = 7
where
u: the vertex the edge leaves
v: the vertex the edge enters
w: the weight of the edge u→v (a distance, time or cost)
dist(x): best known distance from the source to vertex x, in the same units as the edge weight
x: any vertex; the source starts at zero distance
∞: infinity: "no path found yet"
min(…): the smaller of the two values
←: replace the value on the left with the value on the right
In words: if reaching u and then taking the edge is cheaper than the best route to v so far, remember that cheaper route.
```

In the worked line, v's best so far is 9, u is 3 away and the edge costs 4, so v improves to 7. In Python:

```python
if dist[u] + w < dist[v]:
    dist[v] = dist[u] + w
    # Remember which predecessor found v.
    parent[v] = u
```

Distances only ever decrease, and never drop below the true shortest distance. The algorithms differ only in *which* edges they relax, and in what order.

## Dijkstra's algorithm

Intuition: grow a region of "settled" vertices outward from s, always settling the unsettled vertex with the smallest tentative distance next. It is BFS where the queue is ordered by distance instead of arrival.

```python
import heapq
INF = float('inf')

def dijkstra(adj, s):
    # Zero distance also marks discovery.
    dist = {s: 0}
    pq = [(0, s)]
    while pq:
        # Select the cheapest queued
        # distance.
        d, u = heapq.heappop(pq)
        # A later improvement made this
        # stale.
        if d > dist[u]:
            continue  # stale entry
        for v, w in adj[u]:
            nd = d + w
            if nd < dist.get(v, INF):
                dist[v] = nd
                # Old entries remain; skip
                # them on pop.
                heapq.heappush(pq, (nd, v))
    return dist
```

Python's `heapq` has no "decrease key", so we push a new entry and skip outdated ones when they surface (**lazy deletion**). The min-heap holds O(m + 1) entries and can pop stale entries as well as live ones. Each push or pop costs time proportional to the logarithm of the min-heap size, and in a simple graph the min-heap size cannot outgrow n² by much:

```formula
m ≤ n^2
log(m + 1) ≤ 2 log(n + 1)
T = O((n + m) log(n + 1))
where
n: the number of vertices
m: the number of edges
log: the logarithm (base 2 here): how many times you can halve a number before reaching 1
T: the running time of lazy-deletion Dijkstra
≤: is at most
≈: approximately equal to
O(…): Big O: grows at most this fast, up to a constant factor
In words: a min-heap of up to m entries costs log m per operation, and because m is at most n² that is at most about twice log n, which Big O ignores.
```

For a simple graph with one thousand vertices, a min-heap with up to a million entries has a base-two logarithmic factor of about twenty rather than ten: a constant factor, so the bound is unchanged. Arbitrary multigraphs (with repeated edges) can have m far above n², so the logarithmic factor for this lazy implementation depends on the edge count, with one added to keep the argument positive.

## Key takeaways
- Relaxation improves a distance only when an edge yields a cheaper route.
- Skip stale min-heap entries created by earlier tentative distances.

## Further reading
- [Primary reference for this unit](https://algs4.cs.princeton.edu/44sp/)
- [Dijkstra's algorithm — Wikipedia](https://en.wikipedia.org/wiki/Dijkstra%27s_algorithm)
