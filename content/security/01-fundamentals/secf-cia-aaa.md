---
id: secf-cia-aaa
title: The CIA triad and AAA
level: basic
minutes: 10
summary: What "secure" actually means (confidentiality, integrity, availability) and the authentication, authorisation and accounting machinery that enforces it.
---

"Is this system secure?" has no answer until you say *secure against what, protecting which property*. A bank's public interest-rate page has no secrets, but it matters a great deal if someone changes the numbers. A hospital's patient records must stay private, but they also must be available at 3 a.m. in A&E.

Security people use two small frameworks to make that question precise. The **CIA triad** names the properties you want to protect. **AAA** names the machinery that enforces who may do what, and keeps a record of it.

## The CIA triad

| Property | Question it asks | Typical attack |
|---|---|---|
| Confidentiality | Who can read it? | Data breach |
| Integrity | Can it be changed undetected? | Tampering |
| Availability | Can it be used when needed? | DDoS, ransomware |

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
    h = hashlib.sha256()
    with open(path, "rb") as f:
        for chunk in iter(
            lambda: f.read(65536), b""
        ):
            h.update(chunk)
    return h.hexdigest()

# Compare with the publisher's value.
# A mismatch means corruption or tampering.
```

> [!warning] A hash alone is not enough
> If an attacker can swap the file, they can usually swap the hash published next to it too. A plain hash detects accidents. To detect deliberate tampering, the reference value must come from a trusted channel, or you need a MAC or signature (covered in the cryptography module).

### Availability

Authorised users can **use** the system when they need to. Availability failures include denial-of-service floods, ransomware encrypting a file server, a misconfigured firewall rule, or a single disk with no backup dying.

Controls include redundancy, backups (tested ones), rate limiting, capacity planning, DDoS protection and incident response plans.

Ransomware can attack availability and integrity by altering files; if data is also stolen, confidentiality is affected too.

## The properties pull against each other

Disconnecting a server can reduce remote exposure while making its service unavailable. It does not prevent physical access or disclosure of existing copies. Real design evaluates the risks to each property.

- **Encryption** improves confidentiality but adds a key that, if lost, makes data permanently unavailable.
- **Account lockout** after failed logins protects confidentiality, but lets an attacker lock out every user on purpose (an availability attack).
- **Backups** protect availability, but each copy is another place the data can leak from.
- **Fail-closed** behaviour (deny on error) can protect confidentiality and integrity while blocking legitimate use; **fail-open** (allow on error) can preserve access while bypassing a control. Choose based on the failure and threat model.

> [!example] Which property matters most?
> Priorities depend on the system and threat model. For example:
> - Password reset tokens: confidentiality, plus integrity of the account binding and expiry checks.
> - A public software update channel: integrity and authenticity, so devices reject unauthorised releases.
> - A time-critical operational display: availability and integrity can both be essential.
> - A medical record: privacy, correct handling of changes and timely access all matter.

### Beyond three letters

The triad is a starting point, not the whole story. Commonly added properties:

- **Non-repudiation**: evidence that supports attribution of an action and helps resolve a later dispute. Individual credentials, protected records and signatures can contribute; no mechanism alone guarantees attribution to a person or a legal outcome.
- **Authenticity**: as above, the origin is genuine.
- **Privacy**: about people, not just data, including consent and purpose (GDPR territory).

The VERIS framework uses paired attributes from the **Parkerian hexad**: confidentiality/possession, integrity/authenticity and availability/utility. Losing control of an encrypted drive can affect possession without exposing its plaintext; losing its only decryption key affects utility.

## AAA: authentication, authorisation, accounting

The CIA properties are goals. AAA is the plumbing most systems use to reach them.

```
 request
   |
   v
+-----------------+  who are you?
| Authentication  |---- reject
+-----------------+
   | identity
   v
+-----------------+  may you do this?
| Authorisation   |---- deny
+-----------------+
   | allowed
   v
 resource
   |
   v
