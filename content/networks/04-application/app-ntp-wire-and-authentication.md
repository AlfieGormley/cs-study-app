---
id: app-ntp-wire-and-authentication
title: "NTP timestamp fields, eras and authentication"
level: advanced
minutes: 3
sourceLesson: app-ntp-ssh-grpc
summary: "NTP timestamps split seconds and fractions into 32-bit fields, so era context matters when the seconds count rolls over in 2036."
---

### Wire format and security

The basic NTP header is 48 bytes (extensions/authentication can add bytes): leap indicator, version, mode, stratum, poll, precision, root delay and dispersion, reference ID, then four 64-bit timestamps. Each timestamp is 32 bits of seconds since **1 January 1900** and 32 bits of fraction. The fraction splits each second into about 4.3 billion steps of roughly 233 picoseconds, far finer than any real clock or network measurement. The seconds count holds about 136 years, so it rolls back to zero in **February 2036**. Era-aware implementations use other date information, which RFC 5905 says can come from external means such as the file system or dedicated hardware, to decide which 136-year era a timestamp belongs to; the 32-bit field alone cannot.

> [!analogy] Real-world analogy: Two-digit years
> A form that records only the last two digits of the year cannot say whether "36" means 1936 or 2036. People resolve it from context: a birth date on a new passport application is unlikely to be 2036.
>
> **How it maps:** NTP's 32-bit seconds field is the two-digit year: it repeats every 136 years. The "context" is the era an implementation infers from other time information it already has.
>
> **Where it stops:** People fix two-digit years by writing four digits; NTPv4 keeps the 32-bit on-wire field and relies on era handling, so a device with no idea of the current date, such as one whose clock reset to zero, can still pick the wrong era.

Plain NTP is unauthenticated, so an on-path attacker can shift your clock and, for example, make expired certificates look valid. **NTS** (Network Time Security, [RFC 8915](https://www.rfc-editor.org/rfc/rfc8915)) uses TLS key establishment (TCP port 4460), then protects NTP exchanges with negotiated AEAD keys and authenticators. Opaque cookies carry server state; they are not themselves the per-packet integrity check. Authentication does not prevent an on-path attacker from delaying valid packets.

Legacy ntpd's unauthenticated `monlist` response could amplify spoofed requests, documented as CVE-2013-5211. Exposure depends on implementation, version and access controls.

**PTP** (IEEE 1588) can achieve sub-microsecond synchronisation in appropriately engineered networks. Hardware timestamping and PTP-aware transparent clocks reduce timestamp and switch-residence errors; the protocol name alone does not guarantee a particular accuracy.

## Key takeaways
- NTP timestamps split seconds and fractions into 32-bit fields, so era context matters when the seconds count rolls over in 2036.
- NTS authenticates exchanges but cannot stop an on-path attacker delaying valid packets.

## Further reading
- [RFC 5905](https://www.rfc-editor.org/rfc/rfc5905)
- [RFC 8915](https://www.rfc-editor.org/rfc/rfc8915)
- [NTP amplification advisory](https://www.cisa.gov/news-events/alerts/2014/01/13/ntp-amplification-attacks-using-cve-2013-5211)
