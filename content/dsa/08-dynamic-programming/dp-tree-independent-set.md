---
id: dp-tree-independent-set
title: Choose non-adjacent nodes on a tree
level: advanced
minutes: 4
summary: Include and exclude states separate the effect of choosing the parent.
sourceLesson: dp-interval-tree
---

## DP on trees

Once boundary information such as the parent’s selected status is represented in the state, the relevant child subtrees can be combined independently. That makes the tree itself the DP order: compute every child before its parent (a post-order traversal).

### Maximum independent set on a tree

> Choose as many nodes as possible so that no two chosen nodes are adjacent. (Or, weighted: maximise total weight. This is "house robber on a tree".)

On general graphs this is NP-hard. On a tree with n nodes it's O(n).

**State**: two values per node v:

- `inc[v]` records best in v's subtree if v **is** chosen.
- `exc[v]` records best in v's subtree if v is **not** chosen.

**Recurrence**:

- If v is chosen, none of its children may be.
- If v isn't chosen, each child is free to be chosen or not.

```formula
inc[v] = w_v + Σ exc[c]   for c ∈ kids(v)
exc[v] = Σ max(inc[c], exc[c])
   for c ∈ kids(v)
answer = max(inc[r], exc[r])
where
inc[v]: the best total weight in the subtree under v when v itself is chosen
exc[v]: the best total weight in the subtree under v when v is not chosen
v: a node of the tree
w_v: the weight of node v (1 for the unweighted version)
c: a child of v
kids(v): the set of v's children
∈: "is a member of"
Σ: sum over all of v's children; 0 if v is a leaf
max: the larger of the two values
r: the root of the tree
answer: the size (or total weight) of the maximum independent set
In words: choosing v forces every child out; leaving v out lets each child independently take whichever of its two options is better.
```

```
        0
       / \
      1   2
     / \   \
    3   4   5
```

```python
def max_independent_set(adj, root=0):
    # adj: valid simple undirected tree
    if not adj:
        return 0
    if root not in range(len(adj)):
        raise ValueError("invalid root")
    def dfs(v, parent):
        inc, exc = 1, 0
        for c in adj[v]:
            # Do not walk the undirected
            # edge backwards.
            if c == parent:
                continue
            # Finish each child before its
            # parent.
            ci, ce = dfs(c, v)
            # Choosing the parent excludes
            # this child.
            inc += ce
            # An excluded parent leaves the
            # child free.
            exc += max(ci, ce)
        return inc, exc
    return max(dfs(root, -1))
```

Bottom-up on the tree above:

```
node  inc  exc
3     1    0
4     1    0
5     1    0
1     1    2      (exc: 3 and 4 free)
2     1    1
0     1+2+1=4  max(1,2)+max(1,1)=3
```

Answer 4: nodes {0, 3, 4, 5}.

For the stated valid simple undirected tree (symmetric adjacency lists, integer vertices 0..n−1), each node is visited once and each edge twice: **O(n)** work. The routine assumes this tree structure; cycles or disconnected inputs require validation or a different traversal.

> [!warning] Recursion depth on trees
> A tree can be a path of 100,000 nodes. A cold recursive Python DFS can exceed its configured call-depth limit; CPython usually starts with a limit of 1,000, but the actual threshold depends on existing call depth and implementation. For large inputs, compute an order with an explicit stack (or BFS), then process nodes in reverse order so children come before parents.

## Key takeaways
- Include and exclude states separate the effect of choosing the parent.
- Compute children before combining their answers.
- Use an explicit traversal order when recursion would be too deep.

## Further reading
- [Erickson: dynamic programming](https://jeffe.cs.illinois.edu/teaching/algorithms/book/03-dynprog.pdf)
- [MIT algorithms course](https://ocw.mit.edu/courses/6-006-introduction-to-algorithms-spring-2020/)
