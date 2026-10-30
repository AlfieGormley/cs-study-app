---
id: hash-function-polynomial
title: Polynomial hashes and character order
level: intermediate
minutes: 3
sourceLesson: hash-functions
summary: Weighting each character by its position stops anagrams colliding systematically, and Horner's rule computes it in one pass.
---

A string hash must use the *order* of the characters, not just which characters appear. Otherwise every rearrangement of the same letters collides.

## Hashing strings: polynomial hashes

A string is a sequence of characters, and each character has a numeric code (`a` is 97 in ASCII and Unicode). A naive hash adds the character codes, but then every anagram collides: `"listen"` and `"silent"` both sum to 655.

A **polynomial hash** fixes this by giving each position a different weight: the last character is multiplied by 1, the one before it by a base p (such as 31), the one before that by p², and so on. The weighted sum is reduced modulo a large number M to keep it a manageable size. Order now matters: with base 31, `"abc"` hashes to 96,354 but `"cab"` to 98,244, because whichever character comes first carries the biggest weight.

```formula reference
h(s) = (c_0 p^(n − 1) + c_1 p^(n − 2)
        + … + c_(n−1)) mod M
where
h(s): the hash of string s, a whole number from 0 to M − 1
s: the string being hashed
n: the number of characters in s
c_0: the numeric code of the first character
c_1: the numeric code of the second character
c_(n−1): the code of the last character, which gets weight 1
p: the base, a fixed whole number such as 31
M: the modulus, a large number such as the prime 1,000,000,009
mod: "modulo", the remainder after dividing by M
…: the terms in between follow the same pattern
^: "to the power of"
In words: multiply each character's code by the base raised to a power that falls by one per position, add the results and keep the remainder after dividing by M.
```

> [!analogy] Real-world analogy: place value in ordinary numbers
> The digits 1, 2 and 3 can make 123 or 321. Same digits, different numbers, because the leftmost digit is worth hundreds and the rightmost only units.
>
> **How it maps:** a polynomial hash treats each character code as a "digit" in base p instead of base 10. The first character gets the highest power of the base, so rearranging the characters changes the total.
>
> **Where it stops:** decimal digits are always smaller than 10, so every digit string has exactly one value. Character codes are larger than a base such as 31, so different strings can add up to the same total, and the final remainder squeezes all strings into M values.

Position weights distinguish many rearrangements, but not all of them. A remainder has only finitely many values, and even before reduction two anagrams can share a weighted sum: with base 31, `"BAa"` and `"AaB"` both hash to 65,538. A matching hash is therefore only a candidate; the table still compares the actual strings.

You never compute the powers separately. **Horner's rule** walks the string once, multiplying the running total by the base and adding the next code, which gives every earlier character one more factor of the base:

```python
def poly_hash(s, p=31, M=10**9 + 9):
    h = 0
    for ch in s:
        # Shift old weights, add the new
        # code.
        h = (h * p + ord(ch)) % M
    return h

poly_hash("abc")
# 97*31^2 + 98*31 + 99 = 96354
```

Java's `String.hashCode` uses base 31 over UTF-16 code units, with signed 32-bit overflow instead of a prime modulus. Python's `ord` gives Unicode code points, so the code above differs from Java for supplementary characters (such as emoji) even with a modulus of 2³².

## Key takeaways
- Position-dependent weights avoid systematic anagram collisions.
- Horner’s rule accumulates a weighted hash in one pass.
- Python code points and Java UTF-16 code units differ for supplementary characters.

## Further reading
- [String hashing — cp-algorithms](https://cp-algorithms.com/string/string-hashing.html)
