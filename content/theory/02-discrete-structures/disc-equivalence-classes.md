---
id: disc-equivalence-classes
title: "Equivalence classes, partitions and union-find"
level: basic
minutes: 4
summary: "Equivalence relations partition a set into disjoint classes, and every partition defines one."
sourceLesson: disc-relations
---

## Equivalence relations

A relation that is **reflexive, symmetric and transitive** is an **equivalence relation**. It formalises "the same in the way we care about".

Examples:

- **Modular congruence**: integers are related when they leave the same remainder under one fixed positive modulus.
- **Same connected component** in an undirected graph.
- **Case-insensitive equality** of strings: "Hello" and "HELLO" are equivalent.
- **Same hash bucket**: two keys are related when the same fixed bucket-selection function gives the same bucket.

Integers 17 and 5 both leave remainder 2 when divided by 3, so they are equivalent under congruence modulo 3. More generally, equality of outputs under one fixed function is reflexive, symmetric and transitive.

The **equivalence class** of an element is everything equivalent to it:

```formula essential
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

Modulo 3, the classes collect integers with remainder 0, 1 or 2. Every integer belongs to exactly one, including negative integers under the non-negative remainder convention.

The converse holds too: any partition defines an equivalence relation, “in the same block”. Counting equivalence relations therefore amounts to counting partitions; these counts are called **Bell numbers**. Ordering the blocks or their members does not create a new partition.

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

With a strict tolerance of 0.1, 0 is close to 0.08 and 0.08 is close to 0.16, but 0 is not close to 0.16. Chaining “close” judgements therefore need not preserve closeness.

> [!analogy] Real-world analogy: Sorting laundry by colour label
> Assign every garment one fixed colour label and put matching labels together.
>
> **How it maps:** Equality of a fixed label forms equivalence classes. Every item belongs to exactly one class, and merging classes is different from changing individual labels.
>
> **Where it stops:** Informal judgements like “nearly the same colour” need not be transitive, so they do not automatically define the same kind of grouping.

## Key takeaways

- Equivalence relations partition a set into disjoint classes, and every partition defines one.
- Union-find merges classes; tolerance-based equality fails transitivity and cannot define consistent classes.

## Further reading

- [Equivalence relation — Wikipedia](https://en.wikipedia.org/wiki/Equivalence_relation)
- [Mathematics for Computer Science — MIT](https://courses.csail.mit.edu/6.042/spring18/mcs.pdf)
