---
id: adv-randomised-structures
title: Randomised structures and sampling
level: advanced
minutes: 15
summary: How coin flips replace rebalancing in skip lists and treaps, and how reservoir sampling and the Fisher–Yates shuffle produce provably uniform random choices.
---

Balanced binary search trees such as red–black and AVL trees guarantee O(log n) operations (time growing in proportion to the logarithm of n, the number of keys stored), but their rebalancing rules are fiddly to get right. **Randomised structures** take another route: make a few random choices, and the structure is balanced *with high probability*, whatever order the keys arrive in.

The second half of this lesson goes the other way: using randomness *as the output*. Picking k items uniformly from a stream of unknown length, and shuffling an array so every order is equally likely, both have short algorithms that are easy to get subtly wrong.

## Expected vs worst case

A randomised structure's bounds are over its **own coin flips**, not over the input. For any fixed input sequence independent of the random choices, suitably random priorities or promotion levels give expected logarithmic bounds. This is not a worst-case guarantee against every adaptive adversary. You would need to be unlucky, and the probability of being much slower than O(log n), where n is the number of keys, shrinks very quickly as n grows.

That is a stronger guarantee than "average case over random inputs", which a plain BST also has, and which sorted input breaks.

## Skip lists

A sorted linked list of n nodes has O(n) search, because you can only walk forward one node at a time. A **skip list**, introduced by William Pugh in 1990, adds **express lanes**: extra levels of linked lists, each containing a random subset of the level below.

```
L3: H ------------------> 30 ---------> None
L2: H ------> 10 -------> 30 ---------> None
L1: H -> 5 -> 10 -> 20 -> 30 -> 40 ---> None
```

When a key is inserted, it gets level 1, then flips a coin: heads, also join level 2; heads again, level 3; and so on. The chance of heads is called the promotion probability. Three numbers follow from it:

```formula
P(ℓ ≥ m) = p^{m − 1}
E[ℓ] = 1 / (1 − p)
H ≈ log_{1/p}(n)
P(ℓ ≥ 3) = (1/2)^2 = 1/4
E[ℓ] = 1 / (1 − 1/2) = 2
H ≈ log_2(1,000,000) ≈ 20
where
ℓ: the level a newly inserted key ends up with (1, 2, 3, …)
m: any level number we ask about
p: the promotion probability, the chance of heads on each flip; 1/2 in the example, 1/4 in Redis
P(ℓ ≥ m): the probability that the key reaches level m or higher
p^{m − 1}: m − 1 copies of p multiplied together, one factor per heads needed
E[ℓ]: the expected (long-run average) level of a key
H: the number of levels the whole list typically has
n: the number of keys in the skip list
log_{1/p}(n): the logarithm of n to base 1/p: how many times you can divide n by 1/p before reaching 1
log_2(n): the base-2 logarithm of n, the special case p = 1/2
≥: is at least
≈: approximately equal to
In words: each extra level needs one more heads, so levels thin out geometrically; an average key sits on 2 levels at p = 1/2, and the tallest towers reach about log_2(n) levels.
```

So with a million keys and fair coins, about half the nodes reach level 2, a quarter level 3, and the list is about 20 levels tall. These are averages over the coin flips; any single run can be a little taller or shorter.

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

Read the search path backwards: from the found node, each step either goes up (if that node was promoted, which happens with the promotion probability) or left. Pugh's analysis turns that into an expected step count:

```formula
C ≈ (1 / p) × log_{1/p}(n)
C ≈ 2 × log_2(1,000,000) ≈ 2 × 20 = 40
C ≈ 4 × log_4(1,000,000) ≈ 4 × 10 = 40
where
C: the expected number of pointer steps in one search
p: the promotion probability (1/2 in the second line, 1/4 in the third)
1 / p: the expected number of steps spent on each level before the path climbs
n: the number of keys, a million here
log_{1/p}(n): the logarithm of n to base 1/p, about the number of levels
log_2, log_4: logarithms to base 2 and base 4
≈: approximately equal to
In words: about 1/p steps per level times about log_{1/p}(n) levels, so search, insert and delete are expected O(log n).
```

O(log n) means the cost grows in proportion to the logarithm of n. Lower p means fewer, longer hops per level but fewer levels, so at a million keys both settings take about 40 steps. Pugh's full formula adds a small constant; the estimate ignores it.

The memory cost is the number of forward pointers, one per level each node occupies (not counting the head):

