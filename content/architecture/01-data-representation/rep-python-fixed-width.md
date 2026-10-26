---
id: rep-python-fixed-width
title: Modelling fixed-width integers in Python
level: basic
minutes: 3
summary: Python integers have no fixed-width arithmetic wrap.
sourceLesson: rep-integers
---

Python integers can grow, whereas a register or protocol field has a fixed width. Modelling that boundary requires an explicit choice about which bits to keep.

## Python: no overflow, but you can fake it

Python's `int` has arbitrary precision. Arithmetic has no fixed-width wraparound, so `2**100` is exact. Storage and implementation limits still apply; a computation can fail for lack of resources. Python models a negative number as if it had an infinite row of 1s to the left, which is why bitwise operations on negatives behave like two's complement.

To see the *n*-bit pattern, or to emulate a fixed-width type, mask it:

```python
# Select eight bits, then read their sign.
def to_u8(x):
    return x & 0xFF

def to_s8(x):
    # Discard bits outside the 8-bit field.
    x &= 0xFF
    # Upper-half patterns denote negatives.
    return x - 256 if x >= 128 else x

to_u8(-3)       # 253
bin(-3 & 0xFF)  # '0b11111101'
to_s8(100+100)  # -56
to_s8(0xB5)     # -75
```

NumPy, however, uses fixed-width types, so `np.int8(100) + np.int8(100)` wraps to −56 (under the usual NumPy error settings scalar arithmetic warns, while integer array arithmetic generally wraps without that warning).

### Choose a width at the boundary

The mask in these functions is an explicit eight-bit policy. It is appropriate when modelling an eight-bit register or decoding a protocol field whose interpretation is already known. It would hide a validation failure if the application instead required rejecting values outside the permitted range.

The signed helper first discards all but the low eight bits, then interprets their top bit as a sign. Values in the upper half are reduced by the full pattern count; values in the lower half are already non-negative. This separates two decisions that a language type often packages together: which bits to retain and how to interpret those bits.

Use Python's ordinary integer arithmetic for an exact intermediate result when useful, then explicitly choose whether the external format requires rejection, saturation or wraparound. The correct boundary policy depends on the device or protocol, rather than on Python's ability to calculate a larger integer.

## Key takeaways
- Python integers have no fixed-width arithmetic wrap.
- Masking selects the low bits before signed reinterpretation.

## Further reading
- [C working draft N3220](https://www.open-std.org/jtc1/sc22/wg14/www/docs/n3220.pdf)
- [GCC implementation-defined integers](https://gcc.gnu.org/onlinedocs/gcc/Integers-implementation.html)
