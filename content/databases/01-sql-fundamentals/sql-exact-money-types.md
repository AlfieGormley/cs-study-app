---
id: sql-exact-money-types
title: Store money without binary rounding errors
level: advanced
minutes: 3
sourceLesson: sql-schema-ddl
summary: Binary floating point cannot represent most decimal fractions exactly.
---

The examples continue the shop database introduced in the first unit. The original products are Kettle £30, Toaster £25, Lamp £40, Rug £90 and Mug £8. 

## Choosing types

### Money: never floating point

```sql
-- SQLite: decimal literals become binary
-- floats, so the sum misses 0.3.
SELECT 0.1 + 0.2 = 0.3;  -- 0 (false)
SELECT 0.1 + 0.2 - 0.3;
-- about 5.55e-17, not 0
```

How SQLite displays `0.1 + 0.2` depends on its version: 3.53.0 and later show `0.30000000000000004` by default, while earlier releases round the display to 15 significant digits and show `0.3`, hiding the error. The comparison and the subtraction expose it in every version.

In PostgreSQL, those uncast decimal literals are exact `numeric` values, so the equality above is TRUE. To demonstrate binary floating point there, cast the operands explicitly:

```sql
-- PostgreSQL: force binary floating point.
SELECT 0.1::double precision
     + 0.2::double precision
     = 0.3::double precision;
-- false: the rounded sum differs
```

Binary floating point can't represent most decimal fractions exactly. The reason is in how a floating-point number is built: it is a whole number scaled by a power of two, so it can only hold fractions such as halves, quarters and eighths exactly. A tenth is not one of those.

```formula reference
x = m 2^e
0.1 = 1 / 10 = 1 / (2 × 5)
where
x: a finite value representable by this binary floating-point form; infinities and NaN are separate special values
m: an integer significand; its magnitude needs at most 53 bits for a binary64 value, up to about 9 × 10^15
e: an integer exponent within the format's range; negative values divide rather than multiply (2^−3 = 1/8)
2^e: e copies of two multiplied together; a negative e means dividing by two that many times
In words: a float can only store fractions whose denominator (the number below the line) is an integer power of two, such as 1/2, 3/8 or 5/1024. A tenth has a factor of 5 below the line, so no binary float equals 0.1 exactly, and the nearest storable value is used instead.
```

The stored 0.1 and 0.2 are each a tiny bit off, and their sum lands next to, not on, the stored 0.3. Those small errors build up in sums. Store money either as:

- **integer minor units** (pence): `price_pence INTEGER`, where £10.99 is 1099. This is exact, fast and portable, and it's how payment processors such as Stripe represent amounts.
- **exact decimals**: PostgreSQL `numeric(10,2)`. This is exact, and `SUM` of it stays exact.

Converting between pounds and pence is a single multiplication by 100, done once, when the application reads a price typed by a person or displays one: £10.99 is stored as 1099.

Parse typed amounts as exact decimals or split the decimal digits into whole pence before storing them. Multiplying an already rounded binary float by 100 can carry a rounding error into the conversion. A fixed-scale numeric column also rounds inputs with extra decimal places, so choose and apply a rounding rule.

Three £10.99 items then sum to 1099 + 1099 + 1099 = 3297 pence, exactly £32.97, with no rounding at any step.

> [!analogy] Real-world analogy: a ruler marked in halves, quarters and eighths
> An imperial ruler is marked in halves, quarters, eighths and sixteenths of an inch. You can measure 3/8 inch exactly, but a tenth of an inch falls between two marks, so you read the nearest one.
>
> **How it maps:** Binary floating point is that ruler: it stores fractions whose denominator is a power of two exactly, and rounds everything else, such as 0.1, to the nearest mark. Integer pence is a ruler marked in whole pence, which is exactly the unit money is counted in.
>
> **Where it stops:** A double's marks are extraordinarily fine, about 16 significant digits, and their spacing grows with the size of the number. The error in one price is tiny; the trouble is that exact equality fails and small errors accumulate across many sums.

Avoid `real`, `float` and `double precision` for money. Also avoid PostgreSQL's `money` type, whose formatting depends on a server locale setting.

## Key takeaways
- Binary floating point cannot represent most decimal fractions exactly.
- Store money in integer minor units or exact numeric values.
- PostgreSQL uncast decimal literals are numeric, unlike SQLite floating-point literals.

## Further reading
- [Data definition — PostgreSQL documentation](https://www.postgresql.org/docs/current/ddl.html)
- [Don't do this — PostgreSQL wiki](https://wiki.postgresql.org/wiki/Don%27t_Do_This)
