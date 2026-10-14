---
id: rel-owasp-2025-safe-denial
title: OWASP 2025 and safe denial
level: advanced
minutes: 3
summary: Translate the 2025 risk categories into architectural controls and explicit failure behaviour.
sourceLesson: rel-security
---

The previous units added encryption, identity and secret controls. OWASP’s explicitly versioned 2025 list is a checklist of remaining web risks. A logged-in user must still be authorised for each object, and an unavailable security check needs a deliberate denial policy.

## OWASP Top 10 at a high level

The OWASP Top 10:2025 ranks the most critical web application risks. The categories, in order, with the design-level response for each:

| Risk | Design response |
|---|---|
| A01 Broken Access Control | server-side authZ on every object |
| A02 Security Misconfiguration | hardened defaults, IaC, config scanning |
| A03 Software Supply Chain Failures | pinned, scanned, signed dependencies |
| A04 Cryptographic Failures | TLS everywhere, KMS, strong algorithms |
| A05 Injection | parameterised queries, output encoding |
| A06 Insecure Design | threat modelling at design time |
| A07 Authentication Failures | MFA, rate-limited login, managed IdP |
| A08 Software or Data Integrity Failures | signed artefacts, verified updates |
| A09 Security Logging and Alerting Failures | audit logs, detections that page |
| A10 Mishandling of Exceptional Conditions | fail closed, safe error handling |

What changed from the 2021 list:

- **SSRF** is no longer its own category; it's folded into A01 Broken Access Control.
- **A03** broadens 2021's "Vulnerable and Outdated Components" to the whole software supply chain: build systems, distribution and dependencies.
- **A10** is new: failing open, swallowing errors and leaking detail in error messages.
- A07 and A09 were renamed ("Identification and" dropped; "Monitoring" became "Alerting").

Broken access control is number one: insecure direct object references like `GET /invoices/1234` that don't check the invoice belongs to the caller. The fix is architectural: authorisation enforced in a consistent layer, never just hidden in the UI.

> [!note] Fail closed
> A10 is a reliability lesson as much as a security one. If the authorisation service times out, the safe default is to *deny*, not allow. Decide the failure behaviour of every security check explicitly, because a check that fails open under load is a vulnerability that only appears during incidents.

## Key takeaways

- The 2025 list groups SSRF with Broken Access Control and expands supply-chain coverage.
- Enforce object authorisation server-side and validate unexpected inputs and outputs.
- Design exceptional security conditions to fail closed while preserving safe error handling and useful audit evidence.

## Further reading

- [OWASP Top 10:2025](https://top10.owasp.org/2025/)
- [A01:2025 Broken Access Control (OWASP)](https://top10.owasp.org/2025/A01_2025-Broken_Access_Control/)
- [Secrets management cheat sheet (OWASP)](https://cheatsheetseries.owasp.org/cheatsheets/Secrets_Management_Cheat_Sheet.html)
