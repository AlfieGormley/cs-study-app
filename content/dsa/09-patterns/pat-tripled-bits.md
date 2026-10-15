---
id: pat-tripled-bits
title: Recover one value when all others occur three times
level: advanced
minutes: 3
sourceLesson: pat-bits
summary: Count each of the 32 bit positions modulo three.
---

XOR cancels pairs, so tripled values require a different summary. This unit counts each bit position independently under the signed 32-bit input contract.

## Every element thrice except one

For this code, input is a reusable sequence of signed 32-bit integers, with every value occurring three times except one occurring once. XOR does not cancel triples. Instead, count each bit position modulo 3: the bits of the tripled values contribute multiples of 3, so the remainder is the single number's bit.

```formula
s_b = c_b mod 3
c_b = 3t_b + s_b
c_0 = 3 × 1 + 1 = 4 → s_0 = 1
where
s_b: bit b of the single number, 0 or 1
c_b: how many numbers in the input have bit b set
t_b: how many of the tripled values have bit b set
b: a bit position, from 0 (lowest) to 31
c_0: the count for bit 0
s_0: bit 0 of the single number
mod: "modulo", the remainder after division
→: "so", the conclusion drawn from the line
In words: each tripled value adds 0 or 3 to a bit's count, so dividing the count by 3 leaves exactly the single number's bit; for [5, 5, 5, 3], bit 0 is set in all four numbers, 4 mod 3 = 1, and the single number 3 does have bit 0 set.
```

```python
def single_thrice(nums):
    res = 0
    for b in range(32):
        # Tripled values add multiples of
        # three.
        cnt = sum(n >> b & 1 for n in nums)
        if cnt % 3:
            res |= 1 << b
    if res >= 1 << 31:   # sign bit set
        # Convert the pattern to a signed
        # result.
        res -= 1 << 32
    return res
```

O(32n) time, O(1) space. The last two lines convert the 32-bit pattern back to a negative Python int.

## Key takeaways
- Count each of the 32 bit positions modulo three.
- The reconstruction assumes signed 32-bit input values and a reusable sequence.
- Convert a set sign bit back from an unsigned pattern to a negative Python value.

## Further reading
- [Bit manipulation — cp-algorithms](https://cp-algorithms.com/algebra/bit-manipulation.html)
- [Enumerating submasks — cp-algorithms](https://cp-algorithms.com/algebra/all-submasks.html)
- [Bit Twiddling Hacks — Sean Eron Anderson, Stanford](https://graphics.stanford.edu/~seander/bithacks.html)
- [Hamming weight — Wikipedia](https://en.wikipedia.org/wiki/Hamming_weight)
- [Binary cheatsheet — Tech Interview Handbook](https://www.techinterviewhandbook.org/algorithms/binary/)
