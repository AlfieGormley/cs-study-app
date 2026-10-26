---
id: logp-invariants-power
title: Repeated squaring and a conserved product
level: intermediate
minutes: 3
sourceLesson: logp-invariants
summary: The accumulator times the current base raised to the remaining exponent stays equal to the target.
---

## Fast exponentiation

Computing x to the power n (n copies of x multiplied together) with n multiplications is slow for large n. For integer n at least 0, repeated squaring uses O(log(n plus 1)) multiplications: a number that grows with the logarithm of n, roughly the number of binary digits of n. This is not a bit-operation bound: large-integer multiplication costs depend on operand size. The proof assumes exact real-number or integer multiplication. A zeroth power is defined as one, including a zero base, matching this function and Python's integer power convention:

```python
def power(x, n):
    if not isinstance(n, int) or n < 0:
        raise ValueError("n must be >= 0")
    result, base, e = 1, x, n
    # I: result * base**e == x**n
    while e > 0:
        if e % 2 == 1:
            # Absorb an odd remaining
            # factor.
            result *= base
        # Squaring pairs remaining factors.
        base *= base
        # Remove the processed binary digit.
        e //= 2
    return result
```

The invariant is not obvious from the code; it is what makes the code make sense. Written as maths, with what each branch does to it:

```formula essential
result × base^e = x^n
result × (base^2)^{e/2} = result × base^e
result × base × (base^2)^{(e−1)/2}
  = result × base^e
where
x, n: the inputs; the function computes x^n
result: the accumulated part of the answer, starting at 1
base: the current base, starting at x and squared every iteration
e: the remaining exponent, starting at n and halved (rounding down) every iteration
base^e: e copies of base multiplied together
In words: the first line is the invariant. The second line is the even case (base squared, e halved); the third and fourth are the odd case (result absorbs one base, then base squared and e becomes (e − 1)/2). Either way the product is unchanged.
```

- **Init**: result equals 1, base equals x and e equals n, so the product is 1 times x to the power n = x to the power n. ✓
- **Maintain**, if e is even: the second line of the block shows the product is unchanged. ✓
- **Maintain**, if e is odd: the third and fourth lines show the same. ✓
- **Terminate**: e equals 0, so result times base⁰ equals result equals x to the power n. ✓
- **Variant**: e, which strictly decreases while positive and remains nonnegative.

The odd and even branches handle the same conserved product in different ways:

After an odd exponent transfers one factor to the accumulator, the remaining factors can be paired. Squaring the base and halving that even remainder preserves the represented result.

Modular variants of repeated squaring are used in modular exponentiation. Real cryptographic implementations also need side-channel protections; this branching teaching code is not a production RSA implementation.

> [!note] Evidence gap
> A previous fixed RSA runtime claim is omitted because no reproducible implementation, exponent, hardware or benchmark was supplied.


## Key takeaways
- The accumulator times the current base raised to the remaining exponent stays equal to the target.
- Halving the remaining exponent proves termination; logarithmic multiplication count is not a bit-cost bound.

## Further reading
- [MIT Mathematics for Computer Science](https://ocw.mit.edu/courses/6-042j-mathematics-for-computer-science-spring-2015/mit6_042js15_textbook.pdf)
- [Loop variant — Wikipedia](https://en.wikipedia.org/wiki/Loop_variant)
