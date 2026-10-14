---
id: hash-resize-cpython-layout
title: CPython dictionaries: layout and probing
level: intermediate
minutes: 5
sourceLesson: hash-resizing
summary: These are CPython 3.14 implementation details for an ordinary combined table with general keys.
---

These are CPython 3.14 implementation details for an ordinary combined table with general keys. The language promises dictionary behaviour and insertion order, while other Python implementations can choose different layouts.

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

Further details:

- **Sizes** are powers of two, minimum 8, and a table holds at most about two-thirds of its size in entries (the formula below).
- **Growth**: when full, the new size is the smallest power of two that is at least 3 × the number of live keys. Without deletions this doubles the table: in CPython 3.14, a dict built key by key resizes on the 6th, 11th, 22nd and 43rd inserts.
- **Probing** uses a perturbed sequence, not linear steps. CPython first interprets a signed hash as an unsigned machine word for perturbation; otherwise a negative hash would not shift towards zero. Starting from `i = hash & mask`, each step is `perturb >>= 5` then `i = (5*i + perturb + 1) & mask`. The shifting `perturb` feeds the high bits of the hash into the sequence, so keys that share low bits soon diverge; once `perturb` reaches 0, `5*i + 1` alone visits every slot.
- **Deletion** marks the index slot as a dummy (a tombstone) and the entry as empty. A rebuild compacts empty entries. In GIL-enabled builds a later insertion can reuse a dummy index slot; free-threaded builds avoid that reuse for lookup safety.

The size rules, written out (CPython's `USABLE_FRACTION` and growth calculation):

```formula
U = floor(2 × m / 3)
m_new = 2^⌈log_2(3 u)⌉
U = floor(2 × 8 / 3) = floor(5.33) = 5
m_new = 2^⌈log_2(15)⌉ = 2^⌈3.91⌉
m_new = 2^4 = 16
where
U: the usable capacity: the most entries a table of size m can hold before it must grow
m: the table size (number of index slots), a power of two; here 8
m_new: the size of the new table after growing
u: the number of live keys when the table grows; here 5
floor: round down to a whole number
log_2: logarithm to base 2, the power 2 must be raised to; log_2(16) = 4, log_2(15) ≈ 3.91
⌈ ⌉: ceiling, round up to a whole number; ⌈3.91⌉ = 4
^: "to the power of"; 2^4 = 16
In words: a dict can fill two-thirds of its slots; when it is full it grows to the next power of two that is at least three times its live keys, so an 8-slot dict holds 5 keys and grows to 16 slots on the 6th insert.
```

And the probe sequence. Here `&` with `mask` (the table size minus 1) is the same as taking the remainder by the table size, and `perturb >>= 5` divides `perturb` by 32, rounding down:

```formula
i_0 = H mod m
q_new = floor(q / 32)
i_next = (5 × i + q_new + 1) mod m
where
i_0: the first slot tried
i: the slot just tried
i_next: the next slot to try
H: the key's full hash interpreted as a nonnegative unsigned machine word
q: perturb, initially that unsigned word, which shrinks each step
q_new: perturb after shifting right by 5 bits
m: the table size, a power of two
mod: "modulo", the remainder after division
floor: round down to a whole number
In words: each step multiplies the current slot by 5, adds 1 plus the remaining high bits of the hash, and wraps round the table; the high bits shrink away after a few steps, leaving a sequence that visits every slot.
```

For a full hash of 1,234 and eight slots, the first four slot choices are two, one, seven and four. The perturb values after successive shifts are thirty-eight, one and zero.

```formula
i_0 = 1234 mod 8 = 2
i_1 = (5 × 2 + 38 + 1) mod 8 = 1
i_2 = (5 × 1 + 1 + 1) mod 8 = 7
i_3 = (5 × 7 + 0 + 1) mod 8 = 4
where
i_0: first probe slot, counting from zero
i_1: second probe slot
i_2: third probe slot
i_3: fourth probe slot
mod: nonnegative remainder after whole-number division
In words: Shrinking perturb adds high-hash information to early probes; after it reaches zero, the fixed recurrence continues.
```

## Key takeaways
- Ordinary combined dictionaries use sparse indices over insertion-ordered entries.
- Perturbed probing feeds higher hash bits into early probes.
- Capacity, tombstone reuse and layouts are implementation and build details.

## Further reading
- [More compact dictionaries with faster iteration — Raymond Hettinger, python-dev](https://mail.python.org/pipermail/python-dev/2012-December/123028.html)
- [CPython 3.14 dictionary implementation](https://raw.githubusercontent.com/python/cpython/3.14/Objects/dictobject.c)
