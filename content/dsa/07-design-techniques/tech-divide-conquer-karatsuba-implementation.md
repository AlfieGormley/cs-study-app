---
id: tech-divide-conquer-karatsuba-implementation
title: Implementing Karatsuba and matrix splitting
level: intermediate
minutes: 3
sourceLesson: tech-divide-conquer
summary: Binary splits implement the same three-product algebra.
---

The previous unit derived Karatsuba: combine the high-half product, low-half product and one product of half-sums. Here we implement that algebra with binary splits, then see the same "fewer multiplications" idea in square matrix multiplication.

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

In practice the additions and subtractions make Karatsuba slower than schoolbook for small numbers. In CPython 3.14, ordinary multiplication uses Karatsuba only when both operands exceed 70 internal digits; the squaring cutoff is 140. Internal digits have 15 or 30 bits depending on the build (`sys.int_info.bits_per_digit`). Libraries such as GMP go further with Toom–Cook and FFT-based methods for very large numbers. The same "fewer multiplications" idea gives **Strassen's** matrix multiplication. Splitting two square matrices into quarter blocks naively needs 8 half-size block products; Strassen (1969) needs only 7, at the price of 18 block additions and subtractions. The additions cost work proportional to the number of entries, which is quadratic in the matrix side n, while the seven recursive products put the recurrence in the "leaves dominate" case. The result grows like n to the power log₂7, about n to the power 2.807, instead of the n³ of the schoolbook method. As with Karatsuba, practical libraries switch to it only above a size cutoff, if at all.

## Key takeaways
- Binary splits implement the same three-product algebra.
- Practical multiplication selects algorithms by operand size; matrix splitting has its own arithmetic model.

## Further reading
- [Pinned CPython 3.14 integer implementation](https://raw.githubusercontent.com/python/cpython/v3.14.0/Objects/longobject.c)
- [GMP multiplication algorithms](https://gmplib.org/manual/Multiplication-Algorithms)
