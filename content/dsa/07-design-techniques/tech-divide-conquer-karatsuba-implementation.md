---
id: tech-divide-conquer-karatsuba-implementation
title: Implementing Karatsuba and matrix splitting
level: intermediate
minutes: 3
sourceLesson: tech-divide-conquer
summary: Binary splits implement the same three-product algebra.
---

The previous unit derived Karatsuba: combine the high-half product, low-half product and one product of half-sums. Here we implement that algebra with binary splits and compare it with another three-dimensional product problem: square matrix multiplication.

The preceding algebra unit uses decimal blocks for readability. This implementation splits at powers of two, avoiding decimal string conversion and its input-size limit. Its recurrence counts bit operations on linearly sized additions/splits.

```python
def karatsuba(x, y):
    if (type(x) is not int
            or type(y) is not int):
        raise TypeError("integer operands")
    sign = -1 if (x < 0) != (y < 0) else 1
    def mul(x, y):
        if x < 16 or y < 16:
            return x * y
        m = max(x.bit_length(),
                y.bit_length()) // 2
        # Split at a binary block boundary.
        base = 1 << m
        a, b = divmod(x, base)
        c, d = divmod(y, base)
        # Keep both products for
        # reconstruction.
        ac, bd = mul(a, c), mul(b, d)
        # Subtract known products from the
        # half-sums.
        mid = mul(a + b, c + d) - ac - bd
        return ((ac << (2*m))
                + (mid << m) + bd)
    return sign * mul(abs(x), abs(y))
```

In practice the additions and subtractions make Karatsuba slower than schoolbook for small numbers. In CPython 3.14, ordinary multiplication uses Karatsuba only when both operands exceed 70 internal digits; the squaring cutoff is 140. Internal digits have 15 or 30 bits depending on the build (`sys.int_info.bits_per_digit`). Libraries such as GMP go further with Toom–Cook and FFT-based methods for very large numbers. The same "fewer multiplications" idea gives **Strassen's** matrix multiplication: 7 half-size products instead of 8.

```formula
T(n) = 7T(n / 2) + O(n^2)
c = log_2(7) ≈ 2.807 > 2
T(n) = Θ(n^{log_2(7)})
where
T(n): the number of arithmetic operations to multiply two n × n matrices
n: the number of rows (and columns) of each square matrix
O(n^2): the work of the 18 additions and subtractions of (n / 2) × (n / 2) blocks, each touching n^2 / 4 entries
c: the critical exponent, log_2 of the number of subproblems
log_2(7): the base-2 logarithm of 7, about 2.80735
≈: approximately equal to
Θ: Big-Theta, grows at exactly this rate up to constant factors
In words: seven half-size products put Strassen in the "leaves dominate" case, about n^2.807 work instead of the n^3 of the schoolbook method.
```

## Key takeaways
- Binary splits implement the same three-product algebra.
- Practical multiplication selects algorithms by operand size; matrix splitting has its own arithmetic model.

## Further reading
- [Pinned CPython 3.14 integer implementation](https://raw.githubusercontent.com/python/cpython/v3.14.0/Objects/longobject.c)
- [GMP multiplication algorithms](https://gmplib.org/manual/Multiplication-Algorithms)