```formula
N_ptr = n / (1 − p)
N_ptr = n / (1 − 1/2) = 2 × n
N_ptr = n / (1 − 1/4) ≈ 1.33 × n
N_cap = n × (1 − p^L) / (1 − p)
where
N_ptr: the expected total number of forward pointers when levels are not capped
N_cap: the expected total when no node may exceed L levels
n: the number of keys
p: the promotion probability
L: the level cap (32 in the code above)
p^L: L copies of p multiplied together
≈: approximately equal to
In words: each key holds on average 1/(1 − p) pointers, so 2 per key at p = 1/2 and about 1.33 per key at p = 1/4; a cap trims a tiny amount off that.
```

A million keys therefore cost about 2 million pointers with fair coins and about 1.33 million with a promotion probability of 1/4. Lower p saves pointers; search constants and variance also depend on the workload and implementation.

The code caps levels at 32 for a bounded practical capacity. The number of nodes expected to reach the cap shows when that stops being enough:

```formula
N_top = n × p^{L − 1}
N_top = n × (1/4)^31 ≈ n / (4.6 × 10^18)
where
N_top: the expected number of nodes that would want to reach the top (capped) level
n: the number of keys
p: the promotion probability, 1/4 in the second line
L: the level cap, 32 in the second line
p^{L − 1}: L − 1 copies of p multiplied together
≈: approximately equal to
In words: with 32 levels at p = 1/4, you would need billions of billions of keys before the top level gets crowded.
```

Below that size the cap is invisible. An asymptotic O(log n) guarantee for unbounded n requires a cap that grows with log n; a fixed cap eventually leaves too many nodes on its top level.

### Where skip lists are used

- **Redis 8.2 sorted sets** (`ZADD`, `ZRANGE`, leaderboards) pair a hash table with a skip list, using a promotion probability of 1/4 and a cap of 32 levels. Each forward pointer also stores a **span**, so rank queries (`ZRANK`) are O(log n) too, where n is the number of members in the set. Small sorted sets use a compact listpack instead.
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

For distinct keys and priorities, there is exactly **one** tree satisfying both rules. And it is the same tree you would get by inserting the keys in **decreasing priority order** into a plain BST. Since priorities are random, that is a random insertion order, and a BST built from random insertions has expected depth O(log n), where n is the number of keys:

```formula
D ≈ 2 × ln(n) − 2.85
D ≈ 2 × ln(5000) − 2.85 ≈ 17.0 − 2.85 ≈ 14
2 × ln(n) ≈ 1.39 × log_2(n)
where
D: the expected depth of an average node, in edges from the root
n: the number of keys, 5,000 in the second line
ln(n): the natural logarithm of n, to base e ≈ 2.718
log_2(n): the base-2 logarithm of n; 2 × ln(n) equals about 1.39 × log_2(n) because ln(2) ≈ 0.693
≈: approximately equal to
In words: the average depth grows like 2 ln(n), less a small constant of about 2.85, so for large n a randomly built tree is only about 39 % deeper on average than a perfectly balanced one.
```

The average depth is about 14 for 5,000 keys (the leading term 2 ln(n) alone gives 17); the deepest node is somewhat deeper, but still logarithmic in expectation.

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

Each runs in expected time proportional to the tree's depth, which is O(log n) for n keys. Delete is two splits (cutting out the key) and one merge.

Split and merge are what make treaps popular in competitive programming. An **implicit treap** keys nodes by position (subtree sizes) instead of by value, giving a sequence that supports insert at index, delete range, cut-and-paste and reverse range, with expected O(log n) tree work for a sequence of n items when properly augmented; reversal needs lazy tags. Inserting m fresh items costs at least O(m), and deleting nodes can add reclamation work. That is the same job a rope does, which the next lesson covers.

> [!note] Tree vs list
> Skip lists and treaps solve the same problem with the same expected bounds. Skip lists are simpler to make concurrent. Treaps are a real BST, so augmenting nodes (subtree sums, sizes) and split/merge come naturally.

## Reservoir sampling

You are reading a log stream of unknown length and want a uniform random sample of k lines, using O(k) memory. You cannot store the stream, and you cannot know n in advance.

**Algorithm R** keeps the first k items. Then, for each later item `i` (counting from 0), it draws `j = randint(0, i)`; if `j < k`, the new item replaces `sample[j]`.

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

Assume independent uniform draws and a sample size no bigger than the stream. Follow one item: it must first **enter** the sample, then **survive** every later step, where it is evicted only if the draw picks exactly its slot. Multiplying those chances, most factors cancel (the product **telescopes**):

