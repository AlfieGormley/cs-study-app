---
id: disc-set-membership
title: "Set membership and subsets"
level: basic
minutes: 5
summary: "Membership asks whether one object belongs to a set; subset asks whether every element belongs."
sourceLesson: disc-sets-functions
---

Almost every structure in computer science is built from two ideas: a **mathematical set** (a collection of things) and a **mathematical function** (a rule that maps each thing in one set to exactly one thing in another). A simple model treats a type as a set of values and a mathematical relation as a set of tuples. SQL tables can contain duplicate rows, and a hash table usually maps a key through a hash value to a bucket. Getting fluent with the vocabulary pays off everywhere else in this subject.

## Sets

A set is an unordered collection of distinct elements. Curly braces list what is in it, and only membership counts: the order you write the elements in and any repeats make no difference.

Writing the numbers 1, 2 and 3 in a different order, or listing 1 twice, still describes the same three-element set.

These concepts have notation you will see constantly:

| Concept | Meaning |
|---|---|
| Membership | An object belongs to a set |
| Non-membership | An object does not belong |
| Subset | Every element also belongs to another set |
| Proper subset | A subset that is not equal |
| Empty set | A set with no elements |
| Cardinality | The size of a set |

For example, take a two-element set containing 1 and 2, and a three-element set also containing 3:

```formula essential
1 ∈ A     3 ∉ A
A ⊆ B     A ⊂ B
|A| = 2
where
A: the example set {1, 2}
B: the example set {1, 2, 3}
∈: is an element of
∉: is not an element of
⊆: is a subset of: every element of the left-hand set is also in the right-hand set (the two may be equal)
⊂: is a proper subset of: a subset that is not equal, so the right-hand set has at least one extra element
| |: vertical bars around a set mean its cardinality: the number of elements it has
In words: 1 is in A but 3 is not; everything in A is also in B, and B has an extra element (3), so A is a proper subset of B; A has 2 elements and B has 3.
```

Sets can be written by listing elements, or with **set-builder notation**, which describes the elements by a rule. It resembles a Python comprehension, but mathematical sets can also be infinite:

```formula reference
E = { x ∈ ℤ : 0 ≤ x < 10, x mod 2 = 0 }
where
E: the set being defined (the even numbers below 10)
x: a stand-in for each candidate element
ℤ: the integers: …, −2, −1, 0, 1, 2, …
∈: is an element of
{ x ∈ ℤ : … }: set-builder notation: the set of all integers x that make the condition after the colon true. The colon reads "such that"; some books write a vertical bar | instead
≤: is less than or equal to
<: is less than
mod: the remainder after dividing, so x mod 2 = 0 means x is even
In words: A set-builder rule keeps exactly the integers from zero through nine that are even.
```

For example, select even integers from zero through nine in Python, where `%` is the remainder operator:

```python
# Keep exactly the even candidates below 10.
E = {x for x in range(10) if x % 2 == 0}
```

Common number sets: ℕ (natural numbers; whether 0 is included varies by author, so check), ℤ (integers), ℚ (rationals, the fractions of integers) and ℝ (reals, every point on the number line).

> [!warning] Elements versus subsets
> The empty set is a subset of every set, but it is an element of a set only if that set literally lists the empty set inside its braces. The set containing just the empty set has one element; the empty set itself has none.

```formula essential
∅ ⊆ A   for every A
∅ ∈ {∅}     ∅ ∉ {1, 2}
where
∅: the empty set, the set with no elements, also written {}
A: any set at all
⊆: is a subset of: every element of the left-hand set is in the right-hand set
∈: is an element of
∉: is not an element of
{ }: curly braces: the set of the things listed inside
In words: the empty set is a subset of everything (it has no element that could fail to be in A), but it is only an element of a set that lists it, like {∅}. That set has one element; ∅ has none.
```

Sets are unordered and deduplicated. Converting a list to a set and back loses order and duplicates. Python sets only hold hashable elements, so use `frozenset` for a set of sets.

> [!analogy] Real-world analogy: An empty shopping basket
> An empty basket contains nothing; a basket holding an empty box contains one object.
>
> **How it maps:** Membership asks what is inside the outer collection. A collection holding the empty set has one element even though that element itself contains nothing.
>
> **Where it stops:** Physical baskets have capacity and order, while mathematical sets do not.

## Key takeaways

- Membership asks whether one object belongs to a set; subset asks whether every element belongs.
- The empty set is a subset of every set; a set containing the empty set has one element.

## Further reading

- [Set (mathematics) — Wikipedia](https://en.wikipedia.org/wiki/Set_(mathematics))
- [Mathematics for Computer Science — MIT](https://courses.csail.mit.edu/6.042/spring18/mcs.pdf)
