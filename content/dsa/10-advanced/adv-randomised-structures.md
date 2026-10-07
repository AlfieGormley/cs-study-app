---
id: adv-randomised-structures
title: Randomised structures and sampling
level: advanced
minutes: 15
summary: How coin flips replace rebalancing in skip lists and treaps, and how reservoir sampling and the Fisher–Yates shuffle produce provably uniform random choices.
---

Balanced search trees such as red–black and AVL trees guarantee O(log n) operations, but their rebalancing rules are fiddly to get right. **Randomised structures** take another route: make a few random choices, and the structure is balanced *with high probability*, whatever order the keys arrive in.

The second half of this lesson goes the other way: using randomness *as the output*. Picking k items uniformly from a stream of unknown length, and shuffling an array so every order is equally likely, both have short algorithms that are easy to get subtly wrong.

## Expected vs worst case

A randomised structure's bounds are over its **own coin flips**, not over the input. For any fixed input sequence independent of the random choices, suitably random priorities or promotion levels give expected logarithmic bounds. This is not a worst-case guarantee against every adaptive adversary. You would need to be unlucky, and the probability of being much slower than O(log n) shrinks very quickly as n grows.

That is a stronger guarantee than "average case over random inputs", which a plain BST also has, and which sorted input breaks.

## Skip lists

A sorted linked list has O(n) search, because you can only walk forward one node at a time. A **skip list**, introduced by William Pugh in 1990, adds **express lanes**: extra levels of linked lists, each containing a random subset of the level below.

```
L3: H ------------------> 30 ---------> None
L2: H ------> 10 -------> 30 ---------> None
L1: H -> 5 -> 10 -> 20 -> 30 -> 40 ---> None
```

When a key is inserted, it gets level 1, then flips a coin: heads, also join level 2; heads again, level 3; and so on. With probability p = 1/2, about half the nodes reach level 2, a quarter level 3, and the expected number of levels is about log2(n).

### Search

Start at the top-left. Move right while the next key is smaller than the target. When you cannot, drop down a level. At level 1, the next node is the target if it is present.

```python
import random

class Node:
    def __init__(self, key, level):
        self.key = key
        self.next = [None] * level

class SkipList:
    MAX = 32
    P = 0.5

    def __init__(self):
        self.head = Node(None, self.MAX)
        self.level = 1

    def _random_level(self):
        lvl = 1
        while lvl < self.MAX:
            if random.random() >= self.P:
                break
            lvl += 1
        return lvl

    def search(self, key):
        x = self.head
        top = self.level
        for i in range(top - 1, -1, -1):
            while (x.next[i]
                   and x.next[i].key < key):
                x = x.next[i]
        x = x.next[0]
        if x is None:
            return False
        return x.key == key
```

### Insert

Search as usual, but remember the last node visited on each level (`update[i]`). Those are the nodes whose pointers must change. Then pick a random level and splice the new node in on each of its levels.

```python
    def insert(self, key):
        update = [self.head] * self.MAX
        x = self.head
        top = self.level
        for i in range(top - 1, -1, -1):
            while (x.next[i]
                   and x.next[i].key < key):
                x = x.next[i]
            update[i] = x
        lvl = self._random_level()
        self.level = max(self.level, lvl)
        node = Node(key, lvl)
        for i in range(lvl):
            node.next[i] = update[i].next[i]
            update[i].next[i] = node
```

Delete is symmetrical: find `update`, then unlink the node on each level it occupies. No rotations, no colour rules.

### Cost

Read the search path backwards: from the found node, each step either goes up (if the node was promoted, probability p) or left. With p = 1/2, you expect about two steps per level, and about log2(n) levels, so search, insert and delete are **expected O(log n)**.

For uncapped levels, expected forward pointers excluding the head total n/(1 − p): **2n** at p = 1/2 and **1.33n** at p = 1/4. A cap L gives n(1 − p^L)/(1 − p). Lower p saves pointers; search constants and variance also depend on the workload and implementation.

The code caps levels at 32 for a bounded practical capacity. An asymptotic O(log n) guarantee for unbounded n requires a cap that grows with log n; a fixed cap eventually leaves too many nodes on its top level.

### Where skip lists are used