```formula
P_enter = k / (i + 1)
P_survive(t) = t / (t + 1)
P = k/(i+1) × (i+1)/(i+2) × … × (n−1)/n
P = k / n
P = 10 / 1000 = 0.01
where
k: the sample size, 10 in the last line
n: the total number of items in the stream, 1,000 in the last line; k ≤ n
i: the position of the item we follow, counting from 0, with i ≥ k
t: a later step, i < t ≤ n − 1
P_enter: the probability the item gets into the sample when it arrives
P_survive(t): the probability it is not evicted at step t (one minus 1/(t + 1))
P: the probability it is in the final sample
…: and so on, one factor per later step
≤: is at most
In words: each item's chance of getting in shrinks exactly as fast as later items' chances of knocking it out, so every item ends with the same chance, k out of n.
```

The first k items start in with probability 1, and the same telescoping gives k/n: with 10 slots and 1,000 lines, every line has a 1 % chance. If the stream is shorter than k, the code returns everything it saw; a negative k is outside its contract.

Equal inclusion probabilities alone do not prove uniform subsets. Algorithm R additionally gives every possible sample the same probability, by induction over each replacement step:

```formula
P(S) = 1 / C(n, k)
C(n, k) = n! / (k! × (n − k)!)
C(5, 2) = 120 / (2 × 6) = 10
where
S: one particular set of k items
P(S): the probability that the final sample is exactly S
C(n, k): "n choose k", the number of different k-item sets you can pick from n items
n!: n factorial, 1 × 2 × … × n
k: the sample size
n: the stream length
In words: every possible sample of k items is equally likely; from 5 items with 2 slots there are 10 possible pairs, each with probability 1/10.
```

Variants:

- **Algorithm L** computes how many items to skip before the next replacement, so it draws far fewer random numbers than one per item:

```formula
R = O(k × (1 + log(n / k)))
R ≈ 100 × (1 + ln(10^7)) ≈ 1,700
where
R: the number of random numbers Algorithm L needs
k: the sample size, 100 in the second line
n: the stream length, 10^9 (a billion) in the second line
log: a logarithm; the base only changes a constant factor
ln: the natural logarithm, to base e ≈ 2.718; ln(10^7) ≈ 16.1
O(f): grows at most in proportion to f
≈: approximately equal to
In words: Algorithm L's random-number count grows with the logarithm of the stream length, not the length itself.
```

  For a 100-line sample from a billion lines, that is on the order of 1,700 random numbers instead of a billion (the second line is an order-of-magnitude estimate).

- **Weighted sampling** (Efraimidis–Spirakis): give each item a random key based on its weight and keep the k items with the largest keys, as below. This is sequential weighted sampling without replacement. It does not promise that each item's inclusion probability is k times its share of the total weight.

```formula
K = u^{1/w}
s = −ln(u) / w
K = 0.25^{1/2} = 0.5
s = −ln(0.25) / 2 ≈ 0.693
where
w: the item's weight, a positive number; 2 in the example
u: a fresh uniform random number with 0 < u ≤ 1; 0.25 in the example
K: the item's key; keep the k items with the largest K
s: the equivalent score; keep the k smallest s
k: the sample size
ln: the natural logarithm, to base e ≈ 2.718
u^{1/w}: u raised to the power 1 / w (for w = 2, the square root of u)
≈: approximately equal to
In words: heavier items get keys pushed towards 1, so they win more often; the logarithm form ranks items in exactly the same order and avoids tiny numbers that underflow.
```

- **Distributed**: for a single-item sample, choose one shard's sample with probability proportional to its shard size. For larger reservoirs, simple repetition is insufficient: allocate shard counts with a hypergeometric distribution and subsample each local uniform reservoir without replacement. Each local reservoir must hold up to k items, or the whole shard if it is smaller.

## The Fisher–Yates shuffle

To shuffle an array uniformly, walk from the end. At each position `i`, swap `a[i]` with `a[j]` for `j = randint(0, i)`, which can pick `i` itself.

```python
def shuffle(a):
    for i in range(len(a) - 1, 0, -1):
        j = random.randint(0, i)
        a[i], a[j] = a[j], a[i]
```

Think of it as drawing cards from a hat: the last position gets any of the items, the one before it any of the items left, and so on. Count the equally likely runs:

```formula
N_runs = n × (n − 1) × … × 1 = n!
N_runs = 3 × 2 × 1 = 6 = 3!
where
N_runs: the number of different, equally likely sequences of random draws
n: the number of items in the array, 3 in the second line
n!: n factorial, the product of every whole number from 1 to n; also the number of permutations (orderings) of n items
…: and so on down to 1
In words: the draws can play out in exactly as many ways as there are orderings, one run per ordering, so every ordering is equally likely.
```

