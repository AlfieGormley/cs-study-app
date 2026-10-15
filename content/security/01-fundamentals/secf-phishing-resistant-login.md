---
id: secf-phishing-resistant-login
title: Phishing-resistant login, sessions and recovery
level: intermediate
minutes: 3
sourceLesson: secf-authentication
summary: TOTP and ordinary push approvals can be relayed or misused.
---

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
- TOTP and ordinary push approvals can be relayed or misused.
- WebAuthn requires correct challenge, origin, RP and signature checks.
- Protect session and recovery paths as well as the login form.

## Further reading
- [W3C WebAuthn Level 2](https://www.w3.org/TR/webauthn-2/)
- [NIST SP 800-63B-4: authentication](https://pages.nist.gov/800-63-4/sp800-63b.html)
- [OWASP Authentication Cheat Sheet](https://cheatsheetseries.owasp.org/cheatsheets/Authentication_Cheat_Sheet.html)
