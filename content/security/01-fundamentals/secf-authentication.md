---
id: secf-authentication
title: Authentication factors and passwords
level: intermediate
minutes: 13
summary: Knowledge, possession and inherence factors, why passwords fail, how to store them, modern NIST guidance, and why passkeys resist phishing when one-time codes don't.
---

Authentication answers one question: *is this really the account holder?* Everything else in security depends on it. If an attacker can authenticate as your administrator, your access control, encryption and audit logs are all working for them.

## The three factors

| Factor | Something you... | Examples |
|---|---|---|
| Knowledge | know | Password, PIN |
| Possession | have | Security key, phone |
| Inherence | are | Fingerprint, face |

**Multi-factor authentication (MFA)** combines factors from *different* categories. A password plus a security question is still single-factor: both are knowledge, and both can be phished or found in a data breach together.

The point of MFA is independence: stealing a password from a breach dump doesn't give the attacker your phone. Its effectiveness depends on the authenticator and attack path; recovery and session theft need separate protection.

> [!note] Biometrics are not secrets
> Your face is on social media and your fingerprints are on every glass you hold. Biometrics work well as a *local* unlock (the phone checks your fingerprint, then uses a key stored in secure hardware). They work badly as a password sent to a server, because you can't change them after a leak.

## Why passwords fail

Passwords are cheap and universal, but they fail in predictable ways:

- **Reuse.** One breached site's passwords are tried on every other site. This is **credential stuffing**, and it works because a substantial fraction of people reuse passwords.
- **Guessability.** People choose `123456`, names, sports teams and keyboard walks.
- **Phishing.** A convincing fake login page collects the password directly.
- **Theft from servers.** Badly stored password databases leak in plaintext or as fast hashes.

Password reuse can permit account takeover without cracking the target service's password database.

### Measuring strength: entropy

For a password chosen **uniformly at random** from N possibilities, the strength is log2(N) bits.

| Password scheme | Possibilities | Bits |
|---|---|---|
| 8 random non-space printable ASCII | 94^8 ≈ 6.1 × 10^15 | ≈ 52 |
| 4 random Diceware words | 7776^4 ≈ 3.7 × 10^15 | ≈ 52 |
| 6 random Diceware words | 7776^6 ≈ 2.2 × 10^23 | ≈ 78 |
| 4-digit PIN | 10^4 | ≈ 13 |

The formula only applies to random choices. `Password1!` contains every character class, but its predictability places it early in common guessing strategies. Actual time depends on rate limits, hash cost and the attack setup.

```python
import math, secrets

def bits(n_choices, length):
    return length * math.log2(n_choices)

print(round(bits(94, 8), 1))    # 52.4
print(round(bits(7776, 6), 1))  # 77.5

# Generate a random passphrase
with open(
    "wordlist.txt", encoding="utf-8"
) as f:
    words = f.read().split()
assert len(words) == len(set(words)) == 7776
print(" ".join(
    secrets.choice(words) for _ in range(6)
))
```

Note `secrets`, not `random`: `random` is a predictable generator not meant for security.

## Modern password policy (NIST SP 800-63B)

NIST SP 800-63B-4 distinguishes mandatory requirements (SHALL) from recommendations (SHOULD). The following concerns centrally verified passwords, not local device-unlock PINs:

- **Length over complexity.** At least **15 characters** when the password is the only factor; at least 8 when it's part of MFA. Permitting at least 64 characters, printable ASCII and spaces, and Unicode are SHOULD recommendations.
- **No composition rules.** Don't demand "one uppercase, one symbol".
- **No periodic forced changes.** Force a change only on evidence of compromise.
- **Blocklist check.** Compare the entire proposed password against a blocklist of common, expected or compromised passwords. Do not reject a passphrase just because it contains a dictionary word as a substring.
- **Rate limiting.** Unless the authenticator type specifies otherwise, no more than 100 consecutive failures using a specific authenticator on one account before disabling that authenticator; in practice, use throttling and back-off well before that.
- **Allow paste and password managers.**

> [!warning] Lockout is an availability trade-off
> Locking an account after 5 failures stops guessing, but lets anyone lock out your CEO, or every user, on purpose. Prefer progressive delays, per-IP and per-account throttling, and risk signals. A stuffing campaign may try only one or a few credentials per account across many accounts, so per-account thresholds alone can miss it.

## Storing passwords

The server must be able to *verify* a password without being able to *recover* it. Never store plaintext, and never use reversible encryption.

1. **Hash** the password with a suitable password function; attackers can still test guesses against a stolen verifier.
2. **Salt** it: add a unique random value per user before hashing. Identical passwords then produce different hashes, and precomputed tables (rainbow tables) become useless.
3. Use a **slow, memory-hard** password hashing function, so each guess has a substantial resource cost tuned to the deployment.

Fast hashes like SHA-256 are designed to be quick; actual cracking rates depend on hardware, implementation and candidate generation. That's great for file integrity and terrible for passwords.

| Algorithm | OWASP baseline consulted for this review |
|---|---|
| Argon2id | 19 MiB memory, 2 iterations, parallelism 1 |
| scrypt | N = 2^17, r = 8, p = 1 |
| bcrypt | cost 10+, 72-byte input limit |
| PBKDF2-HMAC-SHA256 | 600,000 iterations |

Prefer Argon2id; OWASP lists scrypt when Argon2id is unavailable, bcrypt mainly for legacy systems, and PBKDF2 for applicable compliance needs. Tune and periodically revisit costs; the table is not a universal deployment prescription.

Python provides scrypt when the build has the required OpenSSL support:

