---
id: disc-equivalence-classes
title: "Equivalence classes, partitions and union-find"
level: basic
minutes: 5
summary: "Equivalence relations partition a set into disjoint classes, and every partition defines one."
sourceLesson: disc-relations
---

## Equivalence relations

A relation that is **reflexive, symmetric and transitive** is an **equivalence relation**. It formalises "the same in the way we care about".

Examples:

- **Congruence modulo n**: two integers are related when they leave the same remainder after division by n (see below). Mod 3 groups integers by remainder.
- **Same connected component** in an undirected graph.
- **Case-insensitive equality** of strings: "Hello" and "HELLO" are equivalent.
- **Same hash bucket**: two keys are related when the hash function sends them to the same value. Any relation of the form "same output of some function" is an equivalence relation.

The first and last examples in symbols:

```formula
a ≡ b (mod n)   means   n | (a − b)
17 − 5 = 12 = 4 × 3
so   17 ≡ 5 (mod 3)
x ~ y   means   f(x) = f(y)
where
a, b: integers
n: the modulus, a positive integer (3 in the example)
≡: is congruent to: the two numbers leave the same remainder after division by n
mod: modulo: names the number n we divide by
|: divides: n | m means m is a whole-number multiple of n
x, y: any two elements, such as two hash keys
~: is equivalent to (the relation being defined)
f: any function, such as a hash function h or "birth month"
f(x): the output of f for input x
In words: a and b are congruent mod n when their difference is a multiple of n; 17 and 5 both leave remainder 2 when divided by 3. In general, "x and y give the same output" is always reflexive, symmetric and transitive, because equality of outputs is.
```

The **equivalence class** of an element is everything equivalent to it:

```formula
[a] = { x ∈ A : x ~ a }
where
[a]: the equivalence class of a
a: an element of the set A
A: the set the relation is on
x: a stand-in for each element of A
~: the equivalence relation
∈: is an element of
{ x ∈ A : … }: the set of all x in A that make the condition after the colon true
In words: the class of a collects every element equivalent to a, including a itself.
```

Case-insensitive equality needs a fixed normalisation rule. Likewise, “same hash bucket” means the same final bucket-selection function, not necessarily an equal full hash value.

The crucial theorem: **the equivalence classes partition the set**. Every element is in exactly one class, and two classes are either identical or disjoint.

For congruence mod 3, the integers split into three classes:

```formula
[0] = {…, −3, 0, 3, 6, …}
[1] = {…, −2, 1, 4, 7, …}
[2] = {…, −1, 2, 5, 8, …}
where
[0], [1], [2]: the equivalence classes of 0, 1 and 2 under congruence mod 3: the integers leaving remainder 0, 1 and 2 when divided by 3
{ }: the set of the things listed inside
…: and so on without end, in both directions
In words: every integer lands in exactly one of three classes by its remainder mod 3. Negative numbers follow the same pattern: −2 = −1 × 3 + 1, so −2 is in [1].
```

The converse holds too: any partition defines an equivalence relation ("in the same block"). So the number of equivalence relations on an n-element set equals the number of partitions, the **Bell number**: 1, 1, 2, 5, 15, 52, … for sets of 0, 1, 2, 3, 4 and 5 elements. For example, {a, b, c} has 5 partitions: everything together, the three ways to pair two elements and leave one alone, and all three apart.

### Equivalence relations in code

The **union-find** (disjoint-set) data structure maintains an equivalence relation as you add facts like "a ~ b". Each class is a tree with a representative at the root. Because the relation is transitive, merging two classes is all you ever need to do.

```python
parent = {}

def find(x):
    parent.setdefault(x, x)
    while parent[x] != x:
        # Halve paths to speed later finds.
        parent[x] = parent[parent[x]]
        x = parent[x]
    return x

def union(a, b):
    # Join the roots of the two classes.
    parent[find(a)] = find(b)

union('a', 'b'); union('b', 'c')
# a and c now belong to one class.
find('a') == find('c')   # True
```

Union-find tracks components for Kruskal's algorithm and can support type-variable unification. Full type unification also needs to handle type structure and checks such as the occurs check.

Python's own contract relies on this theory. Well-behaved value equality is normally an equivalence relation, but Python does not enforce these laws and NaN is a standard exception. Hashable objects that compare equal must have equal hashes, and their hash must stay stable while used as keys.

> [!warning] "Approximately equal" is not an equivalence
> Calling two numbers equal when they are within a small tolerance of each other breaks transitivity, so it cannot be used to bucket values into consistent groups. The example below shows the chain that fails.

```formula
x ~ y   means   |x − y| < 0.1
|0.0 − 0.08| = 0.08   so 0.0 ~ 0.08
|0.08 − 0.16| = 0.08   so 0.08 ~ 0.16
|0.0 − 0.16| = 0.16   so 0.0 ≁ 0.16
where
x, y: any two real numbers
~: "approximately equal", the relation being tested
≁: is not related by ~
| |: around a number, the absolute value: its size ignoring the sign, so |x − y| is the distance between x and y
<: is less than
In words: 0.0 is close to 0.08, and 0.08 is close to 0.16, but 0.0 is not close to 0.16, so the relation is not transitive.
```

## Key takeaways

- Equivalence relations partition a set into disjoint classes, and every partition defines one.
- Union-find merges classes; tolerance-based equality fails transitivity and cannot define consistent classes.

## Further reading

- [Equivalence relation — Wikipedia](https://en.wikipedia.org/wiki/Equivalence_relation)
- [Mathematics for Computer Science — MIT](https://courses.csail.mit.edu/6.042/spring18/mcs.pdf)