+-----------------+  what happened?
| Accounting      |--> audit log
+-----------------+
```

### Authentication: who are you?

The system verifies a claimed identity, using something you know (password), have (security key, phone) or are (fingerprint). The lesson on authentication covers this in depth.

Note the distinction between **identification** (claiming to be `alice`) and **authentication** (checking evidence for that claim). Typing a username is identification; the password is authentication.

### Authorisation: what may you do?

Once the system knows who you are, it decides whether *this* identity may perform *this* action on *this* resource. Alice may read her own payslip but not Bob's. This is **access control**, covered in its own lesson.

HTTP `401 Unauthorized` means the request lacks valid authentication credentials for the target resource; the response must include a `WWW-Authenticate` challenge. `403 Forbidden` means the server understood the request but refuses it. A 403 can reflect insufficient permissions, but does not itself prove the requester was authenticated.

> [!tip] Authentication is not authorisation
> Many breaches involve a perfectly authenticated user doing something they were never authorised to do, such as changing `/invoices/1001` to `/invoices/1002` in the URL. Checking that a user is logged in is not the same as checking that they may access that object.

### Accounting: what happened?

The system records who did what, when and from where. Accounting serves:

- **Detection**: spotting attacks in progress (100 failed logins in a minute).
- **Investigation**: reconstructing an incident afterwards.
- **Attribution and compliance evidence**: recording which account approved a payment.
- **Billing**, which is where the term came from in network access.

Good audit logs are themselves an integrity problem. Forward them promptly to a separately administered collector, ideally with append-only retention. This protects received records against production administrators, but a compromised source can still omit or forge events. Monitor collection failures and corroborate important events with other evidence.

### Where AAA appears in practice

The term comes from network access control. **RADIUS** (RFC 2865) and its accounting extension (RFC 2866) let a Wi-Fi access point or VPN concentrator hand the "who is this and are they allowed on?" question to a central server, and report session start and stop for accounting. **TACACS+** does the same job for administering routers and switches, with per-command authorisation. **Diameter** (RFC 6733) is another AAA protocol, designed to address limitations of RADIUS and support applications including network access and mobility. This does not mean RADIUS has disappeared.

In modern applications the same split shows up as:

| AAA part | Typical web/cloud form |
|---|---|
| Authentication | OIDC login, passkeys, SSO |
| Authorisation | IAM policies, RBAC checks |
| Accounting | Audit logs, CloudTrail |

## Pitfalls

1. **Treating security as one property.** "We encrypt everything" says nothing about integrity or availability.
2. **Authenticating once, authorising never.** Login checks run, but individual endpoints don't check ownership.
3. **Logs nobody reads, or logs the attacker can erase.** Accounting only helps if it is protected and monitored.
4. **Logging secrets.** Writing passwords or session tokens into logs turns your audit trail into a confidentiality breach.
5. **Forgetting availability.** A security control that takes the service down (an aggressive lockout, a WAF rule blocking all traffic) is itself an incident.

## Key takeaways
- Confidentiality, integrity and availability are distinct goals; name which ones a control protects.
- Controls can introduce trade-offs: evaluate key loss, lockout abuse and failure behaviour alongside the intended protection.
- Authentication checks evidence for a claimed identity, authorisation decides permission, accounting records events.
- HTTP 401 requires an authentication challenge; 403 is a refusal and does not guarantee authentication succeeded.
- Audit logs must be protected from the very administrators they monitor, and must not contain secrets.

> [!note] Scope and evidence
> These are illustrative threat models, not a universal ranking of risks. Legal assurance for signatures and production log completeness are not established here; those depend on the system, evidence and applicable process.

## Further reading
- [NIST FIPS 199: security objectives](https://nvlpubs.nist.gov/nistpubs/FIPS/NIST.FIPS.199.pdf)
- [RFC 9110: HTTP status semantics](https://www.rfc-editor.org/rfc/rfc9110.html)
- [OWASP: Logging Cheat Sheet](https://cheatsheetseries.owasp.org/cheatsheets/Logging_Cheat_Sheet.html)
- [VERIS security attributes](https://verisframework.org/attributes.html)
- [AAA (computer security) — Wikipedia](https://en.wikipedia.org/wiki/AAA_(computer_security))
- [Parkerian Hexad — Wikipedia](https://en.wikipedia.org/wiki/Parkerian_Hexad)
- [RFC 2865: RADIUS](https://www.rfc-editor.org/rfc/rfc2865)
- [Non-repudiation — Wikipedia](https://en.wikipedia.org/wiki/Non-repudiation)
