---
id: lin-array-index-address
title: Direct indexing with array address arithmetic
level: basic
minutes: 3
sourceLesson: lin-arrays
summary: Address arithmetic gives direct access to a fixed-width slot.
---

An **array** is the simplest data structure there is: a fixed number of same-sized slots laid out one after another in memory. Almost every other structure in this course is either built on arrays or defined by how it differs from one.

Two properties make arrays special:

- **Contiguous layout.** Element at the next index sits immediately after its predecessor. There are no gaps and no pointers between them.
- **Uniform element size.** Every slot is the same number of bytes, so the machine can compute where any element lives.

Everything good about arrays (instant indexing, cache-friendliness) and everything bad (expensive inserts, fixed size) follows from those two facts.

## Indexing is arithmetic

Memory is a long row of numbered bytes; the number of a byte is its **memory address**. To read element `i`, the machine needs that element's address. Because the slots are contiguous and all the same size, it can work the address out directly from where the array starts:

```formula
address(i) = base + i × size
where
address(i): the memory address of the first byte of element i
i: the index of the element you want, counting from 0
base: the memory address where the array starts (the address of element 0)
size: how many bytes one element takes, e.g. 4 for a 32-bit integer, 8 for a 64-bit float or a pointer
In words: skip over i whole elements from the start of the array; the element you want begins right there.
```

For the array drawn below, substitute its 4-byte slots and base address:

```formula
address(3) = 1000 + 3 × 4
address(3) = 1012
where
address: the function giving an element’s starting byte address
3: the zero-based element index in this example
In words: Element 3 starts twelve bytes after the base address.
```

 The formula only works because every slot is the same size and there are no gaps; a structure without those two properties (a linked list, for example) has no such shortcut.

That is one multiply and one add, whatever the array's length. This is why indexing is **O(1)**, or **constant time**: the cost does not grow as the array gets longer. The CPU does not walk to element `i`, it calculates where it is.

```
int32: 4-byte slots, start address 1000

index:    0     1     2     3     4
        +-----+-----+-----+-----+-----+
        |  7  | 12  |  3  | 40  |  9  |
        +-----+-----+-----+-----+-----+
addr:   1000  1004  1008  1012  1016
```

This also explains why most languages start indexing at **0**: the index is an *offset* from the start. Element 0 is zero elements past `base`.

> [!note] O(1) access, O(n) search
> For an array of n elements: indexing by position is O(1). Finding a *value* in an unsorted array is still O(n) (**linear time**: the work grows in proportion to n), because you must look at each slot. If the array is sorted, binary search finds a value in O(log n), where log n means log₂ n, the number of times you can halve n before reaching 1 (about 20 for a million elements).

## Key takeaways
- Address arithmetic gives direct access to a fixed-width slot.
- Position lookup and searching for an unsorted value are different operations.

## Further reading
- [Array (data structure) — Wikipedia](https://en.wikipedia.org/wiki/Array_(data_structure))
