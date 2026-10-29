---
id: secf-security-properties
title: Confidentiality, integrity and availability
level: basic
minutes: 3
sourceLesson: secf-cia-aaa
summary: Name the property attacked before choosing a control.
---

"Is this system secure?" has no answer until you say *secure against what, protecting which property*. A bank's public interest-rate page has no secrets, but it matters a great deal if someone changes the numbers. A hospital's patient records must stay private, but they also must be available at 3 a.m. in A&E.

Security people use two small frameworks to make that question precise. The **CIA triad** names the properties you want to protect. **AAA** names the machinery that enforces who may do what, and records what happened.

## The CIA triad

| Property | Question it asks | Typical attack |
|---|---|---|
| Confidentiality | Who can read it? | Data breach |
| Integrity | Can it be changed undetected? | Tampering |
| Availability | Can it be used when needed? | DDoS, ransomware |

> [!analogy] Real-world analogy: a contract sent by post
> You post a signed contract to a solicitor. You want nobody else to read it, nobody to swap a page on the way, and the letter to arrive before the deadline.
>
> **How it maps:** Keeping other readers out is confidentiality. Noticing a swapped page is integrity. Delivery in time is availability. A tamper-evident seal plays the role of an integrity check, and a postal strike plays the role of a denial of service.
>
> **Where it stops:** A digital file can be copied without the original going missing, so a confidentiality breach can leave no visible trace, unlike a torn envelope. A seal also helps only if you know what the genuine seal looks like: that is the trusted-reference problem with hashes below.

### Confidentiality

Only authorised parties can **read** the information. Breaches of confidentiality are the ones that make headlines: a leaked customer database, an S3 bucket left public, a laptop stolen from a car.

Controls include encryption (at rest and in transit), access control, data minimisation (don't store what you don't need) and classification so people know what is sensitive.

Confidentiality also covers **metadata**. Even if a message is encrypted, the fact that a journalist contacted a particular source at 2 a.m. may be the real secret.

### Integrity

Integrity protects information against **improper modification or destruction**. It does not prove that the original information was factually true. A payment where an attacker changes the destination account number has not leaked anything; it has broken integrity.

Controls include cryptographic hashes and MACs, digital signatures, database constraints, version control, and access control on writes.

Integrity has a subtle sibling: **authenticity**, meaning the data came from who it claims to. A perfectly intact email that was forged by an attacker has integrity in the narrow sense, but not authenticity. A verified signature protects the signed bytes and links them to a signing key; attributing that key to a particular sender also requires a trusted key binding and protection of the private key.

```python
import hashlib

def digest(path):
    # Stream the file into one running hash.
    h = hashlib.sha256()
    with open(path, "rb") as f:
        for chunk in iter(
            lambda: f.read(65536), b""
        ):
            # Include each block exactly
            # once.
            h.update(chunk)
    # Return the printable digest to
    # compare.
    return h.hexdigest()

# Compare with the publisher's value.
# A mismatch means corruption or tampering.
```

> [!warning] A hash alone is not enough
> If an attacker can swap the file, they can usually swap the hash published next to it too. A plain hash detects accidents. To detect deliberate tampering, the reference value must come from a trusted channel, or you need a message authentication code or a digital signature (covered in the cryptography module).

### Availability

Authorised users can **use** the system when they need to. Availability failures include denial-of-service floods, ransomware encrypting a file server, a misconfigured firewall rule, or a single disk with no backup dying.

Controls include redundancy, backups (tested ones), rate limiting, capacity planning, DDoS protection and incident response plans.

Ransomware can attack availability and integrity by altering files; if data is also stolen, confidentiality is affected too.

## Key takeaways
- Name the property attacked before choosing a control.
- A hash needs a trusted reference to detect deliberate substitution.
- Ransomware can affect all three CIA properties.

## Further reading
- [NIST FIPS 199: security objectives](https://nvlpubs.nist.gov/nistpubs/FIPS/NIST.FIPS.199.pdf)
- [Python hashlib documentation](https://docs.python.org/3/library/hashlib.html)
- [VERIS security attributes](https://verisframework.org/attributes.html)