- **Redis 8.2 sorted sets** (`ZADD`, `ZRANGE`, leaderboards) pair a hash table with a skip list, using p = 1/4 and a cap of 32 levels. Each forward pointer also stores a **span**, so rank queries (`ZRANK`) are O(log n) too. Small sorted sets use a compact listpack instead.
- **LevelDB** uses a skip-list memtable. **RocksDB** uses a skip list by default and also offers other memtable representations.
- **Java's `ConcurrentSkipListMap`** is a sorted concurrent map. Splicing pointers level by level is much easier to make lock-free than tree rotations, which touch several nodes at once.

## Treaps

A **treap** is a binary search tree where each node also has a random **priority**, and the tree is a **heap** on priorities: every parent's priority beats its children's. (The name is tree + heap.)

```
      (50, .91)
      /       \
 (20, .74)   (70, .80)
    \           /
  (30, .12)  (60, .33)

BST order on keys, max-heap on priorities
```

For distinct keys and priorities, there is exactly **one** tree satisfying both rules. And it is the same tree you would get by inserting the keys in **decreasing priority order** into a plain BST. Since priorities are random, that is a random insertion order, and a BST built from random insertions has expected depth O(log n), about 2 ln n ≈ 1.39 log2(n) for the average node.

So the treap's shape no longer depends on the order keys actually arrived. Inserting 5,000 sorted keys into a plain BST gives a chain of height 5,000; a treap with independent random priorities has expected logarithmic height, though a linear-height outcome remains possible.

### Split and merge

The cleanest treap implementations use two operations:

- `split(t, key)` returns two treaps: keys below `key`, and the rest.
- `merge(a, b)` joins two treaps when every key in a is smaller than every key in b. The root is whichever root has the higher priority.

Assume distinct keys and independent priorities; `insert` below requires a key not already present. `TNode` generates a random priority, with a counter to break rare finite-precision ties. The ideal analysis assumes independent continuous priorities; this finite implementation approximates that model.

```python
from itertools import count

_serial = count()

class TNode:
    def __init__(self, key):
        self.key = key
        self.pri = (random.random(),
                    next(_serial))
        self.left = self.right = None

def split(t, key):
    # returns (keys < key, keys >= key)
    if t is None:
        return None, None
    if t.key < key:
        l, r = split(t.right, key)
        t.right = l
        return t, r
    l, r = split(t.left, key)
    t.left = r
    return l, t

def merge(a, b):
    # all keys in a < all keys in b
    if a is None or b is None:
        return a or b
    if a.pri > b.pri:
        a.right = merge(a.right, b)
        return a
    b.left = merge(a, b.left)
    return b

def insert(t, key):
    l, r = split(t, key)
    return merge(merge(l, TNode(key)), r)
```

Each runs in expected O(depth) = O(log n). Delete is two splits (cutting out the key) and one merge.

Split and merge are what make treaps popular in competitive programming. An **implicit treap** keys nodes by position (subtree sizes) instead of by value, giving a sequence that supports insert at index, delete range, cut-and-paste and reverse range, with expected O(log n) tree work when properly augmented; reversal needs lazy tags. Inserting m fresh items costs at least O(m), and deleting nodes can add reclamation work. That is the same job a rope does, which the next lesson covers.

> [!note] Tree vs list
> Skip lists and treaps solve the same problem with the same expected bounds. Skip lists are simpler to make concurrent. Treaps are a real BST, so augmenting nodes (subtree sums, sizes) and split/merge come naturally.

## Reservoir sampling

You are reading a log stream of unknown length and want a uniform random sample of k lines, using O(k) memory. You cannot store the stream, and you cannot know n in advance.

**Algorithm R** keeps the first k items. Then, for item i (0-indexed, i ≥ k), it picks a random j in `[0, i]`; if j < k, the new item replaces `sample[j]`.

```python
def reservoir(stream, k):
    sample = []
    for i, x in enumerate(stream):
        if i < k:
            sample.append(x)
        else:
            # randint is inclusive of i
            j = random.randint(0, i)
            if j < k:
                sample[j] = x
    return sample
```

### Why it is uniform

Assume 0 ≤ k ≤ n and independent uniform draws. After n items each has inclusion probability k/n. If n < k, the code returns all n items; a negative k is outside its contract.

- Item i (i ≥ k) **enters** with probability k/(i+1).
- At each later step t, it is **evicted** only if j picks exactly its slot: probability 1/(t+1). So it **survives** step t with probability t/(t+1).
- Multiply: k/(i+1) × (i+1)/(i+2) × ... × (n−1)/n. The product telescopes to **k/n**.

The first k items start in with probability 1, and the same telescoping gives k/n. Equal inclusion probabilities alone do not prove uniform subsets; Algorithm R additionally gives every k-subset probability 1/binomial(n, k), by induction over each replacement step.

