---
id: fp-persistence-cons
title: Persistence and shared list tails
level: advanced
minutes: 4
sourceLesson: fp-persistent-data
summary: Persistence keeps old versions usable after updates.
---

Immutability has an obvious cost. If you can never change a list in place, then "add one element" seems to mean "copy the whole list and add one element". Do that in a loop over a million items and you've written an O(n²) algorithm, where n is the number of items: each step copies everything added so far.

```formula
0 + 1 + 2 + ... + (n − 1) = n(n − 1) / 2
n(n − 1) / 2 = O(n^2)
where
n: the number of items added, one per loop step
...: "and so on" for every step in between
O(n^2): Big-O notation: grows in proportion to n squared (n × n)
In words: the k-th step copies the k − 1 items already there, and those copies add up to about half of n squared.
```

For a million appends, the exact count is 499,999,500,000 item-reference copies: about five hundred billion.

Efficient persistent collections reduce that cost through sharing. **Persistence** means: every "update" returns a new version, the old version stays valid, and efficient implementations can share unchanged memory. Only the small part that actually changed is new.

This lesson shows how that works, from the humble linked list up to the 32-way tries that power Clojure's vectors and maps, and where the trick stops being free.

## What "persistent" means

Here *persistent* has nothing to do with disks. It means old versions persist after an update.

| Kind | Old versions can be |
|---|---|
| Ephemeral (normal) | gone after update |
| Partially persistent | read, not updated |
| Fully persistent | read and updated |
| Confluent | merged with each other |

Purely functional structures are fully persistent automatically: nothing is ever mutated, so every version you hold a reference to is still intact and can be the starting point of new updates.

The naive way to get this is to copy everything on every update. The real way is **structural sharing**.

## The linked list: sharing for free

The singly linked list (a *cons list*) is the simplest persistent structure. Each cell holds a value and a pointer to the rest:

```python
# Distinct heads reuse one immutable tail.
xs = (3, None)
ys = (2, xs)       # [2, 3]
a  = (1, ys)       # [1, 2, 3]
b  = (9, ys)       # [9, 2, 3]

a[1] is b[1]       # True: shared tail
```

```
a --> [1|*]--+
             v
           [2|*]--> [3|/]
             ^
b --> [9|*]--+
```

Prepending to a list allocates one cell and points it at the old list. It's O(1) time and space, and the old list is untouched. That's why Haskell, Lisp, Erlang and Elixir lists grow at the front.

The costs show up at the other end. In this table n is the list's length and i is the position being read or changed (0 for the first cell). O(1) means a fixed bound independent of list length; O(n) grows at most linearly with length and O(i + 1) includes the constant work at index zero:

| Operation | Cost | Why |
|---|---|---|
| Prepend | O(1) | new head, shared tail |
| Head / tail | O(1) | follow one pointer |
| Append | O(n) | copy every cell |
| Index i | O(i + 1) | walk i pointers and read one cell |
| Update at i | O(i + 1) | copy the prefix through that position |

Appending must copy every cell, because the last cell's pointer has to change and every cell before it points (indirectly) at that one. For this immutable linked-list path-copying approach, copy the prefix leading to the change; persistence in general has other implementation techniques.

## Key takeaways
- Persistence keeps old versions usable after updates.
- A cons-list prepend shares the old tail in constant time.

## Further reading
- [Okasaki: Purely Functional Data Structures](https://www.cs.cmu.edu/~rwh/students/okasaki.pdf)
- [Haskell List](https://hackage.haskell.org/package/base/docs/Data-List.html)
