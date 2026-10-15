---
id: fs-raid-rebuild-risk
title: Rebuild bandwidth and error assumptions
level: advanced
minutes: 5
summary: Rebuild duration depends on the real bottleneck and how much must be read.
sourceLesson: fs-storage-devices
---

This unit focuses on rebuild bandwidth and error assumptions. The preceding units provide the file and storage concepts used here.

### Rebuilds and unrecoverable read errors

When one disk in a RAID 5 dies, the array is running with no redundancy until the rebuild finishes, and a conventional full-device rebuild reconstructs the failed member by reading the corresponding allocated array stripes on surviving members. Optimized/partial rebuilds and filesystem-aware layouts can skip unused or known-clean ranges.

Device specifications can state nonrecoverable-read-error limits over bits read, an unrecoverable read error (URE) being a sector the drive cannot read back. Such a limit is not, by itself, an observed independent per-bit probability model. For unit conversion, 10¹⁴ bits equals 12.5 TB.

Rebuilding a 4 × 16 TB RAID 5 after one failure means reading the three survivors in full. Purely as a mathematical scenario, suppose read errors arrive independently at random, which is a **Poisson model**: then the chance of reading everything with no error falls exponentially with the expected number of errors.

```formula
b = 3 × 16 TB × (8 bit/B)
b = 3.84 × 10^14 bit
q = 10^{−14} /bit
λ = bq = 3.84
P_none = e^{−λ}
P_none = e^{−3.84} ≈ 0.0215 = 2.15%
where
b: the number of bits the rebuild reads: three surviving 16 TB disks, times 8 bits per byte
TB: terabyte, 10^12 bytes
B: byte, eight bits
bit: one binary digit, used here to count the bits read
λ: lambda, the expected (average) number of read errors during the rebuild
q: the assumed error rate per bit read; here 1 per 10^14 bits = 10^−14
P_none: the probability of zero errors over the whole rebuild
e: Euler's number, about 2.718; e^{−λ} is the Poisson probability of no events when λ are expected
≈: approximately equal to
%: per cent, hundredths
In words: if errors strike at random at 1 per 10^14 bits, reading 3.84 × 10^14 bits expects 3.84 errors, and the chance of none at all is only about 2%.
```

A datasheet limit alone does not justify this distribution, and no empirical rebuild-failure probability follows without measured error behavior and rebuild details. The rebuild also takes a long time, which is how long the array runs with no redundancy:

```formula
t = V / R
t_1 = 16 × 10^12 B / (150 × 10^6 B/s)
t_1 ≈ 106,700 s ≈ 29.6 h
t_2 = 48 × 10^12 B / (150 × 10^6 B/s)
t_2 = 320,000 s ≈ 88.9 h
where
t: the rebuild time, ignoring overhead
V: the bytes that must move through one bottleneck, in bytes (B)
R: the rate of that bottleneck, in bytes per second (B/s); here 150 MB/s
t_1: the time if each disk streams 150 MB/s in parallel, so the 16 TB written to the replacement sets the pace
t_2: the time if 150 MB/s is the whole array's read bandwidth, shared by all 48 TB read
B: byte
s: second
h: hour, 3,600 s
≈: approximately equal to
In words: even streaming flat out, a 16 TB rebuild takes more than a day, and up to almost four days if the 48 TB of reads share one 150 MB/s pipe.
```

Another complete member failure in that window exceeds RAID 5 redundancy, while a URE can affect a stripe or abort recovery depending on implementation.

That is why large-capacity arrays use RAID 6, RAID-Z2/Z3 or mirrors, and why big storage systems (Ceph, HDFS, S3) replicate or erasure-code across machines instead.

Last pitfalls:

- **RAID is not a backup.** It faithfully replicates `rm -rf`, ransomware and file system corruption.
- **Correlated failures matter.** Shared environment, age, firmware and workload can invalidate independence assumptions; this does not establish that a particular batch will fail together.
- **RAID 0 multiplies risk.** A member failure can make a striped RAID0 volume unusable even though some surviving sectors remain readable. With independent, equal and small per-disk failure probabilities, the array's risk grows almost in proportion to the number of disks (the formula follows this list); correlation and repair alter reliability models.

The RAID 0 risk comes from requiring every disk to survive:

```formula
F = 1 − (1 − p)^N
F ≈ Np   for p ≪ 1
F = 1 − (1 − 0.01)^4 ≈ 0.039 ≈ 4 × 0.01
where
F: the probability that the RAID 0 array fails during the chosen interval (any one member failing loses it)
p: the probability that one disk fails during that interval, assumed independent and equal for every disk; here an illustrative 0.01 (1%)
N: the number of disks in the array; here 4
≪: much less than; the shortcut F ≈ N × p only holds when p is tiny
≈: approximately equal to
In words: the array survives only if all N disks survive, so with small risks the chance of losing it is about N times the risk for one disk: four disks, four times the risk.
```

## Key takeaways
- Rebuild duration depends on the real bottleneck and how much must be read.
- A datasheet error limit does not establish an independent Poisson failure model; RAID is not a backup.

## Further reading
- [OSTEP: Hard Disk Drives (PDF)](https://pages.cs.wisc.edu/~remzi/OSTEP/file-disks.pdf)
- [OSTEP: Flash-based SSDs (PDF)](https://pages.cs.wisc.edu/~remzi/OSTEP/file-ssd.pdf)
- [OSTEP: Redundant Arrays of Inexpensive Disks (PDF)](https://pages.cs.wisc.edu/~remzi/OSTEP/file-raid.pdf)
- [Write amplification — Wikipedia](https://en.wikipedia.org/wiki/Write_amplification)
- [NVM Express — Wikipedia](https://en.wikipedia.org/wiki/NVM_Express)
- [Standard RAID levels — Wikipedia](https://en.wikipedia.org/wiki/Standard_RAID_levels)
- [RAID arrays (md) — Linux kernel documentation](https://docs.kernel.org/admin-guide/md.html)
- [Backblaze hard drive test data](https://www.backblaze.com/cloud-storage/resources/hard-drive-test-data)
