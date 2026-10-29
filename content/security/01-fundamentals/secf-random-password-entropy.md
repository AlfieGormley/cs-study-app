---
id: secf-random-password-entropy
title: What random-password entropy measures
level: intermediate
minutes: 3
sourceLesson: secf-authentication
summary: Each random symbol multiplies the possibilities; entropy counts the doublings.
---

Random password generation gives a useful counting model. It counts independent, equally likely choices; human password selection is not that model.


### Measuring strength: entropy

For a password chosen **uniformly at random** (every possibility equally likely), **bits of entropy** describe the size of its possible-value set. Each extra bit doubles that set, and so doubles the worst-case work of an attacker who must try every possibility.

The key behaviour is multiplication. Every extra random character multiplies the number of possible passwords by the size of the character set; every extra random word multiplies it by the size of the word list. Counting in bits turns that repeated multiplication into simple addition:

```formula essential
H = L log_2(N)
where
H: the password's entropy, in bits; each extra bit doubles the number of equally likely possibilities
L: the length: how many symbols (characters or words) are chosen independently at random
N: the number of equally likely choices for each symbol, such as 94 printable characters, 7,776 Diceware words or 10 digits
log_2: the logarithm to base 2: log_2(N) is the number of doublings of 1 needed to reach N, so log_2(8) = 3
In words: each independently random symbol adds the same number of bits, so adding one more symbol multiplies the attacker's search by the number of choices per symbol.
```

A random printable character adds about 6.6 bits; a random Diceware word (five dice rolls choose one of 7,776 words) adds about 12.9 bits. The same counting model gives these rounded comparisons:

| Password scheme | Possibilities | Bits |
|---|---|---|
| 8 random non-space printable ASCII | About 6.1 thousand million million | About 52 |
| 4 random Diceware words | About 3.7 thousand million million | About 52 |
| 6 random Diceware words | About 220 thousand million million million | About 78 |
| 4-digit PIN | 10,000 | About 13 |

Moving from four to six Diceware words does not make the search 50 % larger: it multiplies it by 7,776 twice, roughly 60 million times.

> [!analogy] Real-world analogy: a combination bike lock
> A bike lock with three dials of ten digits has 1,000 settings; add a fourth dial and it has 10,000. Each dial multiplies the settings by ten rather than adding ten.
>
> **How it maps:** Each dial is one random symbol, and its ten digits are the choices per symbol. Multiplying settings is why entropy adds a fixed number of bits per symbol: about 3.3 bits per ten-digit dial.
>
> **Where it stops:** The count assumes the combination was set at random. An owner who picks 1234 or a birthday has far fewer likely settings, which is the human-choice problem below. A thief can also attack the lock itself instead of trying combinations, just as attackers phish or steal passwords instead of guessing.

### When the model does not apply

The formula only applies to random choices. `Password1!` contains every character class, but its predictability places it early in common guessing strategies. A passphrase of four words a person picked because they sound good has far less entropy than four dice-chosen words. Actual cracking time also depends on rate limits, hash cost and the attack setup, covered in later lessons.

### Generating a random passphrase

The randomness must come from a security-oriented generator. Prepare `wordlist.txt` with exactly 7,776 distinct words and no numeric indices, one word per line; indexed downloadable lists need their indices removed first. The printed passphrase is random, so its words vary each run.

```python
import secrets

with open(
    "wordlist.txt", encoding="utf-8"
) as f:
    words = f.read().split()
# A duplicate would distort probabilities.
assert len(words) == len(set(words)) == 7776
# Six independent draws; repeats allowed.
print(" ".join(
    secrets.choice(words) for _ in range(6)
))
```

Note `secrets`, not `random`: `random` is a predictable generator not meant for security.

## Key takeaways
- Entropy calculations require a stated random-choice model.
- Each independently random character or word multiplies the search, adding a fixed number of bits.
- Use a security-oriented generator and a valid word list.

## Further reading
- [EFF: random-word passphrases and word lists](https://www.eff.org/dice)
- [Python secrets documentation](https://docs.python.org/3/library/secrets.html)
