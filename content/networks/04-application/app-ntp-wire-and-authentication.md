---
id: app-ntp-wire-and-authentication
title: "NTP timestamp fields, eras and authentication"
level: advanced
minutes: 3
sourceLesson: app-ntp-ssh-grpc
summary: "NTP timestamps split seconds and fractions into 32-bit fields, so era context matters at wraparound."
---

### Wire format and security

The basic NTP header is 48 bytes (extensions/authentication can add bytes): leap indicator, version, mode, stratum, poll, precision, root delay and dispersion, reference ID, then four 64-bit timestamps. Each timestamp is 32 bits of seconds since **1 January 1900** and 32 bits of fraction. Both limits follow from the field width:

```formula
r = 1 s / 2^32 ≈ 2.33 × 10^{−10} s ≈ 233 ps
W = 2^32 s ≈ 4.29 × 10^9 s ≈ 136 yr
where
r: the resolution: the smallest time step the 32-bit fraction can represent
W: how long the 32-bit seconds count lasts before it wraps back to zero
^: "to the power of"; 2^32 = 4,294,967,296
≈: approximately equal to
s: seconds
ps: picoseconds, trillionths (10^{−12}) of a second
yr: years; one year is about 31.6 million seconds
In words: splitting a second into 2^32 steps gives steps of about 233 picoseconds, and counting 2^32 whole seconds from 1900 runs out after about 136 years.
```

So the seconds field wraps in **February 2036**; era-aware implementations use contextual date information to disambiguate it. Correct era handling is not guaranteed by the 32-bit field alone.

Plain NTP is unauthenticated, so an on-path attacker can shift your clock and, for example, make expired certificates look valid. **NTS** (Network Time Security, [RFC 8915](https://www.rfc-editor.org/rfc/rfc8915)) uses TLS key establishment (TCP port 4460), then protects NTP exchanges with negotiated AEAD keys and authenticators. Opaque cookies carry server state; they are not themselves the per-packet integrity check. Authentication does not prevent an on-path attacker from delaying valid packets.

Legacy ntpd's unauthenticated `monlist` response could amplify spoofed requests, documented as CVE-2013-5211. Exposure depends on implementation, version and access controls. A universal amplification ratio and present-day deployment prevalence are omitted because this review did not establish reliable measurements.

**PTP** (IEEE 1588) can achieve sub-microsecond synchronisation in appropriately engineered networks. Hardware timestamping and PTP-aware transparent clocks reduce timestamp and switch-residence errors; the protocol name alone does not guarantee a particular accuracy.

## Key takeaways
- NTP timestamps split seconds and fractions into 32-bit fields, so era context matters at wraparound.
- NTS authenticates exchanges but cannot stop an on-path attacker delaying valid packets.

## Further reading
- [RFC 5905](https://www.rfc-editor.org/rfc/rfc5905)
- [RFC 8915](https://www.rfc-editor.org/rfc/rfc8915)
- [NTP amplification advisory](https://www.cisa.gov/news-events/alerts/2014/01/13/ntp-amplification-attacks-using-cve-2013-5211)