Variants:

- **Algorithm L** computes how many items to skip before the next replacement, so it needs only O(k(1 + log(n/k))) random numbers instead of n.
- **Weighted sampling** (Efraimidis–Spirakis): for positive weights w and independent uniform u in (0, 1], keep the k largest `u ** (1 / w)` keys. The equivalent k smallest `-log(u) / w` scores avoid power underflow. This is sequential weighted sampling without replacement, not a promise that marginal inclusion equals k·w/sum(w).
- **Distributed**: for k = 1, choose a shard sample with probability proportional to its shard size. For larger reservoirs, simple repetition is insufficient: allocate shard counts with a hypergeometric distribution and subsample each local uniform reservoir without replacement. Each local reservoir must hold up to min(k, shard size) items.

## The Fisher–Yates shuffle

To shuffle an array uniformly, walk from the end. At each position i, swap it with a random position j in `[0, i]`, which includes i itself.

```python
def shuffle(a):
    for i in range(len(a) - 1, 0, -1):
        j = random.randint(0, i)
        a[i], a[j] = a[j], a[i]
```

Think of it as drawing cards from a hat: position n−1 gets any of the n items, position n−2 gets any of the remaining n−1, and so on. The number of equally likely runs is n × (n−1) × ... × 1 = n!, one for each permutation. It is O(n) time and in place. This is the version Durstenfeld published in 1964 and Knuth gives as Algorithm P; Python's `random.shuffle` uses it.

### The classic bug

A tempting variant swaps every position with **any** position:

```python
for i in range(n):
    j = random.randint(0, n - 1)  # wrong
    a[i], a[j] = a[j], a[i]
```

This has n^n equally likely runs but n! outcomes. For n = 3 that is 27 runs over 6 permutations, and 27 is not divisible by 6, so some permutations **must** be more likely than others. Counting them: three permutations appear 5 times in 27 and three appear 4 times.

> [!warning] Unpredictability matters
> A fair permutation algorithm does not make a predictable generator secure. Use an operating-system-backed generator such as `secrets.SystemRandom` when choices must be unpredictable.
>
> Content gap: the specific historical poker incident is omitted because a reliable primary account establishing the exact loop and seed was not verified in this audit.

Two more pitfalls:

- **Sorting with a random comparator**, such as JavaScript's `arr.sort(() => Math.random() - 0.5)`, gives biased, implementation-dependent results, because the sort assumes comparisons are consistent. Sorting by a random **key** drawn once per element is unbiased (ignoring ties), but O(n log n).
- **Too little randomness**: a 52-card deck has 52! ≈ 8 × 10^67 orders, which needs about 226 bits of state. A generator seeded with 32 bits can reach at most about 4 billion of them.

## Pitfalls

- **Off-by-one ranges**: `randint(0, i)` is inclusive in Python, `randrange(i)` is not. Using `[0, i)` in Fisher–Yates (Sattolo's algorithm) produces only single-cycle permutations, which is not uniform.
- **Ignoring the high-probability fine print**: expected O(log n) is extremely reliable at scale, but individual operations vary. Systems needing hard per-operation bounds use deterministic trees.
- **Predictable seeds**: if attackers can predict your priorities or coin flips, they can build bad inputs for skip lists and treaps after all.

## Key takeaways
- Skip lists stack randomly thinned linked lists; search drops a level when it can't go right. Expected O(log n) operations, about 2n pointers at p = 1/2.
- Treaps are BSTs heap-ordered on random priorities, equivalent to inserting in random order, so expected depth is O(log n) for any input. Split and merge make them versatile.
- Reservoir sampling keeps k uniform items from a stream of unknown length; the inclusion probability telescopes to k/n.
- Fisher–Yates swaps position i with a random j in `[0, i]`, giving n! equally likely outcomes. Swapping with any index gives n^n runs and a biased shuffle.

## Further reading
- [Skip list — Wikipedia](https://en.wikipedia.org/wiki/Skip_list)
- [Treap — Wikipedia](https://en.wikipedia.org/wiki/Treap)
- [Treap (Cartesian tree) — cp-algorithms](https://cp-algorithms.com/data_structures/treap.html)
- [Reservoir sampling — Wikipedia](https://en.wikipedia.org/wiki/Reservoir_sampling)
- [Fisher–Yates shuffle — Wikipedia](https://en.wikipedia.org/wiki/Fisher%E2%80%93Yates_shuffle)
