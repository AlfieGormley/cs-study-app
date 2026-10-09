---
id: adv-segment-trees
title: Segment trees
level: advanced
minutes: 15
summary: A binary tree of range summaries that answers range queries and applies updates in O(log n), plus lazy propagation for updating whole ranges at once.
---

Suppose you have an array and two kinds of request arriving in any order: "what is the sum (or minimum, or maximum) of `a[l..r]`?" and "change `a[i]`".

Throughout this lesson n is the number of elements in the array, and O(f) means "the work grows at most in proportion to f". `a[l..r]` means the elements from index l to index r, both included.

- A plain array makes updates O(1) (a fixed amount of work) but queries O(n).
- A prefix-sum array makes sum queries O(1) but every update O(n), because every later prefix changes.

On large arrays, many O(n) operations can become expensive. A **segment tree** makes both operations O(log n). For a million elements the difference is stark:

```formula
c_scan = n = 1,000,000
c_tree ≈ log_2(n) ≈ 20
where
n: the number of elements in the array, a million here
c_scan: roughly how many elements one O(n) query or update touches
c_tree: roughly how many tree levels one segment-tree operation walks through
log_2(n): the base-2 logarithm of n: the power you raise 2 to in order to get n
≈: approximately equal to
In words: scanning touches every element, while a segment tree only walks down about 20 levels for a million elements.
```

A segment tree does a few nodes of work per level, so the real count is a small multiple of 20, still tens of thousands of times less than a scan. It works for any operation that combines associatively, not just sums.

## The idea: store answers for halves, quarters, eighths...

Each node of a segment tree is responsible for a contiguous range of the array and stores the answer for that range. The root covers everything; each node splits its range in half between its two children; the leaves are single elements.

For `a = [5, 2, 8, 1, 9, 3, 7, 4]` with sums:

```
              [0,7]=39
         /              \
    [0,3]=16          [4,7]=23
    /      \          /      \
 [0,1]=7 [2,3]=9  [4,5]=12 [6,7]=11
  / \     / \      / \      / \
 5   2   8   1    9   3    7   4
```

Any range can be assembled from a handful of these precomputed pieces. Writing S(l, r) for the sum of `a[l..r]`:

```formula
S(2, 5) = S(2, 3) + S(4, 5)
S(2, 5) = 9 + 12 = 21
where
S(l, r): the sum of the array elements from index l to index r, both included; the label [l,r]=value in the drawing is S(l, r)
l: the first index of a range
r: the last index of a range
In words: the range 2 to 5 splits into two stored nodes, 2 to 3 and 4 to 5, so adding their two stored sums gives the answer.
```

That is two nodes instead of four elements. For long ranges the saving is enormous: any range needs at most about two nodes per level of the tree.

## Storing it in an array

Like a binary heap, the tree lives in a flat array, with the root at index 1. The children of a node are found by arithmetic, so no pointers are stored:

```formula
left(v) = 2 × v
right(v) = 2 × v + 1
left(3) = 6,   right(3) = 7
where
v: the array index of a node; the root is 1
left(v): the index of v's left child
right(v): the index of v's right child
In words: double a node's index to find its left child, and add one more for its right child.
```

How big must the array be? Each level can hold twice as many nodes as the one above, and the leaves must fit on the bottom level:

```formula
h = ⌈log_2(n)⌉
slots ≤ 2 × 2^h < 4 × n
n = 5:  h = 3,  2 × 2^3 = 16 < 20
where
n: the number of elements in the array
h: the height of the tree: the number of levels below the root
log_2(n): the base-2 logarithm of n: the power you raise 2 to in order to get n
⌈ ⌉: ceiling: round up to the nearest whole number
2^h: 2 multiplied by itself h times, the number of slots on the bottom level
slots: the highest array index a node can use, plus one
≤: is at most
<: is less than
In words: rounding n up to the next power of two at most doubles it, and a full tree on that many leaves needs twice as many slots, so 4n is always enough.
```

