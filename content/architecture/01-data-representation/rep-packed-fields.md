---
id: rep-packed-fields
title: Combining flags and extracting fields
level: intermediate
minutes: 3
summary: Not every API flag constant denotes a single independent bit.
sourceLesson: rep-bitwise
---

A packed word can hold independent switches, a choice between modes, or several numeric fields. Identify which kind of field you have before choosing a mask.

### Flags

Packing booleans into one integer is the most common use. POSIX `open()` takes flags OR-ed together:

```c
/* Create if absent; append each write. */
int fd = open("log.txt",
    O_WRONLY | O_CREAT | O_APPEND, 0644);
```

Many open options are independent bit flags, but **not every O_ constant is one bit**. Access modes are alternatives selected with O_ACCMODE; O_RDONLY is commonly zero. Test a mode with `(flags & O_ACCMODE) == O_RDONLY`, not a simple AND with O_RDONLY. Creation mode 0644 is also filtered by the process umask when a file is created. The same pattern appears in Python's `re.IGNORECASE | re.MULTILINE` and the `enum.Flag` class.

### Extracting fields

Many formats pack several small numbers into one word. To pull one out, **shift it down, then mask it**:

```python
# Shift each colour byte into the low bits.
colour = 0x1E90FF   # RRGGBB
r = (colour >> 16) & 0xFF   # 0x1E = 30
g = (colour >> 8)  & 0xFF   # 0x90 = 144
b =  colour        & 0xFF   # 0xFF = 255
```

To pack, shift each field up and OR them together: `(r << 16) | (g << 8) | b`. CPU instruction encodings, IPv4 headers, Unix file modes and UUIDs are all decoded this way.

A mask of the low bits is one less than a power of two, because subtracting 1 from `1000...0` turns it into `0111...1`:

```formula reference
M = 2^n − 1
where
M: a mask whose low n bits are 1 and every bit above them 0; in Python it is written (1 << n) - 1
n: how many low bits the mask covers, a non-negative count
2^n: n copies of 2 multiplied together; written 1 << n in code
In words: a mask with consecutive low bits set keeps a field after it has been shifted down; five set low bits give the mask 31.
```

In C, the operand type, promotions and shift-count limit matter; use an appropriately wide unsigned mask and handle *n* equal to the width separately.

## Key takeaways
- Not every API flag constant denotes a single independent bit.
- Shift a field down, then mask away unrelated positions.

## Further reading
- [C working draft N3220](https://www.open-std.org/jtc1/sc22/wg14/www/docs/n3220.pdf)
- [Python bitwise integer operations](https://docs.python.org/3/library/stdtypes.html#bitwise-operations-on-integer-types)
