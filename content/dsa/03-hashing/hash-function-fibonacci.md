---
id: hash-function-fibonacci
title: Multiplication and Fibonacci hashing
level: intermediate
minutes: 4
sourceLesson: hash-functions
summary: Multiplying by a golden-ratio constant and keeping the high bits lets a power-of-two table spread patterned keys.
---

Prime table sizes fix the low-bit problem but are awkward: the table cannot double neatly, and reducing by a variable prime needs a division. Multiplication hashing lets the table size stay a power of two by mixing the key's bits *before* choosing a bucket.

## The multiplication method

Multiply the key by a constant between 0 and 1, keep only the part after the decimal point, and scale that fraction up to the table size. Knuth suggests the constant 0.618…, the fractional part of the golden ratio. For key 8 and 16 buckets: 8 × 0.618034 ≈ 4.944, the fractional part is 0.944, and 16 × 0.944 ≈ 15.1, so the key goes to bucket 15.

The multiplication scrambles every key's fraction, so neighbouring or aligned keys end up far apart and the table size no longer has to be prime. The method assumes integer keys; strings and tuples are first turned into integers.

In integer arithmetic this becomes **Fibonacci hashing**: multiply by a large odd constant, let the product overflow to 32 bits, and use the *top* p bits of the result as the bucket index (4 bits for a 16-bucket table). The top bits are the ones every bit of the key has influenced, which is exactly what the low-bit remainder lacked.

```formula reference
h(k) = floor(((kA) mod 2^32) / 2^(32 − p))
where
h(k): the bucket index for key k, from 0 to 2^p − 1
k: the non-negative integer key
A: the constant 2,654,435,769, which is 2^32 divided by the golden ratio (about 1.618), rounded to an odd number
p: the number of index bits, so the table has 2^p buckets
mod: "modulo", the remainder after division; mod 2^32 keeps the low 32 bits, as a 32-bit unsigned multiply does automatically
floor: round down to a whole number; dividing by 2^(32 − p) and rounding down keeps the top p of the 32 bits
^: "to the power of"
In words: multiply the key by a fixed odd constant, keep 32 bits of the product, and use their highest bits as the bucket number. This is the integer version of "keep the fraction and scale it up".
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

For a table of 2⁴ = 16 buckets, the aligned keys 8, 16, 24, …, 64, which shared just two buckets under `k % 16`, map to 15, 14, 13, 12, 11, 10, 9 and 8: all different. This fixed 32-bit mapping improves this example; it is not a universal collision or avalanche guarantee. Inputs differing by 2³² (about 4.3 billion) collide because the product is reduced modulo 2³².

## Key takeaways
- Multiplication uses a fractional product to choose a bucket.
- The fixed-width version keeps a word-sized product then extracts high index bits.
- The worked alignment example does not guarantee good distribution for every key set.

## Further reading
- [Hash function — Wikipedia](https://en.wikipedia.org/wiki/Hash_function)