```python
import hashlib, hmac, os

N, R, P = 2**17, 8, 1  # ~128 MiB

def hash_pw(pw: str):
    salt = os.urandom(16)
    h = hashlib.scrypt(
        pw.encode(), salt=salt,
        n=N, r=R, p=P,
        maxmem=2**28)
    return salt, h

def verify(pw, salt, stored):
    h = hashlib.scrypt(
        pw.encode(), salt=salt,
        n=N, r=R, p=P,
        maxmem=2**28)
    return hmac.compare_digest(h, stored)
```

`hmac.compare_digest` avoids content-dependent early exit for same-type, same-length inputs. It does not make the whole login constant-time; type or length differences and other code can still affect timing. In production you'd normally use a maintained library (such as `argon2-cffi`) that stores the parameters with the hash, so you can raise them later and rehash on next login.

### Why slowness matters: a calculation

Suppose an attacker steals a database of 8-character random passwords (about 6.1 × 10^15 possibilities).

- With **unsalted fast SHA-256** at an assumed 10^10 guesses a second, the worst case is 6.1 × 10^15 / 10^10 ≈ 6.1 × 10^5 seconds, about **7 days**, and each candidate digest can be compared against all unsalted hashes using the same scheme. Exhausting this space covers only passwords in the assumed eight-character alphabet.
- With a **salted** hash, the work is repeated **per user**.
- With a **memory-hard** hash tuned so each guess costs, say, 10^4 times more, the same search takes around 190 years per user.

The numbers are illustrative, but the shape is real: distinct salts prevent sharing the same candidate-hash computation across accounts. Total attack cost also depends on targeting, password distribution and stopping rules; it is not universally an exact user-count multiplier. No hardware benchmark is supplied for these illustrative rates.

## Second factors compared

Not all MFA is equal. The question is whether it survives **phishing**.

| Method | Phishing-resistant? | Main weakness |
|---|---|---|
| SMS code | No | SIM swap, relay |
| TOTP app | No | Real-time relay |
| Push approval | No | MFA fatigue |
| Security key / passkey | Yes | Device loss |

**SMS** codes can be intercepted via SIM swap (convincing a carrier to move a number). NIST classes PSTN-based out-of-band verification as *restricted*.

**TOTP** (RFC 6238) derives an output from a shared secret and a time counter. Six digits and a 30-second step are common settings; the RFC recommends the 30-second default rather than fixing every deployment to it. TOTP adds a barrier beyond a reused password, but its output can be relayed to the genuine verifier within the acceptance window.

**Push notifications** can be abused by sending prompt after prompt until a tired user taps Approve; the 2022 Uber breach involved this. **Number matching** (type the number shown on screen) reduces it.

### Why passkeys resist phishing

Passkeys (FIDO2 / WebAuthn) use public-key cryptography:

```
Registration:
 device makes key pair for "bank.com"
 server stores PUBLIC key only

Login:
 server --- challenge ---> browser
 browser checks RP ID and origin
 device signs authenticator data
   + hash of browser client data
 server verifies signature + context
```

The browser checks the relying-party (RP) ID against the calling origin and includes the origin and challenge in client data. The authenticator signs authenticator data plus the client-data hash. The server must verify the signature, challenge, expected origin, RP ID hash and required flags. A phishing origin cannot simply use a bank RP credential through a conforming browser. This resists credential phishing, but does not prevent compromised clients, session theft or weak recovery. Stealing the stored public key does not yield the private key; a broader database compromise may still expose sessions or other secrets.

## Beyond the login form

- **Account recovery** is authentication too, and often the weakest path. If "forgot password" emails a link, email account security is your security.
- **Sessions**: after login, a bearer session token conveys access to an authenticated session. Protect it (HttpOnly, Secure cookies; rotate on login; expire).
- **Step-up authentication**: ask for a fresh factor before high-risk actions, such as changing the payout bank account.
- **Single sign-on (SSO)** centralises authentication through an identity provider using OIDC or SAML, so MFA policy lives in one place.

## Pitfalls

1. **Leaking which usernames exist.** "Wrong password" versus "No such user" lets attackers enumerate accounts. Use one generic message (and similar response times).
2. **Fast hashes, or no salt.** MD5 and SHA-1 password databases are cracked at scale after every breach.
3. **Security questions.** Mother's maiden name is public record.
4. **MFA on login but not recovery.** Attackers take the path without the second factor.
5. **Logging credentials**, as covered in the CIA lesson.

## Key takeaways
- MFA means independent factors from different categories; two passwords are still one factor.
- Entropy formulas apply only to randomly chosen secrets; human-chosen passwords are far weaker than they look.
- NIST 800-63B: length (15+ alone, 8+ with MFA), blocklists, no forced rotation, no composition rules.
- Store passwords with a unique salt and a slow, memory-hard function such as Argon2id or scrypt.
- SMS, TOTP and conventional push approvals are relayable; correctly implemented WebAuthn resists credential phishing through RP and origin binding. Recovery and session attacks remain relevant.

## Further reading
- [NIST SP 800-63B: Authentication and Authenticator Management](https://pages.nist.gov/800-63-4/sp800-63b.html)
- [Password Storage Cheat Sheet — OWASP](https://cheatsheetseries.owasp.org/cheatsheets/Password_Storage_Cheat_Sheet.html)
- [Authentication Cheat Sheet — OWASP](https://cheatsheetseries.owasp.org/cheatsheets/Authentication_Cheat_Sheet.html)
- [WebAuthn — Wikipedia](https://en.wikipedia.org/wiki/WebAuthn)
- [RFC 6238: TOTP](https://www.rfc-editor.org/rfc/rfc6238)
