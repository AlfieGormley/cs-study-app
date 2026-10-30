---
id: graph-bitset-reachability
title: Transitive closure with bitset rows
level: intermediate
minutes: 3
sourceLesson: graph-all-pairs
summary: Boolean closure tracks reachability rather than route cost.
---

Earlier Floyd–Warshall units established the intermediate-vertex recurrence. Here n counts vertices, m counts edges, and vertices are numbered from zero. The example graph has 2→0 of weight 5 and 0→1 of weight 3, so 2 can reach 1 through 0.

## Transitive closure

Sometimes you only care whether j is **reachable** from i. Replace min/+ with OR/AND (Warshall's algorithm):

```formula reference
R[i][j] ← R[i][j] ∨ (R[i][k] ∧ R[k][j])
where
i, j: the start and end vertices
k: the vertex unlocked this round
R[i][j]: 1 (true) if j is known to be reachable from i, 0 (false) otherwise
∨: logical OR: true if either side is true
∧: logical AND: true only if both sides are true
←: replace the old value with the new one
In words: a start vertex reaches an end vertex if it already did, or if it reaches the newly unlocked vertex and that vertex reaches the end.
```

In the example graph, 2 has no edge to 1, but 2 reaches 0 and 0 reaches 1, so unlocking vertex zero marks that pair reachable.

Pack each row into a bitset, and a whole row updates in one operation: "if i reaches k, then i reaches everything k reaches". Python's arbitrary-size integers make this easy:

```python
def closure(n, edges):
    reach = [1 << i for i in range(n)]
    # Visit each input edge once.
    for u, v in edges:
        # Set v’s bit in u’s reachability
        # row.
        reach[u] |= 1 << v
    for k in range(n):
        bit = 1 << k
        for i in range(n):
            if reach[i] & bit:
                # Merge all destinations
                # reachable via k.
                reach[i] |= reach[k]
    return reach
```

This computes reflexive transitive closure: every vertex reaches itself via a zero-length walk. A row of n bits is stored in machine words, typically 64 bits each, so OR-ing two rows costs one operation per word rather than per bit: for 10,000 vertices, 157 word operations instead of 10,000 single-bit ones.

```formula reference
c_row = ⌈n / w⌉
T = O(m + n^2 ⌈n / w⌉)
where
n: the number of vertices, so each row has n bits
w: the word size in bits; 64 on a typical 64-bit CPU
m: the number of edges
c_row: word operations to OR one row into another
⌈ ⌉: ceiling: round up to a whole number
T: the total running time of bitset transitive closure
O(…): Big O: grows at most this fast, up to a constant factor
In words: packing bits divides the inner loop's work by the word size, roughly 64 times less.
```

A row OR is therefore not constant time; it shrinks the inner work by about the word size. Python integers use implementation-specific internal digits (`sys.int_info.bits_per_digit`), not necessarily 64-bit payloads. Uses: "can this permission/role reach that resource?", "does module A transitively depend on B?", and query optimisers deriving implied joins.

For sparse graphs, a BFS from every vertex costs O(n(n + m)), n traversals of O(n + m) each, which beats n³ when m is small. On a DAG you can compute closures in reverse topological order by OR-ing together the bitsets of the vertices each one has edges to.

## Key takeaways
- Boolean closure tracks reachability rather than route cost.
- The implementation includes each vertex’s zero-length walk to itself.
- A Python integer row operation is not constant time as row width grows.

## Further reading
- [Python docs: bitwise operations on integers](https://docs.python.org/3/library/stdtypes.html#bitwise-operations-on-integer-types)
- [Transitive closure — Wikipedia](https://en.wikipedia.org/wiki/Transitive_closure)
