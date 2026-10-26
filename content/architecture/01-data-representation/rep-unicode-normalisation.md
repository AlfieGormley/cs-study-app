---
id: rep-unicode-normalisation
title: Canonical equivalence and normalisation
level: intermediate
minutes: 3
summary: Visually identical strings can have different code-point sequences.
sourceLesson: rep-text-encoding
---

Text can have different code-point spellings that represent the same abstract text. Normalisation supplies a consistent spelling when that equivalence is intended.

## Normalisation

Because `é` has two spellings, two strings can look identical but compare unequal:

```python
# Compose canonically equivalent text.
import unicodedata as ud

a = 'café'      # precomposed
b = 'café'     # e + combining
a == b               # False
len(a), len(b)       # (4, 5)
ud.normalize('NFC', b) == a   # True
```

Unicode defines normal forms. **NFC** composes where possible (the usual choice for storage and comparison). **NFD** decomposes. HFS+ historically uses a modified decomposed form; other macOS file systems have different storage and comparison rules. Do not assume that all macOS filenames are byte-for-byte standard NFD. **NFKC** also folds "compatibility" variants such as `ﬁ` (one ligature code point) into `fi`, which is useful for search and usernames.

Python's `.upper()` changes letter case without performing Unicode normalisation. The two displayed spellings therefore still compare unequal after both are upper-cased; their UTF-8 byte sequences also remain different until an appropriate normal form reconciles them.

### Choose the equivalence you actually need

Canonical normalisation reconciles alternative encodings of the same abstract text. It does not make every pair of visually similar strings equal: a Latin letter and a lookalike Cyrillic letter can remain different. Font choice can also hide differences that normalisation does not remove.

Compatibility normalisation goes further. The ligature ﬁ and the two letters fi are compatibility-equivalent, so NFKC can make them match; NFC preserves their difference. That transformation can discard distinctions useful in the original text. Choose it deliberately for a search index or an identifier policy, and keep an original copy where fidelity matters.

Normalisation is also separate from case folding, language-aware sorting and path validation. Apply the rules required by the relevant protocol in a defined order. A stored normal form can simplify comparisons, but it does not make a username safe or prove two users intended the same name.

## Key takeaways
- Visually identical strings can have different code-point sequences.
- Choose a normal form according to the application and protocol.

## Further reading
- [Unicode 17 conformance and encoding forms](https://www.unicode.org/versions/Unicode17.0.0/core-spec/chapter-3/)
- [RFC 3629: UTF-8](https://www.rfc-editor.org/rfc/rfc3629)