For three items there are 6 runs and 6 orderings, each with probability 1/6. It takes O(n) time (proportional to n) and works in place. This is the version Durstenfeld published in 1964 and Knuth gives as Algorithm P; Python's `random.shuffle` uses it.

### The classic bug

A tempting variant swaps every position with **any** position:

```python
for i in range(n):
    j = random.randint(0, n - 1)  # wrong
    a[i], a[j] = a[j], a[i]
```

Count its runs against the possible orderings:

```formula
N_runs = n^n
N_perm = n!
N_runs = 3^3 = 27
N_perm = 3! = 6
27 / 6 = 4.5
where
N_runs: the number of equally likely sequences of random draws
N_perm: the number of possible orderings (permutations)
n: the number of items, 3 in the example
n^n: n copies of n multiplied together, because each of n steps picks from all n positions
n!: n factorial, 1 × 2 × … × n
In words: 27 equally likely runs cannot be shared evenly among 6 orderings, so some orderings must come up more often.
```

Counting them: three permutations appear 5 times in 27 and three appear 4 times, so some come out with probability 5/27 ≈ 18.5 % instead of 1/6 ≈ 16.7 %.

> [!warning] Unpredictability matters
> A fair permutation algorithm does not make a predictable generator secure. Use an operating-system-backed generator such as `secrets.SystemRandom` when choices must be unpredictable.
>
> Content gap: the specific historical poker incident is omitted because a reliable primary account establishing the exact loop and seed was not verified in this audit.

Two more pitfalls:

- **Sorting with a random comparator**, such as JavaScript's `arr.sort(() => Math.random() - 0.5)`, gives biased, implementation-dependent results, because the sort assumes comparisons are consistent. Sorting by a random **key** drawn once per element is unbiased (ignoring ties), but O(n log n) for n elements.
- **Too little randomness**: a generator can only produce as many shuffles as it has possible seeds, as below.

```formula
52! ≈ 8 × 10^67
log_2(52!) ≈ 225.6
2^32 ≈ 4.3 × 10^9
where
52!: 52 factorial, the number of orders of a 52-card deck
log_2(52!): the base-2 logarithm of 52!: the number of bits needed to give every order its own state
2^32: the number of different seeds a 32-bit seed allows
≈: approximately equal to
In words: a deck has about 8 × 10^67 orders, needing about 226 bits of state, but a 32-bit seed can start only about 4.3 billion different shuffles.
```

  So a generator seeded with 32 bits can reach at most about 4 billion of the deck's orders, a vanishingly small fraction.

## Pitfalls

- **Off-by-one ranges**: `randint(0, i)` is inclusive in Python, `randrange(i)` is not. Drawing `j` with `randrange(i)` in Fisher–Yates, so position `i` can never keep its own item, is Sattolo's algorithm: it produces only single-cycle permutations, which is not uniform.
- **Ignoring the high-probability fine print**: expected O(log n), for n keys, is extremely reliable at scale, but individual operations vary. Systems needing hard per-operation bounds use deterministic trees.
- **Predictable seeds**: if attackers can predict your priorities or coin flips, they can build bad inputs for skip lists and treaps after all.

## Key takeaways
- Skip lists stack randomly thinned linked lists; search drops a level when it can't go right. Expected O(log n) operations for n keys, and about two pointers per key with a promotion probability of 1/2.
- Treaps are BSTs heap-ordered on random priorities, equivalent to inserting in random order, so expected depth is O(log n) for n keys and any input. Split and merge make them versatile.
- Reservoir sampling keeps k uniform items from a stream of unknown length; every item ends up in the sample with the same probability, k divided by the stream length.
- Fisher–Yates swaps each position with a random position at or before it, giving one equally likely run per ordering. Swapping with any index gives a run count that does not divide evenly among the orderings, so the shuffle is biased.

## Further reading
- [Skip list — Wikipedia](https://en.wikipedia.org/wiki/Skip_list)
- [Treap — Wikipedia](https://en.wikipedia.org/wiki/Treap)
- [Treap (Cartesian tree) — cp-algorithms](https://cp-algorithms.com/data_structures/treap.html)
- [Reservoir sampling — Wikipedia](https://en.wikipedia.org/wiki/Reservoir_sampling)
- [Fisher–Yates shuffle — Wikipedia](https://en.wikipedia.org/wiki/Fisher%E2%80%93Yates_shuffle)
