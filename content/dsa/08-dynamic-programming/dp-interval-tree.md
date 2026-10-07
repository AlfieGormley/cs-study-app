---
id: dp-interval-tree
title: Interval and tree DP
level: advanced
minutes: 15
summary: DP over ranges (matrix chain multiplication, burst balloons, palindromes), evaluated by interval length, and DP over trees (maximum independent set), evaluated bottom-up from the leaves.
---

So far every state has been a prefix, a suffix or a pair of prefixes. Two more shapes cover a large class of harder problems:

- **Interval DP**: the state is a contiguous range `[i, j]`, and the recurrence splits it at some point k.
- **Tree DP**: the state is a node (often with a small flag), and the answer combines the answers of its children.

## Interval DP: the pattern

```
dp[i][j] = best over k in [i, j) of
           combine(dp[i][k], dp[k+1][j],
                   cost(i, k, j))
```

- **States**: O(n²) intervals.
- **Transitions**: O(n) split points each.
- **Total**: usually **O(n³)** time, O(n²) space.
- **Order**: every interval depends on strictly shorter ones, so loop by **length**, from short to long.

## Matrix chain multiplication

With the classical dense algorithm, multiplying p × q by q × r costs p·q·r scalar multiplications. Matrix multiplication is associative in exact arithmetic, so for a chain A·B·C you can choose the bracketing, and the costs can differ wildly.

With A: 10 × 30, B: 30 × 5, C: 5 × 60:

- (AB)C: 10·30·5 + 10·5·60 = 1,500 + 3,000 = **4,500**
- A(BC): 30·5·60 + 10·30·60 = 9,000 + 18,000 = **27,000**

Six times as many scalar multiplications in this cost model, just from the brackets. The number of possible bracketings grows like the Catalan numbers (exponentially), so trying them all is out.

Represent the chain by a dimension list `p`, where matrix i is `p[i] × p[i+1]`.

**State**: `C[i][j]` = minimum cost to multiply matrices i through j.

**Recurrence**: the **last** multiplication splits the chain into `(i..k)` and `(k+1..j)`. Those two products are `p[i] × p[k+1]` and `p[k+1] × p[j+1]`, so the final multiply costs `p[i]·p[k+1]·p[j+1]`:

```
C[i][j] = min over i <= k < j of
    C[i][k] + C[k+1][j]
    + p[i] * p[k+1] * p[j+1]
```

**Base**: `C[i][i] = 0` (a single matrix needs no work).

```python
def matrix_chain(p):
    p = tuple(p)
    if not p or any(type(x) is not int
                    or x <= 0 for x in p):
        raise ValueError("positive dims")
    n = len(p) - 1
    if n == 0:
        return 0
    C = [[0] * n for _ in range(n)]
    for length in range(2, n + 1):
        for i in range(n - length + 1):
            j = i + length - 1
            C[i][j] = min(
                C[i][k] + C[k+1][j]
                + p[i] * p[k+1] * p[j+1]
                for k in range(i, j))
    return C[0][n - 1]
```

`matrix_chain([10, 30, 5, 60])` returns 4,500. For `[40, 20, 30, 10, 30]` (four matrices) it returns 26,000, via `((A(BC))D)`. Store the best k in a parallel `split` table to print the bracketing recursively.

The table fills diagonal by diagonal:

```
         j=0   j=1   j=2
 i=0      0   1500  4500
 i=1            0   9000
 i=2                  0
```

> [!note] Where this matters
> Numerical libraries face this directly: `numpy.linalg.multi_dot` chooses the multiplication order for a chain of arrays using this DP, and `numpy.einsum` with `optimize=True` uses its greedy contraction-order search, which need not find the global optimum. Database query optimisers solve a harder cousin when ordering joins.

## Burst balloons: think about the last move

> Balloons in a row have numbers. Bursting balloon k earns `left · k · right`, where left and right are its *current* neighbours (or 1 past the ends). Maximise total coins.

The obvious state, "which balloon do I burst **first** in `[i, j]`?", fails: after bursting it, its neighbours become adjacent, so the two halves aren't independent.

The trick is to ask which balloon is burst **last** in an open interval `(i, j)`. The subproblem keeps boundary balloons i and j present. If k is last, then when it is burst its neighbours are exactly i and j (everything between has gone). And the balloons in `(i, k)` and `(k, j)` never interact with each other, because k stands between them the whole time.

Pad the array with 1s at both ends: `a = [1] + nums + [1]`.

```
B[i][j] = max over i < k < j of
    B[i][k] + a[i]*a[k]*a[j] + B[k][j]
```

with `B[i][i+1] = 0` (no balloons strictly between).

For `[3, 1, 5, 8]` the answer is **167**: burst 1 (3·1·5 = 15), then 5 (3·5·8 = 120), then 3 (1·3·8 = 24), then 8 (1·8·1 = 8).

> [!tip] First vs last
> When a choice changes the neighbours of what's left, try defining the recurrence by the **last** action in the interval instead of the first. The last action sees a fixed boundary; the first one doesn't.

## Palindromes

### Counting palindromic substrings

`P[i][j]` = True if `s[i..j]` is a palindrome. It is exactly when the ends match and the inside is a palindrome (or there is no inside):