That is why implementations allocate `4 * n`. When n is already a power of two, the bottom level holds exactly n leaves and 2n slots are enough.

## Query, update and build

The examples require non-empty arrays and valid inclusive ranges or point indices:

```formula
0 ≤ l ≤ r < n
0 ≤ i < n
where
l: the first index of the query range
r: the last index of the query range (inclusive)
i: the index of a single element to update
n: the number of elements in the array
≤: is at most
<: is less than
In words: ranges and positions must lie inside the array, and a range must not end before it starts.
```

For an 8-element array, `query(2, 5)` is valid and `query(5, 2)` or `update(8, x)` is not. Complexity assumes constant-size summaries and constant-time combines on word-sized values. Integer sums are associative; floating-point sums need numerical-error considerations.

```python
class SegTree:
    def __init__(self, a):
        self.n = len(a)
        if not self.n:
            raise ValueError("empty array")
        self.t = [0] * (4 * self.n)
        self._build(a, 1, 0, self.n - 1)

    def _pull(self, v):
        t = self.t
        t[v] = t[2*v] + t[2*v + 1]

    def _build(self, a, v, lo, hi):
        if lo == hi:
            self.t[v] = a[lo]
            return
        m = (lo + hi) // 2
        self._build(a, 2*v, lo, m)
        self._build(a, 2*v + 1, m + 1, hi)
        self._pull(v)

    def query(self, l, r):  # inclusive
        return self._q(1, 0, self.n-1, l, r)

    def _q(self, v, lo, hi, l, r):
        if r < lo or hi < l:     # disjoint
            return 0
        if l <= lo and hi <= r:  # covered
            return self.t[v]
        m = (lo + hi) // 2
        return (self._q(2*v, lo, m, l, r) +
            self._q(2*v+1, m+1, hi, l, r))

    def update(self, i, x):
        self._u(1, 0, self.n-1, i, x)

    def _u(self, v, lo, hi, i, x):
        if lo == hi:
            self.t[v] = x
            return
        m = (lo + hi) // 2
        if i <= m:
            self._u(2*v, lo, m, i, x)
        else:
            self._u(2*v+1, m+1, hi, i, x)
        self._pull(v)
```

The query has three cases at each node:

1. **Disjoint**: the node's range misses `[l, r]` entirely. Return the identity (0 for sum, +infinity for min).
2. **Covered**: the node's range lies inside `[l, r]`. Return its stored value without going deeper.
3. **Partial overlap**: recurse into both children and combine.

The update walks one root-to-leaf path, then recomputes each node on the way back up.

### Why O(log n)?

- **Build**: each of the 2n − 1 nodes is computed once: O(n).
- **Update**: one root-to-leaf path, O(1) work per node: O(log n).
- **Query**: at each level, at most two nodes are *partially* overlapped (the ones containing the ends of `[l, r]`). Everything between them is fully covered and stops immediately. So at most four nodes are visited per level.

Counting levels gives the bounds:

```formula
N_build = 2 × n − 1
N_update ≤ ⌈log_2(n)⌉ + 1
N_query ≤ 4 × (⌈log_2(n)⌉ + 1)
n = 10^6:  N_update ≤ 21,  N_query ≤ 84
where
n: the number of elements in the array
N_build: the number of nodes the build computes
N_update: the number of nodes a point update touches (one per level, root to leaf; a leaf one level higher than the deepest saves one)
N_query: the number of nodes a range query visits
log_2(n): the base-2 logarithm of n
⌈ ⌉: ceiling: round up to the nearest whole number
≤: is at most
In words: a build touches every node once, an update touches one node per level, and a query touches at most four nodes per level.
```

For a million elements that is at most 21 nodes per update and at most 84 per query, which is why both are O(log n). The bounds assume combining two summaries takes constant time.

## Beyond sums: what can a node store?

The structure works whenever the combine operation is **associative**, with an **identity element** for the empty range:

