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
-- SQLite: binary literals expose rounding.
-- SQLite: literals use binary floats.
SELECT 0.1 + 0.2 = 0.3;  -- 0 (false)
SELECT 0.1 + 0.2;
-- 0.30000000000000004
```

In PostgreSQL, those uncast decimal literals are exact `numeric` values, so the equality above is TRUE. To demonstrate binary floating point there, cast the operands explicitly:

```sql
-- PostgreSQL: force binary floating point.
-- PostgreSQL: force binary double values.
SELECT 0.1::double precision
     + 0.2::double precision
     = 0.3::double precision;
-- false: the rounded sum differs
```

Binary floating point can't represent most decimal fractions exactly. The reason is in how a floating-point number is built: it is a whole number scaled by an integer power of two.

```formula
x = m 2^e
0.1 = 1 / 10 = 1 / (2 × 5)
where
x: a finite value representable by this binary floating-point form; infinities and NaN are separate special values
m: an integer significand; its magnitude needs at most 53 bits for a binary64 value, up to about 9 × 10^15
e: an integer exponent within the format's range; negative values divide rather than multiply (2^−3 = 1/8)
2^e: e copies of two multiplied together; a negative e means dividing by two that many times
In words: a float can only store fractions whose denominator (the number below the line) is an integer power of two, such as 1/2, 3/8 or 5/1024. A tenth has a factor of 5 below the line, so no choice of m and e gives exactly 0.1, and the nearest storable value is used instead.
```

The stored 0.1 and 0.2 are each a tiny bit off, and their sum lands next to, not on, the stored 0.3. Those small errors build up in sums. Store money either as:

- **integer minor units** (pence): `price_pence INTEGER`, where £10.99 is 1099. This is exact, fast and portable, and it's how payment processors such as Stripe represent amounts.
- **exact decimals**: PostgreSQL `numeric(10,2)`. This is exact, and `SUM` of it stays exact.

Converting between pounds and pence is a single multiplication, done once, when the application reads a price typed by a person or displays one:

```formula
P = 100L
P = 100 × 10.99 = 1099
where
P: the amount in pence, a whole number, which is what is stored in the column
L: the amount in pounds (£), as a person reads it
100: the number of pence in one pound
In words: store the amount as a count of the smallest unit, so every sum and comparison works on exact whole numbers.
```

Parse typed amounts as exact decimals or split the decimal digits into whole pence before storing them. Multiplying an already rounded binary float by 100 can carry a rounding error into the conversion. A fixed-scale numeric column also rounds inputs with extra decimal places, so choose and apply a rounding rule.

Three £10.99 items then sum to 1099 + 1099 + 1099 = 3297 pence, exactly £32.97, with no rounding at any step.

Avoid `real`, `float` and `double precision` for money. Also avoid PostgreSQL's `money` type, whose formatting depends on a server locale setting.

## Key takeaways
- Binary floating point cannot represent most decimal fractions exactly.
- Store money in integer minor units or exact numeric values.
- PostgreSQL uncast decimal literals are numeric, unlike SQLite floating-point literals.

## Further reading
- [Data definition — PostgreSQL documentation](https://www.postgresql.org/docs/current/ddl.html)
- [Don't do this — PostgreSQL wiki](https://wiki.postgresql.org/wiki/Don%27t_Do_This)
