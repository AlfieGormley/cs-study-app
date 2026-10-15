---
id: nsec-tls-certificate-operations
title: Revocation, renewal and verified TLS clients
level: intermediate
minutes: 3
summary: Revocation mechanisms and client failure policy vary.
sourceLesson: nsec-tls
---

Certificate trust must survive routine operations as well as the first connection. This unit covers leaked keys, validity limits and a Python client that keeps chain and hostname verification enabled.

### Revocation and short lifetimes

If a private key leaks, the certificate must be **revoked**. The two classic mechanisms are **CRLs** (lists of revoked serial numbers) and **OCSP** (ask the CA about one certificate). Direct OCSP requests can reveal certificate lookups to the responder. Some clients **soft-fail** when status cannot be retrieved; others use different revocation mechanisms or policies. Blocking a responder can therefore undermine a soft-fail check. **OCSP stapling** lets the server attach a recent signed OCSP response itself.

The industry's answer has shifted to **short-lived certificates**. Let's Encrypt shut down its OCSP service in 2025 in favour of CRLs. The CA/Browser Forum has cut the maximum lifetime of public certificates from 398 days to 200 days (from March 2026), falling to 100 days in 2027 and 47 days in 2029. Short lifetimes limit the damage of an unrevoked key, and make reliable renewal and monitoring more demanding. **Automated renewal** (for example ACME) is a practical approach, not a mathematical requirement imposed by the lifetime alone.

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
- [RFC 9846: TLS 1.3 (2026 revision)](https://www.rfc-editor.org/rfc/rfc9846.html)
- [RFC 8446: original TLS 1.3 specification](https://www.rfc-editor.org/rfc/rfc8446)
- [The Illustrated TLS 1.3 Connection](https://tls13.xargs.org/)
- [RFC 9849: TLS Encrypted Client Hello](https://www.rfc-editor.org/rfc/rfc9849.html)
- [Ballot SC081v3: reducing certificate validity periods — CA/Browser Forum](https://cabforum.org/2025/04/11/ballot-sc081v3-introduce-schedule-of-reducing-validity-and-data-reuse-periods/)
- [Certificate Transparency — MDN](https://developer.mozilla.org/en-US/docs/Web/Security/Certificate_Transparency)
- [ssl: TLS/SSL wrapper for socket objects — Python docs](https://docs.python.org/3/library/ssl.html)