```formula
(x ⊕ y) ⊕ z = x ⊕ (y ⊕ z)
x ⊕ e = e ⊕ x = x
min(min(5, 2), 8) = min(5, min(2, 8)) = 2
where
⊕: the combine operation the tree uses (for example +, min or max)
x, y, z: any three node summaries, in left-to-right order
e: the identity element: the value that leaves anything unchanged when combined with it (0 for +, +∞ for min, −∞ for max)
min: the smaller of its arguments
+∞: plus infinity, larger than every value
−∞: minus infinity, smaller than every value
In words: you may group neighbouring pieces in any way without changing the answer, and there is a neutral value to return for an empty range.
```

The worked line shows min is associative. Sum, min, max, gcd (greatest common divisor), bitwise AND, bitwise OR, bitwise XOR and matrix products all qualify. Subtraction does not: (8 − 3) − 2 is 3 but 8 − (3 − 2) is 7.

Associative is enough; **commutative is not required**. The recursive code always combines the left child before the right, so non-commutative operations like matrix multiplication or string concatenation work, as long as you keep that order. Actual string concatenation is not constant-time, and matrix costs depend on dimension; their runtimes include combine costs.

You can also store a small **struct** per node. The famous example is the **maximum subarray sum** over a range, with point updates. Each node stores four numbers:

| Field | Symbol | Meaning |
|---|---|---|
| `sum` | s | total of the range |
| `pre` | p | best prefix sum |
| `suf` | q | best suffix sum |
| `best` | b | best subarray sum |

Combining a left child L and a right child R:

```formula
s = s_L + s_R
p = max(p_L, s_L + p_R)
q = max(q_R, s_R + q_L)
b = max(b_L, b_R, q_L + p_R)
where
s, p, q, b: the combined node's total, best prefix sum, best suffix sum and best subarray sum
s_L, p_L, q_L, b_L: the same four numbers for the left child L
s_R, p_R, q_R, b_R: the same four numbers for the right child R
max: the largest of its arguments
In words: the best prefix either stays in the left half or takes all of it plus a prefix of the right; the best subarray is in one half or is a left suffix joined to a right prefix.
```

For example, take the left half [2, −1] and the right half [3, −5]:

```formula
s_L = 1,  p_L = 2,  q_L = 1,  b_L = 2
s_R = −2,  p_R = 3,  q_R = −2,  b_R = 3
s = 1 + (−2) = −1
p = max(2, 1 + 3) = 4
q = max(−2, −2 + 1) = −1
b = max(2, 3, 1 + 3) = 4
where
s_L, p_L, q_L, b_L: total, best prefix, best suffix and best subarray sum of the left half [2, −1]
s_R, p_R, q_R, b_R: the same four numbers for the right half [3, −5]
s, p, q, b: the same four numbers for the whole array [2, −1, 3, −5]
max: the largest of its arguments
In words: the best subarray of the whole array is 2 − 1 + 3 = 4, which crosses the middle and is found as the left half's best suffix plus the right half's best prefix.
```

You can check every line by listing the prefixes and suffixes of [2, −1, 3, −5] by hand. These rules assume subarrays must be non-empty.

The best subarray is either entirely in one half or crosses the middle, in which case it is a suffix of the left plus a prefix of the right. Kadane's algorithm cannot handle updates; this can, in O(log n) each.

## Lazy propagation: updating whole ranges

Now add a third request: "add `x` to every element of `a[l..r]`". Doing it as one point update per element is slow for a big range:

```formula
c_naive = (r − l + 1) × (⌈log_2(n)⌉ + 1)
c_naive = 10^6 × 21 = 21,000,000
where
c_naive: the number of nodes touched when a range add is done as separate point updates
l, r: the first and last index of the range, inclusive
r − l + 1: the number of elements in the range
n: the number of elements in the array; the example uses a whole-array add with n = 10^6
log_2(n): the base-2 logarithm of n
⌈ ⌉: ceiling: round up to the nearest whole number
In words: each element in the range costs a full root-to-leaf update, so a range covering most of the array costs O(n log n).
```

