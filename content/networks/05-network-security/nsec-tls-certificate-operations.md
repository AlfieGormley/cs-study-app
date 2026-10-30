---
id: nsec-tls-certificate-operations
title: Revocation, renewal and verified TLS clients
level: intermediate
minutes: 4
summary: Revocation mechanisms and client failure policy vary.
sourceLesson: nsec-tls
---

Certificate trust must survive routine operations as well as the first connection. This unit covers leaked keys, validity limits and a Python client that keeps chain and hostname verification enabled.

### Revocation and short lifetimes

If a private key leaks, the certificate must be **revoked**. The two classic mechanisms are **CRLs** (lists of revoked serial numbers) and **OCSP** (ask the CA about one certificate). Direct OCSP requests can reveal certificate lookups to the responder. Some clients **soft-fail** when status cannot be retrieved; others use different revocation mechanisms or policies. Blocking a responder can therefore undermine a soft-fail check. **OCSP stapling** lets the server attach a recent signed OCSP response itself.

The industry's answer has shifted to **short-lived certificates**. Since March 2024 the CA/Browser Forum Baseline Requirements have required CAs to publish CRLs while making OCSP optional, and Let's Encrypt turned off its OCSP service in August 2025, publishing revocation only through CRLs. The Baseline Requirements also cut the maximum lifetime of publicly trusted TLS server certificates on a fixed schedule, applied by issue date:

| Certificate issued | Maximum validity |
|---|---|
| Before 15 March 2026 | 398 days |
| 15 March 2026 to 14 March 2027 | 200 days |
| 15 March 2027 to 14 March 2029 | 100 days |
| From 15 March 2029 | 47 days |

(Schedule as published in Baseline Requirements version 2.3.1, checked October 2026; check the current version, because ballots can change it.) After each date a publicly trusted CA must not issue a longer certificate; certificates already issued keep their original expiry. Short lifetimes limit how long an unrevoked stolen key stays useful, and they make reliable renewal and expiry monitoring more demanding. **Automated renewal** (for example ACME) is the practical response: a once-a-year manual process cannot keep up with a 100-day or 47-day maximum.

> [!analogy] Real-world analogy: cancelled bank cards and short expiry dates
> When a bank card is stolen, a shop can check a printed list of cancelled card numbers, or phone the bank about one card. Both can fail: the list may be out of date, and if the phone line is down the shop must decide whether to accept the card anyway. Cards that expire after a few weeks limit the damage even when the check fails.
>
> **How it maps:** The printed list is a CRL, the phone call is an OCSP query (which tells the bank which card is being used, just as OCSP tells a CA which site is being checked), accepting the card when the line is down is soft-fail, and short expiry is a short-lived certificate.
>
> **Where it stops:** Certificates are checked by software automatically on every connection, and certificate holders must renew far more often than cardholders replace cards, so automation is essential. A short-lived certificate also does not stop misuse of a stolen key before it expires.

Checking a server by hand:

```python
import socket, ssl

host = "www.rfc-editor.org"

# Load trusted CAs; keep peer checks on.
ctx = ssl.create_default_context()

with socket.create_connection(
        (host, 443), timeout=10) as raw:
    # SNI also supplies the name to verify.
    with ctx.wrap_socket(
            raw,
            server_hostname=host) as tls:
        # Describe this live connection.
        print(tls.version())
        print(tls.cipher()[0])
        cert = tls.getpeercert()
        # Flatten the subject entries.
        subject = dict(
            x[0] for x in cert["subject"])
        print(subject)
```

The negotiated version, cipher and certificate subject depend on the live endpoint and local TLS stack; no fixed output is guaranteed. `create_default_context()` turns on chain and hostname verification; passing `server_hostname` sets SNI and the name to check. Code that sets `verify=False` (in `requests`) or `CERT_NONE` throws all of that away and is open to any MITM.

## Key takeaways
- Revocation mechanisms and client failure policy vary.
- The public certificate lifetime schedule makes reliable renewal and monitoring valuable.
- Use a verified TLS context and an explicit server name; live outputs are environment dependent.

## Further reading
- [CA/Browser Forum Baseline Requirements (TLS server certificates)](https://cabforum.org/working-groups/server/baseline-requirements/requirements/)
- [OCSP service has reached end of life — Let's Encrypt](https://letsencrypt.org/2025/08/06/ocsp-service-has-reached-end-of-life/)
- [RFC 6960: Online Certificate Status Protocol (OCSP)](https://www.rfc-editor.org/rfc/rfc6960)
- [ssl: TLS/SSL wrapper for socket objects — Python docs](https://docs.python.org/3/library/ssl.html)
