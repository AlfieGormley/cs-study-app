---
id: logp-invariants-euclid
title: Euclid and a decreasing remainder
level: intermediate
minutes: 3
sourceLesson: logp-invariants
summary: Replacing the pair by divisor and remainder preserves common divisors.
---

## Euclid's algorithm

Use non-negative integer arguments. In the invariant comment, `a0` and `b0` denote the original inputs; they are mathematical labels, not extra runtime variables. The function definition itself prints nothing.

```python
def gcd(a, b):
    # integers a, b >= 0; gcd(0, 0) = 0
    # I: gcd(a, b) == gcd(a0, b0)
    while b != 0:
        # Preserve divisors; shrink
        # remainder.
        a, b = b, a % b
    return a
```

The key fact behind the maintenance step:

```formula essential
gcd(a, b) = gcd(b, a mod b)
a = q × b + (a mod b)
0 ≤ a mod b < b
gcd(a, 0) = a
where
a, b: non-negative integers, the current values; the first three lines require b to be positive, while the final line covers b equal to zero; gcd(0, 0) is defined as zero
a_0, b_0: the original inputs (written a0, b0 in the code)
gcd(a, b): the greatest common divisor: the largest whole number dividing both a and b
mod: the remainder after division (Python `%`): a mod b is what is left after taking out as many b's as fit
q: the whole-number quotient, how many times b fits into a
≤: at most
<: less than
In words: replacing (a, b) with (b, a mod b) keeps the gcd the same, the remainder is always smaller than b, and once b reaches 0 the answer is a.
```

- **Init**: trivially, with a0, b0 the inputs. ✓
- **Maintain**: any common divisor of a and b divides a − qb equals a mod b, and any common divisor of b and a mod b divides a equals qb + (a mod b). Same divisors, same greatest one. ✓
- **Terminate**: b equals 0 and gcd(a, 0) equals a. ✓
- **Variant**: b, since 0 is at most a mod b is less than b.

```
a    b
252  105
105  42
42   21
21   0     -> return 21
```


For the displayed trace, the first division leaves forty-two after removing two copies of one hundred and five from two hundred and fifty-two. The next division leaves twenty-one; the next divides exactly and leaves zero. This explains why the first coordinate at exit is the divisor being returned.

The all-zero input uses a separate convention. Every positive integer divides zero, so there is no largest positive common divisor of zero and zero under the literal “largest divisor” definition. Returning zero agrees with Python’s gcd operation and lets this implementation handle that boundary explicitly.

## Key takeaways
- Replacing the pair by divisor and remainder preserves common divisors.
- The second non-negative argument strictly decreases until the result is reached.

## Further reading
- [MIT Mathematics for Computer Science](https://ocw.mit.edu/courses/6-042j-mathematics-for-computer-science-spring-2015/mit6_042js15_textbook.pdf)
- [Nearly all binary searches and mergesorts are broken — Google Research blog](https://research.google/blog/extra-extra-read-all-about-it-nearly-all-binary-searches-and-mergesorts-are-broken/)
