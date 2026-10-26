---
id: fund-estimation-units
title: Keep units and orders of magnitude straight
level: intermediate
minutes: 4
summary: Convert daily counts, powers of ten and network bits into consistent estimation units.
sourceLesson: fund-estimation
---

Back-of-the-envelope estimation is quick, approximate arithmetic that tells you **which order of magnitude** you're dealing with. Is this one database or a hundred? Gigabytes or petabytes? One server or a fleet?

The goal is not precision. Being within a factor of 2–3 is fine. Being off by 1,000x because you confused MB with GB is not.

## Reference units, not a memory test

### Large counts and time

Use thousand, million and billion consistently. Moving between decimal size prefixes changes the scale by a thousand each step. Write the units beside estimates so a missed prefix is visible.

For daily counts, a day contains 86,400 seconds. Dividing a count per day by that duration gives an **average** per-second rate, not the busiest-second demand. A 365.25-day year contains about 31.6 million seconds; rounded estimates should say which convention they use.

| Daily events | Average events/s |
|---|---|
| 1 million | About 12 |
| 10 million | About 120 |
| 100 million | About 1,200 |
| 1 billion | About 12,000 |

Use these as a scale check, then allow for the measured traffic peak.

### Size

| Unit | Bytes | In words |
|---|---|---|
| KB (kilobyte) | 1,000 | thousand |
| MB (megabyte) | 1,000,000 | million |
| GB (gigabyte) | 10 to the power 9 | billion |
| TB (terabyte) | 10 to the power 12 | trillion |
| PB (petabyte) | 10 to the power 15 | quadrillion |

Each step up the table is 1,000 times bigger. (Using powers of 10 rather than powers of 2 introduces an error of about 2% at KB, growing to about 13% at PB: a binary kilobyte is 1,024 bytes, 2.4% more than 1,000. That's fine for estimates. Strictly, the binary units are KiB, MiB, GiB and so on.)

### Illustrative object-size assumptions

These are exercise inputs, not measured universal sizes. Content gap: no representative dataset is provided for a reliable generic object-size table; measure your own serialized records and media.

| Item | Assumed size |
|---|---|
| ID / timestamp | 8 bytes |
| Short text post + metadata | 300 B – 1 KB |
| User profile row | 1 KB |
| Compressed photo | 200 KB – 2 MB |
| 1 minute of HD video | ~40–100 MB |

### Bandwidth

Network speeds are quoted in bits per second; storage and file sizes in bytes.

A byte contains **eight bits**. A 1 Gbps link therefore has a raw rate equivalent to 125 MB/s, and a 10 Gbps link to 1.25 GB/s. Application throughput is lower once protocol overhead and other limits are included. A claim that a 10 Gbps link sends 10 GB/s confuses bits with bytes.

## Key takeaways
- Estimate the order of magnitude and state what you rounded.
- Daily counts become average per-second rates by dividing by 86,400 seconds.
- Distinguish decimal and binary sizes, and divide bits by eight to obtain bytes.
- Object sizes in the table are illustrative assumptions; measure the records and media you will store.

## Further reading
- [The System Design Primer](https://github.com/donnemartin/system-design-primer)
- [Back-of-the-envelope calculation](https://en.wikipedia.org/wiki/Back-of-the-envelope_calculation)
- [NIST: decimal and binary prefixes](https://physics.nist.gov/cuu/Units/binary.html)
