---
id: tech-divide-conquer-karatsuba
title: Karatsuba and fewer products
level: intermediate
minutes: 5
sourceLesson: tech-divide-conquer
summary: Three recursive half-products replace the four products of schoolbook splitting.
---

## Karatsuba multiplication

Schoolbook multiplication of two n-digit numbers multiplies every digit by every other digit: O(n²). In 1960 Anatoly Karatsuba found a faster way, published with Ofman in 1962.

Split each number into a high half and a low half around a power of ten:

```formula
x = a 10^m + b
y = c 10^m + d
xy = ac × 10^{2m}
      + (ad + bc) × 10^m
      + bd
where
x: the first number to multiply, with n digits
y: the second number to multiply, with n digits
m: the split point, about half the number of digits (n / 2)
10^m: 10 raised to the power m, a 1 followed by m zeros
10^{2 × m}: 10 raised to the power 2 × m
a: the high half of x (its leading digits)
b: the low half of x (its last m digits)
c: the high half of y
d: the low half of y
In words: each number is "high half shifted left by m digits, plus low half", so their product is three pieces: high × high shifted by 2m digits, the two cross products shifted by m digits, and low × low.
```

That looks like four half-size multiplications (a × c, a × d, b × c and b × d), which gives no gain:

```formula
T(n) = 4T(n / 2) + O(n)
c_crit = log_2(4) = 2 > 1
T(n) = Θ(n^2)
where
T(n): the number of digit operations to multiply two n-digit numbers
n: the number of digits in each number
O(n): linear work for the additions and shifts
c_crit: the critical exponent of the master theorem, log_2 of the number of subproblems; it is compared with 1, the exponent of the linear O(n) work
log_2(4): the base-2 logarithm of 4, which is 2 because 2^2 = 4
Θ: Big-Theta, grows at exactly this rate up to constant factors
n^2: n squared, the cost of schoolbook multiplication
In words: four half-size products are exactly as expensive as multiplying every digit by every digit.
```

The trick is that the middle term can be had with **one** extra multiplication:

```formula
ad + bc
  = (a + b)(c + d) − ac − bd
where
a: the high half of x
b: the low half of x
c: the high half of y
d: the low half of y
In words: multiply the two half-sums together once, then subtract the high and low products you already computed; what is left is exactly the two cross terms.
```

So three multiplications suffice:

```formula
T(n) = 3T(n / 2) + O(n)
c_crit = log_2(3) ≈ 1.585 > 1
T(n) = Θ(n^{log_2(3)})
where
T(n): the number of digit operations to multiply two n-digit numbers
n: the number of digits in each number
O(n): linear work for the additions, subtractions and shifts
c_crit: the critical exponent, log_2 of the number of subproblems; it is compared with 1, the exponent of the linear O(n) work
log_2(3): the base-2 logarithm of 3, about 1.585: the power you raise 2 to in order to get 3
≈: approximately equal to
Θ: Big-Theta, grows at exactly this rate up to constant factors
In words: three half-size products put the algorithm in the "leaves dominate" case, with about n^1.585 work instead of n^2.
```

An exponent-only scale expression for 1000 digits is about 57,000, compared with one million for a square. These are growth-model expressions, not exact digit-product counts: rounding, base cases and half-sum carries matter.

```formula
W_k = n^{log_2(3)} ≈ 56,871
W_s = n^2 = 1,000,000
where
n: the number of digits, 1000 in these substitutions
W_k: the Karatsuba growth expression, not an exact operation count
W_s: the schoolbook quadratic growth expression
log_2: the base-two logarithm
≈: approximately equal to
In words: The smaller exponent illustrates the growth advantage without predicting measured instruction counts.
```

A worked example on 1234 × 5678:

```formula
m = 2: a = 12, b = 34, c = 56, d = 78
ac = 12 × 56 = 672
bd = 34 × 78 = 2652
(a + b)(c + d) = 46 × 134 = 6164
p_mid = 6164 − 672 − 2652 = 2840
xy = 672 × 10^4 + 2840 × 10^2 + 2652
xy = 6,720,000 + 284,000 + 2,652
xy = 7,006,652
where
m: the split point in digits; 2 for 4-digit numbers
a: the high half of x, here 12
b: the low half of x, here 34
c: the high half of y, here 56
d: the low half of y, here 78
p_mid: the middle coefficient, a × d + b × c, found from one multiplication and two subtractions
x: the first number, 1234
y: the second number, 5678
In words: three two-digit multiplications (672, 2652 and 6164) and some subtractions and shifts give 1234 × 5678 = 7,006,652.
```

## Key takeaways
- Three recursive half-products replace the four products of schoolbook splitting.
- Arithmetic-operation counts, bit costs and real implementation cutoffs are different claims.

## Further reading
- [Karatsuba algorithm](https://en.wikipedia.org/wiki/Karatsuba_algorithm)
- [GMP multiplication algorithms](https://gmplib.org/manual/Multiplication-Algorithms)
