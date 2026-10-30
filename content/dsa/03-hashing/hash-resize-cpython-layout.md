---
id: hash-resize-cpython-layout
title: CPython dictionaries: layout and probing
level: intermediate
minutes: 5
sourceLesson: hash-resizing
summary: CPython's dict pairs a sparse index array with dense insertion-ordered entries, grows at two-thirds full and mixes high hash bits into its probes.
---

Python the language promises how a dict behaves, including insertion order. How CPython achieves that is an implementation detail, and it shows how the ideas in this module fit together in a real table. Everything below describes CPython 3.14's ordinary dict with general keys; other Python implementations, and other CPython layouts, can differ.

## How CPython's dict works

CPython's dict is open addressing with a **compact layout**, introduced in Python 3.6 and based on a 2012 proposal by Raymond Hettinger. The simplified description below covers an ordinary combined table with general keys. Split/key-sharing tables and Unicode-only entries have different layouts. There are two arrays:

```
indices (small ints, 1 per slot)
[ -,  1,  -,  0,  -,  -,  2,  - ]

entries (dense, insertion order)
0: hash, 'cat', 1
1: hash, 'dog', 2
2: hash, 'eel', 3
```

- The **indices array** is the hash table proper. Each slot holds an index into `entries`, and uses 1, 2, 4 or 8 bytes depending on the table size, so a small dict's index is tiny.
- The **entries array** stores (hash, key, value) in insertion order. That is why dicts preserve insertion order: iteration just walks `entries`.

Compared with the old design, which stored full entries in a sparse array (24 bytes per general entry on the illustrated 64-bit build), this saves a lot of memory, because only the cheap index array is sparse.

> [!analogy] Real-world analogy: a visitors' book with a lookup card
> A reception desk writes each visitor on the next free line of a visitors' book, in arrival order. To find someone quickly, it also keeps a small card of numbered boxes; each box holds just a line number in the book.
>
> **How it maps:** the book is the dense entries array, which is why iteration follows insertion order. The card is the sparse indices array: it can have many empty boxes cheaply, because each box holds only a small line number rather than a whole entry.
>
> **Where it stops:** a receptionist would cross out a departed visitor and never reuse the line. CPython also leaves a hole in the entries when you delete, but marks the box on the card as "dummy" so searches keep probing, and compacts the book only when the dict is rebuilt.

Further details:

- **Sizes** are powers of two, minimum 8. A table holds at most two-thirds of its size in entries (CPython's `USABLE_FRACTION`), so an 8-slot dict holds 5 keys.
- **Growth**: when full, the new size is the smallest power of two that is at least three times the number of live keys. Without deletions this doubles the table: in CPython 3.14, a dict built key by key resizes on the 6th, 11th, 22nd and 43rd inserts. Deleting keys never shrinks it.
- **Probing** uses a perturbed sequence, not linear steps, described below.
- **Deletion** marks the index slot as a dummy (a tombstone) and the entry as empty. A rebuild compacts empty entries. In GIL-enabled builds a later insertion can reuse a dummy index slot; free-threaded builds avoid that reuse for lookup safety.

```formula reference
U = floor(2m / 3)
m_new = 2^⌈log_2(3u)⌉
where
U: the usable capacity: the most entries a table of m slots can hold before it must grow
m: the table size (number of index slots), a power of two
m_new: the size of the new table after growing
u: the number of live keys when the table grows
floor: round down to a whole number
log_2: logarithm to base 2, the power 2 must be raised to
⌈ ⌉: ceiling, round up to a whole number
^: "to the power of"
In words: a dict can fill two-thirds of its slots; when it is full it grows to the next power of two that is at least three times its live keys. An 8-slot dict holds 5 keys and grows to 16 slots on the 6th insert.
```

## The perturbed probe sequence

Linear probing in a power-of-two table would look only at the hash's low bits, and keys sharing those bits would form runs. CPython instead mixes the rest of the hash into the first few probes. It keeps a value called `perturb`, starting as the full hash (read as an unsigned 64-bit number), and shifts it right by 5 bits before each step:

```python
def probe_order(h, size, n):
    # size is a power of two
    mask = size - 1
    perturb = h & (2**64 - 1)
    i = h & mask
    out = [i]
    while len(out) < n:
        perturb >>= 5
        i = (5 * i + perturb + 1) & mask
        out.append(i)
    return out

probe_order(1234, 8, 4)  # [2, 1, 7, 4]
```

Here `& mask` keeps the low bits, which for a power-of-two size is the same as the remainder after dividing by the size. For a hash of 1,234 in an 8-slot table, the first slot is 2; `perturb` then shrinks to 38, 1 and 0, steering the next probes to 1, 7 and 4. Keys that share low bits but differ higher up therefore part company after a probe or two.

Once `perturb` reaches 0, the step is just `5*i + 1`, and in a power-of-two table that recurrence visits every slot before repeating, so a search always finds an empty slot eventually.

## Key takeaways
- Ordinary combined dictionaries use sparse indices over insertion-ordered entries.
- Perturbed probing feeds higher hash bits into early probes.
- Capacity, tombstone reuse and layouts are implementation and build details.

## Further reading
- [More compact dictionaries with faster iteration — Raymond Hettinger, python-dev](https://mail.python.org/pipermail/python-dev/2012-December/123028.html)
- [CPython 3.14 dictionary implementation](https://raw.githubusercontent.com/python/cpython/3.14/Objects/dictobject.c)
