---
id: fund-estimation-units
title: Keep units and orders of magnitude straight
level: intermediate
minutes: 5
summary: Convert daily counts, powers of ten and network bits into consistent estimation units.
sourceLesson: fund-estimation
---

Back-of-the-envelope estimation is quick, approximate arithmetic that tells you **which order of magnitude** you're dealing with. Is this one database or a hundred? Gigabytes or petabytes? One server or a fleet?

The goal is not precision. Being within a factor of 2–3 is fine. Being off by 1,000x because you confused MB with GB is not.

## Numbers to memorise

### Powers of ten

Estimates juggle very large numbers, so they are written as powers of ten: 10^3 means 10 × 10 × 10 = 1,000, i.e. a 1 followed by three zeros. Multiplying powers of ten adds the exponents (10^3 × 10^6 = 10^9); dividing subtracts them (10^9 / 10^5 = 10^4). That turns most estimation arithmetic into counting zeros.

```formula
10^3 = 10 × 10 × 10 = 1,000
10^6 = 1,000,000
10^a × 10^b = 10^{a + b}
10^a / 10^b = 10^{a − b}
where
10^3, 10^6: ten to the power 3 and ten to the power 6: that many copies of ten multiplied together, which is a 1 followed by that many zeros
^: "to the power of"; the small raised number (the exponent) counts the tens multiplied together
a, b: any two exponents
In words: a power of ten is a 1 followed by that many zeros; multiplying adds the zeros, dividing takes them away.
```

### Time

```formula
1 day = 86,400 s ≈ 10^5 s
1 month ≈ 2.6 M s ≈ 2.5 × 10^6 s
1 year ≈ 31.5 M s ≈ 3 × 10^7 s
where
day: 24 hours = 24 × 60 × 60 = 86,400 seconds
month: an average month, a twelfth of a 365.25-day year, about 30.4 days
year: 365.25 days
s: second
M: million (10^6)
≈: approximately equal to; rounded to keep the arithmetic easy
In words: a day is about a hundred thousand seconds, a month about two and a half million, and a year about thirty million.
```

A handy shortcut follows: divide a daily count by 86,400 to get an average rate per second.

| Per day | Per second (avg) |
|---|---|
| 1 million | ~12 |
| 10 million | ~120 |
| 100 million | ~1,200 |
| 1 billion | ~12,000 |

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

Network speeds are quoted in bits per second; storage and file sizes in bytes. A byte is 8 bits, so:

```formula
R_B = R_b / 8
1 Gbps / 8 = 125 MB/s
10 Gbps / 8 = 1.25 GB/s
where
R_B: the rate in bytes per second
R_b: the rate in bits per second
Gbps: gigabits per second, 10^9 bits per second
MB/s: megabytes per second, 10^6 bytes per second
GB/s: gigabytes per second, 10^9 bytes per second
MB: megabyte, 1,000,000 bytes
GB: gigabyte, 10^9 bytes
s: second
In words: divide a network speed in bits by 8 to get bytes per second.
```

## Key takeaways
- Estimate the order of magnitude and state what you rounded.
- Daily counts become average per-second rates by dividing by 86,400 seconds.
- Distinguish decimal and binary sizes, and divide bits by eight to obtain bytes.
- Object sizes in the table are illustrative assumptions; measure the records and media you will store.

## Further reading
- [The System Design Primer](https://github.com/donnemartin/system-design-primer)
- [Back-of-the-envelope calculation](https://en.wikipedia.org/wiki/Back-of-the-envelope_calculation)
- [NIST: decimal and binary prefixes](https://physics.nist.gov/cuu/Units/binary.html)
