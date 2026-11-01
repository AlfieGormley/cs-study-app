---
id: secp-secret-scanning-entropy
title: Secret scanning and character entropy
level: intermediate
minutes: 4
sourceLesson: secp-secrets
summary: Understand what an entropy score measures and why scanners combine it with patterns and context.
---

Pattern scanning and character statistics can help find exposed credentials, but neither identifies every secret or proves that a string is unpredictable. This unit explains what a character-entropy score measures, then why ordinary hashes trip it while real passwords can slip past.

## Catching leaks: secret scanning

Prevention fails, so detect leaks early:

- **Pre-commit hooks** (gitleaks, detect-secrets) can block recognised secret patterns before commit, when installed and not bypassed.
- **Push protection** (GitHub secret scanning) can reject pushes containing supported secret formats, subject to enablement and bypass policy.
- **Repository and history scanning** finds what slipped through earlier.

Scanners combine three kinds of evidence:

1. **Known formats.** A provider's key often has a recognisable shape. For example, a regex for `AKIA` followed by 16 uppercase letters or digits finds long-term AWS access-key IDs (temporary ones use other prefixes such as `ASIA`). An access-key ID alone is not the secret key, but it shows where to look.
2. **Context.** Names such as `password =`, `api_key:` or `Authorization:` next to a value raise suspicion even when the value looks ordinary.
3. **Randomness of the characters.** Generated keys mix many characters evenly; code and words repeat a few. An **entropy score** captures that.

## What an entropy score measures

The score many scanners use is empirical character-frequency **Shannon entropy**, in bits per character: count how often each character appears in the candidate string and measure how evenly spread those counts are.

```formula reference
H = Σ p_i log_2(1 / p_i)
where
H: the empirical Shannon entropy of the string, in bits per character: 0 when every character is the same, higher when many different characters appear about equally often
Σ: sigma, meaning "add up": add the term after it once for every distinct character i in the string
i: one distinct character in the string
p_i: the fraction of the string made up of character i, between 0 and 1
log_2: the base-2 logarithm: log_2(x) is the power you must raise 2 to in order to get x, so log_2(8) = 3
In words: a string of one repeated character scores zero; the more distinct characters a string uses, and the more evenly it uses them, the higher it scores, up to a ceiling set by the character set (6 bits per character for the 64 base64 data characters).
```

A short Python version shows the behaviour on realistic strings:

```python
import math
from collections import Counter

def entropy(s):
    n = len(s)
    # Frequency-weighted surprise per char.
    return sum(c / n * math.log2(n / c)
               for c in Counter(s).values())

# A 40-hex-digit git commit hash.
sha = ("9fceb02d0ae598e95dc9"
       "70b74767f19372d61af8")
samples = ["aaaaaaaa", sha,
           "Summer2024!", "get_user_by_id"]
for s in samples:
    # Prints 0.0, 3.87, 3.1, 3.32
    print(round(entropy(s), 2))
```

Read those results as a scanner would:

- The git commit hash scores high because hex digits appear evenly, yet it is public. Hashes, UUIDs and build IDs are the classic **false positives**.
- `Summer2024!` is a plausible real password but scores *lower* than the function name `get_user_by_id`. Short, human-chosen secrets are the classic **false negatives** for entropy alone.
- The score describes this sample's character counts, not the process that generated it. A string shorter than 64 characters cannot use all 64 base64 characters evenly, so short random keys also score below the theoretical ceiling.

Thresholds are tool settings, not facts about secrecy. detect-secrets, for example, flags quoted base64-looking strings scoring above 4.5 and quoted hex strings scoring above 3.0 by default (checked November 2026), and separately looks for keywords such as `password`. That is why a scanner hit needs triage: confirm whether the value is live, and if it is, treat it as exposed and revoke it.

## Key takeaways
- Use pre-commit, push and history scans as complementary leak-detection points.
- An access-key ID pattern does not establish possession of the secret key.
- Empirical character entropy describes frequencies in a sample rather than the randomness of its generator.
- Hashes and IDs trip entropy rules; short human-chosen passwords can slip under them.
- Combine patterns, context and review; low or high scores alone do not settle whether a value is sensitive.

## Further reading
- [Yelp detect-secrets entropy implementation](https://github.com/Yelp/detect-secrets/blob/master/detect_secrets/plugins/high_entropy_strings.py)
- [GitHub push protection](https://docs.github.com/en/code-security/secret-scanning/introduction/about-push-protection)
- [OWASP secrets management](https://cheatsheetseries.owasp.org/cheatsheets/Secrets_Management_Cheat_Sheet.html)