**Lazy propagation** applies a range update the same way a query reads a range: stop at fully covered nodes. At such a node, update its stored sum and leave a **pending tag** saying "my children still owe `+x`":

```formula
S_new = S_old + x × (hi − lo + 1)
z_new = z_old + x
S_new = 0 + 5 × (3 − 0 + 1) = 20
where
lo, hi: the first and last array index covered by a node whose whole range lies inside the update range
S_old: that node's stored sum before the update
S_new: that node's stored sum after the update
z_old: the node's pending tag (the amount its children still owe) before the update
z_new: the node's pending tag after the update
x: the amount added to every element of the range
In words: adding x to every element of a node's range raises its sum by x times the number of elements, and the tag remembers to pass x on to the children later.
```

The third line is the node [0,3] in the trace below. The tag is **pushed down** to the children only when some later operation needs to go below that node.

```python
class LazySeg:
    def __init__(self, n):
        if n < 1:
            raise ValueError("n > 0")
        self.n = n
        self.t = [0] * (4 * n)   # sums
        self.lz = [0] * (4 * n)  # pending

    def _apply(self, v, lo, hi, x):
        # add x to every element under v
        self.t[v] += x * (hi - lo + 1)
        self.lz[v] += x

    def _push(self, v, lo, hi):
        x = self.lz[v]
        if x:
            m = (lo + hi) // 2
            self._apply(2*v, lo, m, x)
            self._apply(2*v+1, m+1, hi, x)
            self.lz[v] = 0

    def add(self, l, r, x):
        self._add(1, 0, self.n-1, l, r, x)

    def _add(self, v, lo, hi, l, r, x):
        if r < lo or hi < l:
            return
        if l <= lo and hi <= r:
            self._apply(v, lo, hi, x)
            return
        self._push(v, lo, hi)
        m = (lo + hi) // 2
        self._add(2*v, lo, m, l, r, x)
        self._add(2*v+1, m+1, hi, l, r, x)
        t = self.t
        t[v] = t[2*v] + t[2*v + 1]

    def query(self, l, r):
        return self._q(1, 0, self.n-1, l, r)

    def _q(self, v, lo, hi, l, r):
        if r < lo or hi < l:
            return 0
        if l <= lo and hi <= r:
            return self.t[v]
        self._push(v, lo, hi)
        m = (lo + hi) // 2
        return (self._q(2*v, lo, m, l, r) +
            self._q(2*v+1, m+1, hi, l, r))
```

> [!example] Tracing a lazy update
> On 8 zeros, `add(0, 3, 5)` reaches node `[0,3]`, which is fully covered. It sets that node's sum to 20 and its tag to 5, and the root's sum to 20. The four leaves are not touched at all. A later `add(2, 5, 1)` must go inside `[0,3]`, so it first pushes the tag: `[0,1]` and `[2,3]` each get sum 10 and tag 5.

Both operations now visit O(log n) nodes, so range update and range query are both **O(log n)**.

Lazy propagation needs two properties:

- You can update a node's summary without looking at its children.
- Pending tags **compose**: two adds become one add. Mixing "assign" and "add" works too, but the tag must record the order (an assignment wipes out earlier adds).

For a range add, both properties are one line each:

```formula
S_new = S_old + x × w
M_new = M_old + x
z_2 = (z_0 + x_1) + x_2 = z_0 + (x_1 + x_2)
where
S_old, S_new: a node's stored sum before and after the add
M_old, M_new: a node's stored minimum before and after the add
w: the width of the node: the number of elements it covers
x: the amount added to every element
z_0: the node's pending tag before two later adds
z_2: the node's pending tag after both adds
x_1, x_2: two adds applied one after the other
In words: a sum grows by x for every element and a minimum grows by exactly x, and two pending adds merge into a single add of their total.
```

