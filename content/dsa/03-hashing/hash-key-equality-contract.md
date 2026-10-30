---
id: hash-key-equality-contract
title: Hashable keys and equality
level: basic
minutes: 3
sourceLesson: hash-maps-sets
summary: The equality contract determines which entries a dictionary treats as the same key.
---

The equality contract determines which entries a dictionary treats as the same key. A key is not safe merely because a call to hash succeeds: its equality-relevant state must also remain stable while stored.

## Keys must be hashable

A hash table finds a key by recomputing its hash. If a key's hash could change after insertion, the table would look in the wrong bucket and the entry would be lost. So the contract is:

1. If `a == b`, then `hash(a) == hash(b)`. Equal keys must land in the same bucket.
2. A key's hash and equality-relevant state must stay stable while it is in the table.

The reverse of rule 1 is *not* required: unequal keys may share a hash. That is just a collision.

In Python, immutable built-ins (`int`, `str`, `tuple` of hashables, `frozenset`) are hashable. The built-ins list, dict and set are not hashable. Mutability alone is not the general test: custom mutable objects can use stable identity equality/hashing, and an immutable class can disable hashing:

```python
d = {}
d[(1, 2)] = "ok"     # tuple: fine
d[[1, 2]] = "no"     # TypeError: unhashable
```

The second assignment deliberately fails: the tuple entry is stored, then the list key raises `TypeError` and execution stops unless the caller handles it.

> [!warning] Equal keys collapse
> Because `1 == 1.0 == True` in Python, they are the same dict key. `{1: "a", True: "b"}` gives `{1: "b"}`: the second assignment updates the value, keeping the first key object.

If you define `__eq__` on your own class, Python sets `__hash__` to `None`, making instances unhashable, unless you also define `__hash__`. In Java, overriding `equals` without `hashCode` is a classic bug: two equal objects can have different hashes, causing lookup to miss even if bucket reduction happens to coincide.

> [!analogy] Real-world analogy: filing by a name that can change
> An office files each customer's paperwork in a drawer chosen by the first letter of their surname. A customer marries and changes surname, but nobody moves the paperwork.
>
> **How it maps:** the surname is a key's equality-relevant state and the drawer is its bucket. Searching under the new name opens the wrong drawer; searching under the old name finds paperwork whose name no longer matches. The paperwork is still in the cabinet but unreachable, just like a mutated key in a set.
>
> **Where it stops:** a clerk could notice and refile the paperwork. A hash table never notices a mutation, so you must remove the key before changing it and reinsert it afterwards, or use a stable key such as a customer ID.

## Designing a key safely

Separate an object’s identity from its current contents. A mutable customer record can be stored as a value while its stable customer ID is the key. Updating the record’s address then leaves the index intact. Using all mutable fields as the key makes every change an index-maintenance operation instead.

For a custom value object, choose the same fields for equality and hashing. Two points considered equal by their coordinates must hash from those coordinates as well. If coordinates can change, freeze the key object or remove it before changing the fields and reinsert it afterwards. Defining a hash from one field and equality from another does not satisfy the contract.

A tuple is not automatically a safe key just because the outer container is immutable. Its elements must also be hashable; a tuple containing a list fails when hashed. A frozenset, unlike a set, is immutable and hashable. Neither object promises that a bad custom element implementation becomes sound merely by being wrapped.

## Key takeaways
- Equal keys must have equal hashes; unequal keys may collide.
- Hash and equality-relevant state must remain stable while a key is stored.
- Immutable containers require hashable elements; mutability alone is not the general test.

## Further reading
- [Python 3.14 data model: hashing](https://docs.python.org/3.14/reference/datamodel.html#object.__hash__)
