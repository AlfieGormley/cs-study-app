---
id: hash-function-fibonacci
title: Multiplication and Fibonacci hashing
level: intermediate
minutes: 4
sourceLesson: hash-functions
summary: Multiplication hashing separates hash mixing from the choice of table size.
---

Multiplication hashing separates hash mixing from the choice of table size. The example below uses a fixed 32-bit calculation; it improves one patterned input without proving that every input distributes well.

## The multiplication method

Primes are awkward: the table cannot double neatly, and a variable divisor may require division; compilers can optimise division by known constants. The **multiplication method** lets m be a power of two. Multiply the key by a constant, keep only the part after the decimal point, and scale that up to the table size:

```formula
h(k) = floor(m frac(k A))
A = (√(5) − 1) / 2 ≈ 0.618
A_round = 0.618034
h(8) = floor(16 × frac(8 × A_round))
h(8) = floor(16 × frac(4.944272))
h(8) = floor(16 × 0.944272)
h(8) ≈ floor(15.108) = 15
where
h(k): the bucket index for key k, from 0 to m − 1
k: the integer key, here 8
m: the number of buckets, here 16 (any size works, including powers of two)
A: a constant between 0 and 1; Knuth suggests (√5 − 1)/2 ≈ 0.618, the fractional part of the golden ratio
A_round: the rounded constant used in the illustrative decimal calculation, dimensionless
frac: "fractional part", what is left after removing the whole-number part; frac(4.944) = 0.944
floor: round down to the nearest whole number; floor(15.108) = 15
√: square root; √5 ≈ 2.236
≈: approximately equal to (the value is rounded)
In words: multiply the key by about 0.618, throw away the whole-number part, and scale the leftover fraction (between 0 and 1) up to a bucket number; key 8 lands in bucket 15 of 16.
```

Because every key's fraction is scrambled by the multiplication, the size of the table no longer has to be prime. The method still assumes keys are integers; other keys (strings, tuples) are first turned into integers.

In integer arithmetic this becomes **Fibonacci hashing**: multiply by a large odd constant, keep the low 32 bits of the product, and use the *top* few of those bits as the bucket index (4 bits for a 16-bucket table):

```formula
h(k) = floor(((kA) mod 2^32)
             / 2^{32 − p})
h(8) = floor(4055616968 / 2^28)
h(8) ≈ floor(15.1) = 15
where
h(k): the bucket index for key k, from 0 to 2^p − 1
k: the integer key, here 8
A: the constant 2,654,435,769, which is 2^32 divided by the golden ratio (about 1.618), rounded to an odd number
mod: "modulo", the remainder after division; mod 2^32 keeps the low 32 bits, as a 32-bit unsigned multiply does automatically
p: the number of index bits, so the table has 2^p buckets; here p = 4, giving 16 buckets
floor: round down to a whole number; dividing by 2^(32 − p) and rounding down keeps the top p bits
^: "to the power of"; 2^32 = 4,294,967,296
In words: multiply the key by a fixed odd constant, keep 32 bits of the result, and use its highest p bits as the bucket; key 8 gives bucket 15 of 16, matching the decimal version above.
```

The same calculation in Python, where `%` is mod and `>>` shifts bits right (dividing by a power of two and rounding down):

```python
def fib_hash(k, p):
    if not 0 <= p <= 32:
        raise ValueError("p out of range")
    # 2**32 / golden ratio
    A = 2654435769
    # Keep 32 bits, then take high index
    # bits.
    return ((k * A) % 2**32) >> (32 - p)
```

For a table of 2⁴ = 16 buckets, the aligned keys eight, sixteen, twenty-four, thirty-two, forty, forty-eight, fifty-six and sixty-four map to 15, 14, 13, 12, 11, 10, 9, 8: all different. This fixed 32-bit mapping improves this example; it is not a universal collision or avalanche guarantee. Inputs differing by 2³² (about 4.3 billion) collide because the product is reduced modulo 2³².

## Key takeaways
- Multiplication uses a fractional product to choose a bucket.
- The fixed-width version keeps a word-sized product then extracts high index bits.
- The worked alignment example does not guarantee good distribution for every key set.

## Further reading
- [Hash function — Wikipedia](https://en.wikipedia.org/wiki/Hash_function)
