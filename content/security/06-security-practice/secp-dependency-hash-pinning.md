---
id: secp-dependency-hash-pinning
title: Lockfiles and artifact hashes
level: intermediate
minutes: 3
sourceLesson: secp-supply-chain
summary: Understand what an enforced package hash checks and what it cannot prove.
---

Version selection and byte identity are different checks. A lockfile records intended dependency choices; an enforced artifact hash checks whether the downloaded bytes are one of the approved files. Neither establishes that the approved package is harmless.

## Lockfiles and artifact hashes

A **lockfile** (`poetry.lock`, `package-lock.json`, `requirements.txt` from `pip-compile`) records resolved dependency choices; complete reproducibility also depends on platform markers, artifacts, installer behavior and how the lockfile is enforced. With **hashes**, the installer also refuses an artefact whose content differs from what you reviewed:

```
# Schematic only: digest is truncated.
# A real requirements file needs all digits.
requests==2.32.3 \
  --hash=sha256:70761c...
```

```
pip install --require-hashes \
  -r requirements.txt
```

For each downloaded distribution, pip requires a match with an allowed digest for that requirement; several allowed hashes can cover different platform files. A cryptographic hash maps bytes to a fixed-length fingerprint. Changed bytes overwhelmingly produce a different SHA-256 digest, but collisions are mathematically possible:

```formula
H(f) = h_lock
where
H: the SHA-256 hash function: it turns a file of any size into a 256-bit fingerprint, written as 64 hexadecimal characters
f: the package file pip has just downloaded (a wheel or source archive)
h_lock: the SHA-256 fingerprint you recorded for that file in requirements.txt, after --hash=sha256:
In words: pip installs a file only when the fingerprint of what it downloaded equals the fingerprint you recorded; a swapped or tampered file with no approved digest match is rejected. Matching a digest does not prove that the approved file is safe.
```

For example, if someone replaces `requests-2.32.3` on a mirror with a modified copy, its digest will overwhelmingly differ from the recorded full digest (shown here only as `70761c...`) and pip refuses it. A match provides strong computational evidence of approved bytes, subject to the hash function’s collision resistance. If the file you recorded was already malicious, its *H(f)* matches perfectly.

## Key takeaways
- Exact versions and artifact hashes make updates deliberate.
- Hash checking tests approved bytes, rather than the safety of those bytes.
- Platform markers, artifacts and installer behaviour still affect reproducibility.

## Further reading
- [pip secure installs](https://pip.pypa.io/en/stable/topics/secure-installs/)
- [NIST Secure Hash Standard](https://csrc.nist.gov/pubs/fips/180-4/upd1/final)
