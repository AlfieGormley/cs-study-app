---
id: secf-accounting-evidence
title: Accounting and protected audit evidence
level: basic
minutes: 3
sourceLesson: secf-cia-aaa
summary: Record attributable events without recording secrets.
---

AAA separates identity checking, permission decisions and event recording. This unit follows the permission decision into its evidence trail: the records an investigator can use, and the limits of trusting those records.


### Accounting: what happened?

The system records who did what, when and from where. Accounting serves:

- **Detection**: spotting attacks in progress (100 failed logins in a minute).
- **Investigation**: reconstructing an incident afterwards.
- **Attribution and compliance evidence**: recording which account approved a payment.
- **Billing** for metered network access.

Good audit logs are themselves an integrity problem. Forward them promptly to a separately administered collector, ideally with append-only retention. This protects received records against production administrators, but a compromised source can still omit or forge events. Monitor collection failures and corroborate important events with other evidence.

> [!analogy] Real-world analogy: a shop's CCTV recorder
> A shop records its cameras onto a box in the back office. A burglar who reaches the office can take the box, so careful shops also send the footage to an off-site service.
>
> **How it maps:** The cameras are the systems producing log events. The back-office box is logs kept on the production servers, which an attacker with admin rights can delete. Off-site recording is forwarding to a separately administered, append-only collector.
>
> **Where it stops:** Off-site footage still shows only what the cameras saw. An attacker who controls a log source can omit or forge events before they are sent. A log line also names an account, not necessarily the person at the keyboard.

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

> [!note] Scope and evidence
> These are illustrative examples, not a universal ranking of risks. A log entry or signature supports attribution, but whether it is complete or carries legal weight depends on the system, the surrounding evidence and the applicable process.

## Key takeaways
- Record attributable events without recording secrets.
- Separate log administration and monitor failed collection.
- AAA protocols separate authentication, authorisation and accounting.

## Further reading
- [OWASP Logging Cheat Sheet](https://cheatsheetseries.owasp.org/cheatsheets/Logging_Cheat_Sheet.html)
- [RFC 2903: generic AAA architecture](https://www.rfc-editor.org/rfc/rfc2903)
- [RFC 2865: RADIUS](https://www.rfc-editor.org/rfc/rfc2865)
- [RFC 2866: RADIUS accounting](https://www.rfc-editor.org/rfc/rfc2866)
- [RFC 8907: TACACS+](https://www.rfc-editor.org/rfc/rfc8907)
- [RFC 6733: Diameter](https://www.rfc-editor.org/rfc/rfc6733)
