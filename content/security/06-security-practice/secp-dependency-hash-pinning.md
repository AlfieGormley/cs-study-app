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

For each downloaded distribution, pip requires a match with an allowed digest for that requirement; several allowed hashes can cover different platform files. A cryptographic hash such as SHA-256 maps a file of any size to a fixed-length fingerprint (256 bits, written as 64 hexadecimal characters). pip installs a file only when the fingerprint of what it downloaded equals one you recorded.

For example, if someone replaces `requests-2.32.3` on a mirror with a modified copy, its SHA-256 digest will, in practice, differ from the recorded full digest (shown here only as `70761c...`), and pip refuses it. Collisions are mathematically possible, so a match is strong computational evidence of approved bytes rather than a proof.

The check has a sharp limit: it compares bytes, not intentions. If the file you recorded was already malicious, its digest matches perfectly and pip installs it. Hash checking also says nothing about vulnerabilities discovered later in the approved file.

> [!analogy] Real-world analogy: photographing your bike before a repair
> Before leaving your bike at a repair shop, you photograph it. When you collect it, you compare the bike with the photo: if the shop hands you a different bike, you notice at once.
>
> **How it maps:** The photo is the recorded digest in `requirements.txt`; collecting the bike is pip downloading a file; refusing a bike that does not match the photo is hash-checking mode rejecting an unapproved file.
>
> **Where it stops:** If the frame was already bent when you took the photo, the bent bike matches perfectly: a hash approves exact bytes, not their safety. And a photo can miss a small change, whereas changing even one byte of a file changes its SHA-256 digest in practice.

## Key takeaways
- Exact versions and artifact hashes make updates deliberate.
- Hash checking tests approved bytes, rather than the safety of those bytes.
- Platform markers, artifacts and installer behaviour still affect reproducibility.

## Further reading
- [pip secure installs](https://pip.pypa.io/en/stable/topics/secure-installs/)
- [NIST Secure Hash Standard](https://csrc.nist.gov/pubs/fips/180-4/upd1/final)
