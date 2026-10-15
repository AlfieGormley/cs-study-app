---
id: pki-key-management-rotation
title: Key rotation and random-nonce limits
level: intermediate
minutes: 3
sourceLesson: pki-key-management
summary: KEK version rotation can leave earlier wrapped keys readable under retained material.
---

Envelope encryption separates a locally used data encryption key (DEK) from the key encryption key (KEK) protecting it. Key custody and application authorisation remain essential.

## Rotation

Rotating a key means new data is protected by new key material. In envelope systems there are two separate things to rotate:

- **KEK rotation**: for AWS-generated symmetric encryption keys, AWS KMS keeps every previous version of a key's material, wraps new DEKs with the latest, and still unwraps old ones automatically. The key's identifier does not change, and nothing is re-encrypted. Once enabled, automatic rotation runs yearly by default (configurable down to 90 days).
- **DEK rotation**: generate fresh DEKs for new data. With AES-GCM and random 96-bit nonces, NIST limits a key to 4,294,967,296 encryptions, so a DEK shared by billions of records must be replaced.

Where does 4,294,967,296 come from? With random nonces the danger is two encryptions picking the same nonce by chance, which breaks GCM. The birthday approximation gives the chance of any repeat:

```formula
P ≈ q(q − 1) / (2^{b+1})
P ≈ 2^{32} × 2^{32} / 2^{97} = 2^{−33}
where
P: the probability that at least two of the q nonces are equal
q: the number of encryptions under one key; here the NIST limit, 2^32 ≈ 4.3 billion
b: the nonce length in bits; 96 for GCM
≈: approximately equal to; the approximation is accurate while P is small
In words: the chance of a repeated nonce grows with the square of the number of messages; at 2^32 messages it is about 1 in 8.6 billion, inside NIST SP 800-38D's requirement that the chance of any repeat stay at or below 2^−32, NIST separately specifies the conservative 2^32 invocation cap for this construction; the approximation illustrates its margin rather than deriving that exact cap.
```

The square is the "birthday" effect: every pair of encryptions is a chance for a match, the number of pairs grows with the square of the number of messages, and each pair matches with probability 1 in roughly 79 octillion. Double the messages and the risk quadruples. For example, at 10 million encryptions a day one key reaches the limit in:

```formula
t = q_max / r
t = 4,294,967,296 / 10,000,000 ≈ 429.5 d
where
t: the time until the key must be retired, in days (d)
q_max: the NIST limit, 2^32 = 4,294,967,296 encryptions per key
r: the encryption rate, 10 million per day
≈: approximately equal to
d: days
In words: at 10 million encryptions a day, one random-nonce GCM key lasts about 14 months.
```

A fresh DEK per object keeps each key far below the random-IV invocation bound. A deterministic IV construction with guaranteed uniqueness avoids random collisions, but must also obey its own invocation, length and authentication limits. Count use across every device sharing a key.

Rotation limits how much data one key protects; it does *not* fix a compromise on its own. If a KEK leaked, old versions can still unwrap old DEKs. After a real compromise you must re-encrypt the data under keys the attacker never had.

## Key takeaways
- KEK version rotation can leave earlier wrapped keys readable under retained material.
- Random-nonce collision risk grows with the number of message pairs across all users of a key.
- Exposure recovery needs uncompromised keys and, where DEKs may be known, data re-encryption.

## Further reading
- [AWS KMS cryptographic details](https://docs.aws.amazon.com/kms/latest/developerguide/kms-cryptography.html)
- [NIST key-management guidance](https://csrc.nist.gov/pubs/sp/800/57/pt1/r5/final)