```
P[i][j] = s[i] == s[j] and
          (j - i < 2 or P[i+1][j-1])
```

```python
def count_palindromes(s):
    n = len(s)
    P = [[False] * n for _ in range(n)]
    count = 0
    for i in range(n - 1, -1, -1):
        for j in range(i, n):
            inner = j - i < 2 or P[i+1][j-1]
            if s[i] == s[j] and inner:
                P[i][j] = True
                count += 1
    return count
```

`"aaa"` has 6 (three `a`s, two `aa`s, one `aaa`); `"abc"` has 3; `"racecar"` has 10. O(n²) time and space.

Note the loop order: `i` descending, `j` ascending, because `P[i][j]` reads `P[i+1][j-1]` (next row down). Looping by length works too.

**Expand around centre** gets the same O(n²) time in O(1) space: for each of the 2n − 1 centres (characters and gaps), grow outwards while the ends match. **Manacher's algorithm** computes a compact array of palindrome radii in O(n), reusing mirror information. That suffices to find a longest palindrome or count occurrences; explicitly listing all occurrences can require Θ(n²) output.

### Longest palindromic subsequence

Not contiguous, so it's a classic interval DP:

```
if s[i] == s[j]:
    L[i][j] = L[i+1][j-1] + 2
else:
    L[i][j] = max(L[i+1][j], L[i][j-1])
```

with `L[i][i] = 1` and empty intervals valued 0. For `"bbbab"` the answer is 4 (`"bbbb"`). Its length equals the LCS length of s and its reverse; an arbitrary reconstructed LCS need not itself be palindromic.

## DP on trees

Once boundary information such as the parent’s selected status is represented in the state, the relevant child subtrees can be combined independently. That makes the tree itself the DP order: compute every child before its parent (a post-order traversal).

### Maximum independent set on a tree

> Choose as many nodes as possible so that no two chosen nodes are adjacent. (Or, weighted: maximise total weight. This is "house robber on a tree".)

On general graphs this is NP-hard. On a tree it's O(n).

**State**: two values per node v:

- `inc[v]` = best in v's subtree if v **is** chosen.
- `exc[v]` = best in v's subtree if v is **not** chosen.

**Recurrence**:

- If v is chosen, none of its children may be: `inc[v] = w[v] + Σ exc[c]`.
- If v isn't chosen, each child is free: `exc[v] = Σ max(inc[c], exc[c])`.

**Answer**: `max(inc[root], exc[root])`.

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
            if c == parent:
                continue
            ci, ce = dfs(c, v)
            inc += ce
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
> A tree can be a path of 100,000 nodes. Recursive DFS in Python then blows the 1,000-frame limit. For large inputs, compute an order with an explicit stack (or BFS), then process nodes in reverse order so children come before parents.

### Other tree DPs with the same shape

- **Tree diameter**: for each node, the two longest downward paths through different children.
- **Minimum vertex cover**: `inc[v] = 1 + Σ min(inc[c], exc[c])`, `exc[v] = Σ inc[c]` (if v isn't in the cover, every child must be).
- **Rerooting**: for suitable constant-sized states and O(1)-per-edge combination/exclusion (often using prefix/suffix aggregates), a second top-down pass can compute every root’s answer in O(n). More expensive transitions change the bound.

## In the real world

- **Parsing**: CYK uses an interval DP for a grammar in Chomsky normal form, in O(n³ · |grammar|) for nonempty strings; handle an allowed empty string separately.
- **RNA secondary structure** prediction in noncrossing base-pair models (such as Nussinov and Zuker formulations) uses interval DP; unrestricted pseudoknots need other treatment.
- **Optimal binary search trees** (given access frequencies) are interval DP; Knuth's observation that the optimal root index is monotone cuts it from O(n³) to O(n²).
- **Compilers** use tree DP for instruction selection: tiling an expression tree with machine instructions at minimum cost.

## Key takeaways
- Interval DP: state `[i, j]`, split at k, evaluate by increasing length; typically O(n³) time, O(n²) space.
- Matrix chain: `C[i][j] = min C[i][k] + C[k+1][j] + p[i]·p[k+1]·p[j+1]`. Bracketing can change the cost by large factors.
- When a move changes what's adjacent (burst balloons), define the recurrence by the **last** move in the interval.
- Palindromic substrings: `P[i][j] = ends match and inside is a palindrome`; O(n²) for the table, or O(n) for compact radii/counting with Manacher.
- Tree DP: per-node states (e.g. include/exclude), computed children first. Maximum independent set is O(n) on trees, NP-hard on general graphs.

## Further reading
- [Matrix chain multiplication — Wikipedia](https://en.wikipedia.org/wiki/Matrix_chain_multiplication)
- [Longest palindromic substring — Wikipedia](https://en.wikipedia.org/wiki/Longest_palindromic_substring)
- [Independent set (graph theory) — Wikipedia](https://en.wikipedia.org/wiki/Independent_set_(graph_theory))
- [CYK algorithm — Wikipedia](https://en.wikipedia.org/wiki/CYK_algorithm)
- [Jeff Erickson, Algorithms, ch. 3: Dynamic Programming (PDF)](https://jeffe.cs.illinois.edu/teaching/algorithms/book/03-dynprog.pdf)
