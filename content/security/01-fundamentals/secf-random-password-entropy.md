---
id: secf-random-password-entropy
title: Calculate random-password entropy
level: intermediate
minutes: 3
sourceLesson: secf-authentication
summary: Entropy calculations require a stated random-choice model.
---

Random password generation gives a useful counting model. We will count independent, equally likely choices; human password selection is not that model.


### Measuring strength: entropy

For a password chosen **uniformly at random** (every possibility equally likely), **bits of entropy** describe the size of its possible-value set. Each extra bit doubles that set. Fifty-two bits corresponds to about 4.5 thousand million million equally likely values. Guessing strategy and rate determine the work needed. The random-choice model gives:

```formula
H = log_2(N^L) = L log_2(N)
where
H: the password's entropy, in bits: an attacker trying every possibility needs up to 2^H guesses
N: the number of choices for each symbol: 94 non-space printable ASCII characters, 7,776 words in a Diceware list, or 10 digits in a PIN
L: the length: how many symbols (characters or words) are chosen
N^L: L copies of N multiplied together: the total number of possible passwords
log_2: the logarithm to base 2: log_2(x) is the power you must raise 2 to in order to get x, so log_2(8) = 3 and log_2(1024) = 10
In words: entropy in bits is the number of times you would have to double 1 to reach the number of possible passwords, and each extra random symbol adds the same number of bits again.
```

Taking the logarithm turns multiplication of choices into addition of bits. Each independent random character or word adds a fixed number of bits. Five six-sided-die rolls have 7,776 possible outcomes, which index the Diceware list. Two worked examples:

```formula
H_c = 8 × log_2(94)
H_c ≈ 8 × 6.555 ≈ 52.4 bits
H_w = 4 × log_2(7776)
H_w ≈ 4 × 12.925 ≈ 51.7 bits
where
H_c: entropy of 8 random characters from the 94 non-space printable ASCII characters, in bits
H_w: entropy of 4 random words from a 7,776-word Diceware list, in bits
log_2: the logarithm to base 2: log_2(94) ≈ 6.555 because 2^6.555 ≈ 94
≈: approximately equal to (the logarithms are rounded)
bits: the unit of entropy; one bit is one doubling of the number of possibilities
In words: eight random printable characters and four random Diceware words are about equally strong, at roughly 52 bits each.
```

The same counting model gives these rounded comparisons:

| Password scheme | Possibilities | Bits |
|---|---|---|
| 8 random non-space printable ASCII | About 6.1 thousand million million | About 52 |
| 4 random Diceware words | About 3.7 thousand million million | About 52 |
| 6 random Diceware words | About 220 thousand million million million | About 78 |
| 4-digit PIN | 10,000 | About 13 |

The formula only applies to random choices. `Password1!` contains every character class, but its predictability places it early in common guessing strategies. Actual time depends on rate limits, hash cost and the attack setup.

Prepare `wordlist.txt` with exactly 7,776 distinct words and no numeric indices, one word per line. Indexed downloadable lists need their indices removed first. The first two printed lines are entropy values; the third is a fresh random passphrase, so its exact words vary.

```python
import math, secrets

def bits(n_choices, length):
    # Independent choices add equal bits.
    return length * math.log2(n_choices)

print(round(bits(94, 8), 1))    # 52.4
print(round(bits(7776, 6), 1))  # 77.5

# Draw six words independently; the output
# varies, and repeated words are permitted.
with open(
    "wordlist.txt", encoding="utf-8"
) as f:
    words = f.read().split()
# A duplicate would distort probabilities.
assert len(words) == len(set(words)) == 7776
print(" ".join(
    secrets.choice(words) for _ in range(6)
))
```

Note `secrets`, not `random`: `random` is a predictable generator not meant for security.

## Key takeaways
- Entropy calculations require a stated random-choice model.
- Each independently selected character or word adds predictable entropy.
- Use a security-oriented generator and a valid word list.

## Further reading
- [EFF: random-word passphrases and word lists](https://www.eff.org/dice)
- [Python secrets documentation](https://docs.python.org/3/library/secrets.html)
