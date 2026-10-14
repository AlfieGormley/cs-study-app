---
id: hash-function-polynomial
title: Polynomial hashes and character order
level: intermediate
minutes: 3
sourceLesson: hash-functions
summary: A string hash must preserve enough position information to avoid systematic anagram collisions.
---

A string hash must preserve enough position information to avoid systematic anagram collisions. We build the weighted sum incrementally, retaining the same result with only one running accumulator.

## Hashing strings: polynomial hashes

A string is a sequence of characters, and each character has a numeric code (`a` is 97 in ASCII and Unicode). A naive hash adds the character codes, but then every anagram collides: `"listen"` and `"silent"` both sum to 655.

A **polynomial hash** fixes this by weighting each position by a different power of a base, so character order affects the result without guaranteeing distinct totals:

```formula
h(s) = (c_0 p^{n − 1} + c_1 p^{n − 2}
        + … + c_{n−1}) mod M
h("abc") = 97 × 31^2 + 98 × 31 + 99
h("abc") = 93217 + 3038 + 99 = 96354
where
h(s): the hash of string s, a whole number from 0 to M − 1
s: the string being hashed, here "abc"
n: the number of characters in s, here 3
c_0: the numeric code of the first character (a = 97)
c_1: the numeric code of the second character (b = 98)
c_{n−1}: the code of the last character (c = 99), which gets weight 1
p: the base, a fixed whole number; here 31, a small prime commonly used for text
M: the modulus, a large prime such as 1,000,000,009 (10⁹ + 9) that keeps the result a manageable size
mod: "modulo", the remainder after dividing by M
…: the terms in between follow the same pattern
^: "to the power of"; 31^2 = 961
In words: multiply each character's code by the base raised to a power that falls by one per position, add the results and keep the remainder after dividing by M; "abc" gives 96,354, while "cab" gives 98,244.
```

Position weights distinguish many rearrangements, including the examples here, but do not guarantee distinct hashes for every permutation. A remainder has only finitely many possible values. Even before reduction, anagrams can share a weighted total: base thirty-one hashes both BAa and AaB to sixty-five thousand five hundred and thirty-eight. Their code-point sequences are (66, 65, 97) and (65, 97, 66), so these position weights do not uniquely encode every rearrangement. Hash matches therefore remain candidates for equality checks.

Computed with Horner's rule, it needs one multiply and one add per character:

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
