---
id: secp-secret-scanning-entropy
title: Secret scanning and character entropy
level: intermediate
minutes: 4
sourceLesson: secp-secrets
summary: Calculate an empirical entropy score while recognising that a score is not proof of a secret.
---

Pattern scanning and character statistics can help find exposed credentials, but neither identifies every secret or proves that a string is unpredictable. This unit computes the empirical character-frequency score, then explains why apparently random hashes and ordinary identifiers can trigger it.

## Catching leaks: secret scanning

Prevention fails, so detect leaks early:

- **Pre-commit hooks** (gitleaks, detect-secrets) can block recognised secret patterns before commit, when installed and not bypassed.
- **Push protection** (GitHub secret scanning) can reject pushes containing supported secret formats, subject to enablement and bypass policy.
- **Repository and history scanning** finds what slipped through earlier.

Some scanners combine **patterns** for known formats (this illustrative regex detects an `AKIA` prefix followed by 16 uppercase letters/digits; temporary AWS access-key IDs use other prefixes such as `ASIA`, and an ID alone is not the secret key) with an **entropy score**: random keys look more random than code.

One score used by secret scanners is empirical character-frequency **Shannon entropy**, worked out from how often each character appears in the candidate string. It measures how "mixed" the characters are, in bits per character:

```formula
H = Σ p_i log_2(1 / p_i)
p_i = c_i / n
where
H: the empirical Shannon entropy of the string, in bits per character: 0 when every character is the same, higher when many different characters are used about equally often
Σ: sigma, meaning "add up": add the term after it once for every distinct character i in the string
i: one distinct character in the string (for "abcdabcd" there are four: a, b, c and d)
p_i: the fraction of the string made up of character i, between 0 and 1
c_i: how many times character i appears in the string
n: the length of the string, in characters
log_2: the base-2 logarithm: log_2(x) is the power you must raise 2 to in order to get x, so log_2(8) = 3; applied to 1 / p_i it gives that character’s information content in bits under the empirical distribution
In words: each character contributes "how common it is" times "how surprising it is"; a string of one repeated character scores zero, and equally frequent distinct characters increase the score.
```

The code below implements the frequency-weighted sum from the formula; each distinct character contributes once:

```python
import math
import re
from collections import Counter

AWS_ID = re.compile(r"AKIA[0-9A-Z]{16}")

def entropy(s):
    n = len(s)
    # Frequency of each distinct character.
    counts = Counter(s).values()
    # Average surprise per character.
    return sum(c / n * math.log2(n / c)
               for c in counts)

print(entropy("aaaaaaaa"))   # 0.0
print(entropy("abcdabcd"))   # 2.0
```

This function computes empirical character-frequency Shannon entropy, in bits per character; it does not measure the unpredictability of the process that generated a particular string. A string using 2 symbols equally often scores 1.0; 4 symbols, 2.0. Working two strings through by hand:

```formula
H("abcdabcd") = 4 × ((2 / 8) log_2(4))
H("abcdabcd") = 2.0 bpc
H("password") = 6 × ((1 / 8) × 3)
               + (2 / 8) × 2
H("password") = 2.75 bpc
H_max = log_2(64) = 6 bpc
where
H: the empirical Shannon entropy of the quoted string, in bits per character
log_2: the base-2 logarithm, so log_2(4) = 2, log_2(8) = 3 and log_2(64) = 6
H_max: the highest score for a string using only the 64 base64 data characters (excluding optional = padding), reached when those characters occur equally often
bpc: bits per character, the unit of this empirical score
In words: "abcdabcd" uses four characters equally (each a quarter of the string), giving 2 bits per character; "password" has six characters that appear once (1/8 each) and one, s, that appears twice (2/8), giving 2.75 bits per character; a string restricted to the 64 base64 data characters cannot score above 6 bits per character.
```

A finite sample's empirical score need not equal its generating distribution's entropy: a sample shorter than 64 characters cannot use all 64 base64 data characters evenly, so its empirical score is below 6 bits per character. By the same calculation `get_user_by_id` scores about 3.3. An entropy score alone produces false positives (hashes, UUIDs), so tools combine it with context like variable names (`password =`, `api_key:`).

## Key takeaways
- Use pre-commit, push and history scans as complementary leak-detection points.
- An access-key ID pattern does not establish possession of the secret key.
- Empirical character entropy describes frequencies in a sample rather than the randomness of its generator.
- Combine patterns, context and review; low or high scores alone do not settle whether a value is sensitive.

## Further reading
- [Yelp detect-secrets entropy implementation](https://github.com/Yelp/detect-secrets/blob/master/detect_secrets/plugins/high_entropy_strings.py)
- [GitHub push protection](https://docs.github.com/en/code-security/secret-scanning/introduction/about-push-protection)
- [OWASP secrets management](https://cheatsheetseries.owasp.org/cheatsheets/Secrets_Management_Cheat_Sheet.html)