So a node covering 4 elements with sum 20 and minimum 3 becomes sum 28 and minimum 5 after adding 2.

Some updates fail the first test. "Replace every `a[i]` in a range with `a[i] mod k`" (the remainder when `a[i]` is divided by `k`) changes a sum in a way that depends on every element, so plain lazy propagation cannot do it.

## The iterative bottom-up version

For point updates and commutative operations there is a compact, fast, non-recursive form. It needs only 2n slots, with the leaves in the second half:

```formula
leaf(j) = n + j
parent(i) = ⌊i / 2⌋
n = 8:  leaf(5) = 13,  parent(13) = 6
where
n: the number of elements in the array
j: an array position, from 0 to n − 1
leaf(j): the index in the tree array of element j's leaf
i: any tree index other than the root (index 1)
parent(i): the index of i's parent
⌊ ⌋: floor: round down to the nearest whole number
In words: element j is stored at slot n + j, and halving any index (rounding down) moves one level up.
```

In Python, `i // 2` is exactly the floor of i / 2 for non-negative i.

```python
def build(a):
    n = len(a)
    t = [0] * n + list(a)
    for i in range(n - 1, 0, -1):
        t[i] = t[2*i] + t[2*i + 1]
    return t

def query(t, n, l, r):  # half-open [l, r)
    res = 0
    l, r = l + n, r + n
    while l < r:
        if l & 1:   # l is a right child
            res += t[l]
            l += 1
        if r & 1:   # r - 1 is a left child
            r -= 1
            res += t[r]
        l, r = l // 2, r // 2
    return res
```

It avoids recursive-call overhead.

> [!note] Content gap: performance multiplier
> No fixed speedup is supplied because the original “several times faster” claim lacked a reproducible benchmark for a specified implementation and workload.

## Where segment trees are used

- **Competitive programming and interviews**: range sum/min/max with updates, "count of smaller numbers after self" (after coordinate compression), and booking problems such as "maximum number of overlapping events" (range add plus range max).
- **Computational geometry**: sweep-line algorithms, such as computing the area of a union of rectangles, keep a segment tree over the y-coordinates.
- **Huge index ranges**: a **dynamic** (sparse) segment tree creates nodes only when touched, so it can cover indices up to 10^9 with memory proportional to the operations performed.

> [!note] A name clash
> In computational geometry, "segment tree" traditionally names a related structure that stores a set of *intervals* and answers "which intervals contain point x?" in O(log n + k), where n is the number of stored intervals and k is the number of intervals reported. The Wikipedia article describes that version. The array-based range-query tree in this lesson is the meaning used in competitive programming and interviews.

## Pitfalls

- **Inclusive vs half-open ranges.** Pick one convention and stick to it; mixing them is the most common bug.
- **Wrong identity.** Returning 0 for a disjoint range in a *min* tree silently corrupts answers. Use +infinity.
- **Forgetting to push.** In a lazy tree, every operation that descends past a node must push its tag first, including queries.
- **Overkill.** If you only need prefix sums with point updates, a Fenwick tree (next lesson) is shorter and often has lower overhead; measure the actual workload. If the array never changes, a prefix-sum array or sparse table is simpler still.

## Key takeaways
- A segment tree stores the answer for every node's range; any query range decomposes into O(log n) nodes, where n is the array length.
- Build O(n), point update O(log n), range query O(log n), in a `4n` array.
- Any associative combine works, including non-commutative ones and multi-field nodes such as max subarray sum.
- Lazy propagation defers range updates with tags pushed down on demand, making range update and range query both O(log n).
- Use the identity element for disjoint ranges and push tags before descending.

## Further reading
- [Segment Tree — cp-algorithms](https://cp-algorithms.com/data_structures/segment_tree.html)
- [Segment tree, the interval-stabbing version — Wikipedia](https://en.wikipedia.org/wiki/Segment_tree)
- [Range minimum query — Wikipedia](https://en.wikipedia.org/wiki/Range_minimum_query)
