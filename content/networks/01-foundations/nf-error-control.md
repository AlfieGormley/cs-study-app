---
id: nf-error-control
title: Error detection and sliding-window ARQ
level: advanced
minutes: 16
summary: Parity, the Internet checksum and CRCs worked by hand, what each can and can't catch, and the maths of stop-and-wait, Go-Back-N and Selective Repeat, including why sequence numbers limit the window.
---

Physical links can introduce errors through noise, interference or equipment faults. Error rates depend on the link, operating conditions and coding; there is no single Ethernet or wireless rate. A reliability design must consider two distinct functions:
1. **Detect** that a frame was damaged, so it isn't delivered as if it were good.
2. **Recover**, either by fixing the error in place (forward error correction) or by sending the data again (**ARQ**, automatic repeat request).

This lesson covers both halves. The detection codes reappear throughout the stack, and sliding-window ARQ is the skeleton of TCP, which the transport module builds on.

## The idea behind every check

The sender computes a few redundant bits from the data and sends them along. The receiver recomputes them from what arrived. A mismatch means something changed.

How good a code is depends on its **Hamming distance** *d*: the minimum number of bit flips needed to turn one valid codeword into another.

- A code with distance *d* detects any error of up to *d* − 1 bits.
- It can **correct** up to ⌊(*d* − 1) / 2⌋ bits.

For a given worst-case number of bit errors, correction requires a larger minimum distance than detection. These are alternative decoding guarantees; a distance-3 correcting decoder cannot also promise to identify every two-bit error as uncorrectable.

## Parity

One **parity bit** makes the number of 1s even (even parity). Distance is 2, so it catches any single-bit error, and any odd number of flips, but misses every even number. Two flips in a byte cancel out.

A **burst error** spans from the first changed bit to the last; intermediate bits need not all change. Parity misses bursts containing an even number of flips, so it cannot guarantee detection of even a two-bit burst.

## The Internet checksum

IPv4 headers, UDP and TCP use a **16-bit one's complement sum** (RFC 1071): add the data as 16-bit words, fold any carry back into the bottom, and invert.

```python
def inet_checksum(data: bytes) -> int:
    if len(data) % 2:
        data += b"\x00"
    total = 0
    for i in range(0, len(data), 2):
        word = (data[i] << 8) | data[i + 1]
        total += word
        # fold the carry back in
        total = (total & 0xFFFF) + (
            total >> 16)
    return ~total & 0xFFFF

hdr = bytes.fromhex(
    "4500 0073 0000 4000 4011 0000"
    "c0a8 0001 c0a8 00c7")
print(hex(inet_checksum(hdr)))  # 0xb861

a = bytes.fromhex("4500 0073 0000 4000")
b = bytes.fromhex("0000 4500 4000 0073")
print(inet_checksum(a) == inet_checksum(b))
# True
```

The checksum field (bytes 10–11 here) is zero while computing; the sender then writes `b861` into it. The receiver sums the whole header including the checksum, and a correct header gives zero after inversion.

It was chosen because it is **fast in software**: just additions, which can be done 32 or 64 bits at a time and updated incrementally when a router changes the TTL. Its weaknesses follow from addition being commutative:

- **Reordered 16-bit words** give the same sum, as the second example shows.
- Some multi-bit errors cancel, such as one word going up by *x* and another down by *x*.
- A roughly uniform random checksum result suggests an undetected-error probability on the order of 2⁻¹⁶. Structured corruptions, such as word reordering, do not follow that model.

> [!note] Errors the CRC never sees
> Stone and Partridge's study of real traffic (SIGCOMM 2000) found that TCP checksum failures happen far more often than link bit error rates predict. The authors inferred causes including memory and software errors, but could not explain every observed pattern. Corruption introduced after an incoming CRC check and before a new outgoing CRC is computed can pass both link checks. This is the **end-to-end argument**: only a check from source to destination covers the whole path, which is why storage systems and protocols like TLS add their own stronger integrity checks.

## Cyclic redundancy checks

A **CRC** treats the bits as the coefficients of a polynomial over GF(2), arithmetic where addition and subtraction are both XOR and there are no carries. Sender and receiver agree on a **generator** polynomial *G* of degree *r*.

1. Append *r* zeros to the data *D*.
2. Divide by *G* using XOR long division.
3. The *r*-bit remainder *R* is the CRC. Send *D* followed by *R*.
4. The receiver divides everything it got by *G*. A remainder of zero means "no detected error" in this unreflected, zero-initialised model. Real protocols can use other initialisation and final-XOR conventions.

### A worked division

*D* = `101110`, *G* = `1001` (x³ + 1), so *r* = 3. Wherever the leading bit is 1, XOR the generator in beneath it:

```
 101110000   D + three zeros
^1001
 001010000
^  1001
 000011000
^    1001
 000001010
^     1001
 000000011   remainder R = 011
```

The sender transmits `101110 011`. The receiver divides `101110011` by `1001` and gets `000`. If the fourth bit is flipped in transit (`101010011`), the remainder is `100`, not zero, and the frame is dropped.

The same thing in code:

```python
def crc_remainder(data, gen):
    if not data or set(data) - {"0", "1"}:
        raise ValueError("need binary data")
    if (len(gen) < 2 or gen[0] != "1"
            or gen[-1] != "1"
            or set(gen) - {"0", "1"}):
        raise ValueError("bad generator")
    r = len(gen) - 1
    bits = list(data + "0" * r)
    for i in range(len(data)):
        if bits[i] == "1":
            for j, g in enumerate(gen):
                b = bits[i + j]
                bits[i + j] = str(
                    int(b) ^ int(g))
    return "".join(bits[-r:])

print(crc_remainder("101110", "1001"))
# 011
```

### What a CRC guarantees

For a generator of degree *r* ≥ 1 with leading and constant coefficients 1, the CRC detects:

- **All single-bit errors**.
- **All burst errors of length *r* or less**: the span between first and last flipped bits is at most *r*.
- **All odd numbers of bit errors**, if *G* has (x + 1) as a factor.
- For suitably random long error patterns, approximately a 2⁻ʳ fraction are undetected. This is not a guarantee for arbitrary or adversarial errors.

Ethernet's **CRC-32** uses generator `0x04C11DB7` with the x³² term implicit. It detects every burst of up to 32 bits within the protected codeword. Koopman's table gives distance at least 4 through 91,607 data bits (excluding the 32 check bits), and at least 5 through 2,974 data bits. Thus all 1–3-bit errors within the FCS-protected region of ordinary 1518-byte or 9000-byte frames are detected. This excludes preamble/SFD and assumes fixed framing, rather than inserted or deleted bits. Other generators, including CRC-32C, have different guarantees.

### Fast in hardware, fine in software

The division is just a shift register with XOR taps, so NICs can compute CRCs at line rate using hardware resources and power. Software uses a 256-entry lookup table to process a byte at a time, and some CPU instruction sets accelerate particular CRC polynomials; the supported polynomial must match the protocol. Real CRC-32 also has bit-reflection and initial and final XOR conventions, which is why a straight bitwise version looks like this:

```python
import zlib

def crc32(data: bytes) -> int:
    crc = 0xFFFFFFFF
    for byte in data:
        crc ^= byte
        for _ in range(8):
            lsb = crc & 1
            crc >>= 1
            if lsb:
                crc ^= 0xEDB88320
    return crc ^ 0xFFFFFFFF

msg = b"123456789"
print(hex(crc32(msg)))       # 0xcbf43926
print(crc32(msg) == zlib.crc32(msg))  # True
```

`0xEDB88320` is `0x04C11DB7` bit-reversed, and `0xCBF43926` is the standard check value for CRC-32.

> [!warning] A CRC is not a MAC
> A CRC is linear: an attacker who flips some bits can compute exactly how the CRC changes and fix it up, without knowing anything secret. WEP's integrity check was a CRC-32, which is one reason WEP fell. For tamper resistance you need a cryptographic MAC, such as the authentication tag in TLS.

## Recovering: FEC or ARQ?

| | FEC | ARQ |
|---|---|---|
| How | Extra bits fix errors | Resend what was lost |
| Cost | Redundancy and coding work | ACK/state overhead plus retransmissions |
| Latency | Encoding/decoding and possible buffering delay | Loss detection, retransmission and propagation delay |
| Design considerations | Can reduce retries; code and channel determine effectiveness | Feedback delay, loss and retransmission cost matter |

Real systems can combine FEC with retransmission. FEC is not absent from Ethernet: several PHYs use it, including Reed–Solomon coding in high-speed variants. Ordinary Ethernet MAC handling discards invalid-FCS frames without a MAC-level request to resend them; a higher layer may recover, depending on the protocol. FEC can avoid a retransmission round trip, but adds coding work and cannot correct arbitrary damage.

> [!note] Content omitted after review
> Universal bit-error rates and blanket claims about coding or retransmission across all wireless and deep-space links are omitted. Those require a specific standard, mode, mission or measurement that this lesson has not established.

## Stop-and-wait

The simplest ARQ: send one frame, wait for its ACK, then send the next. If no ACK arrives before a timeout, resend. A 1-bit sequence number (alternating 0 and 1) lets the receiver spot a duplicate when the frame arrived but the ACK was lost.

Assume ordered channels, detectable corruption, no arbitrarily delayed duplicates surviving sequence-number reuse, and retry behaviour that eventually permits delivery. For the loss-free timing model, let *L* be the complete frame size, *R* the data-link rate and RTT the round-trip propagation delay, excluding data-frame transmission. Ignore ACK transmission, processing, queueing and framing gaps. The sender is busy for *L*/*R* out of each *L*/*R* + RTT:

```
U = (L/R) / (L/R + RTT)
```

> [!example] Stop-and-wait across a country
> 1 Gbit/s, 30 ms RTT, 1500-byte frames (12,000 bits).
> - *L*/*R* = 12,000 / 10⁹ = 12 µs.
> - U = 0.012 / 30.012 ≈ **0.04%**.
> - Throughput = 12,000 bits / 30.012 ms ≈ **400 kbit/s** on a gigabit link.

## Sliding windows

The fix is **pipelining**: allow up to *N* frames to be outstanding. To keep the link busy the window must cover a full round trip, which is the bandwidth-delay product from lesson 2:

```
U = min(1, N * (L/R) / (L/R + RTT))
N to fill = ceil((L/R + RTT) / (L/R))
```

For the example above, N = 30.012 / 0.012 ≈ **2,501 frames** in flight. Two strategies handle a loss inside that window.

### Go-Back-N

- The receiver accepts frames **only in order**. Anything after a gap is discarded.
- ACKs are **cumulative**: "ACK n" means everything up to n arrived.
- On timeout, the sender retransmits the oldest unacknowledged frame and all later **outstanding** frames in its window.

The receiver is trivial (one expected sequence number, no buffer), but a gap can require retransmission of several already received frames.

```
sender:   0 1 2 3 4 5 | 2 3 4 5
               x lost   ^ timeout: go back
receiver: 0 1 - drop drop drop | 2 3 4 5
```

### Selective Repeat

- The receiver **buffers** out-of-order frames within its window and ACKs each one individually.
- The textbook sender keeps a timer per unacknowledged frame and resends frames whose acknowledgements have not arrived before timeout.
- Buffered frames are delivered upwards once the gap is filled.

It costs memory and bookkeeping on both sides, and it avoids retransmitting correctly acknowledged later frames merely because an earlier frame was lost. Lost ACKs or repeated loss can still cause more retransmissions. TCP uses cumulative byte acknowledgements and can negotiate SACK to report non-contiguous received ranges. Its recovery and congestion-control rules are more complex than these textbook models.

### Window size versus sequence numbers

With *k*-bit sequence numbers, numbers wrap modulo 2ᵏ. Under the ordered-channel and bounded-old-duplicate assumptions above, window limits avoid confusing retransmissions from the outstanding window with new data. Finite sequence numbers alone cannot handle packets delayed across arbitrary numbers of wraps. The table assumes equal sender and receiver windows for Selective Repeat.

| Protocol | Maximum window |
|---|---|
| Go-Back-N | 2ᵏ − 1 |
| Selective Repeat | 2ᵏ⁻¹ |

Why Go-Back-N can't use all 2ᵏ, with *k* = 2 (numbers 0–3) and a window of 4:

1. The sender sends 0, 1, 2, 3. All arrive; the receiver now expects 0 (the next lap).
2. All four ACKs are lost. The sender times out and resends the *old* 0.
3. The receiver, expecting a new 0, accepts the duplicate as fresh data. Silent corruption.

With a window of 3 the receiver would be expecting 3 when the old 0 reappears, and would reject it.

Selective Repeat is stricter because the receiver accepts a whole window of numbers. After receiving 0, 1, 2 with window 3, it accepts {3, 0, 1}. If the ACKs are lost and the sender resends the old 0, it falls inside the new window and is wrongly accepted. Keeping the window at no more than half the sequence space separates the old retransmissions from the next receive window in this scenario.

> [!example] Sizing sequence numbers
> The 2,501-frame window above needs *k* = 12 for Go-Back-N (4,095 ≥ 2,501), but *k* = 13 for Selective Repeat (2¹² = 4,096 ≥ 2,501, whereas 2¹¹ = 2,048 isn't enough). TCP numbers bytes using 32 bits and constrains window sizes; negotiated timestamps support PAWS rejection of old segments. Byte numbering alone does not remove wraparound concerns.

### When errors happen: the maths

If attempts independently fail with probability *p* < 1 and retries continue until success, the geometric distribution gives **1 / (1 − p)** expected attempts. This counts attempts, not elapsed time: timeout and ACK behaviour still matter.

If individual bits flip independently with probability *b*, an *n*-bit frame has at least one flipped bit with probability **p = 1 − (1 − b)ⁿ**, approximately *nb* when *nb* is small. Treating this as frame-loss probability additionally assumes every such frame is rejected; FEC and undetected errors change that mapping.

For a hypothetical uncoded 12,000-bit frame at *b* = 10⁻⁶:

- p ≈ **1.1928%**.
- Expected attempts ≈ **1.0121** under the independent retry model.
- A continuously busy sender retransmitting only failed frames spends a fraction **1 − p ≈ 98.8072%** of frame transmission time on successful attempts. This is an ideal efficiency, not a finite-window throughput prediction.

Go-Back-N also retransmits later outstanding frames discarded after a gap. Its actual goodput depends on timer values, acknowledgements, propagation, window size and the loss process.

MIT's lecture gives an **approximate** Go-Back-N model: choose N to fill the loss-free feedback cycle, set the timeout to N frame times, ignore ACK errors, and charge N transmissions for each failed delivery attempt. Then expected transmissions per delivered frame are **1 + Np/(1 − p)**, giving efficiency **(1 − p)/(1 + (N − 1)p)**. With N = 2,501 and p ≈ 0.0119283 this is about **3.21%**. It is a model of retransmission work, not a universal finite-window or measured-network prediction.

> [!note] Content omitted after review
> Measured protocol-performance comparisons are absent because no link implementation or workload has been benchmarked here. The formulas describe their stated idealised models.

## Key takeaways
- A code with Hamming distance *d* detects *d* − 1 bit errors and corrects ⌊(*d* − 1)/2⌋. These are alternative guarantees for bounded bit flips.
- Parity catches odd numbers of flips only. The Internet checksum is fast to compute in software but misses reordered words and some cancelling errors.
- A CRC of degree *r* is XOR long division. It catches all bursts up to *r* bits; Ethernet's CRC-32 catches every 1–3-bit error within its protected region at the frame lengths discussed here. CRCs are not secure against tampering.
- Corruption between an incoming link check and outgoing check generation can escape both. End-to-end checks are still needed.
- Stop-and-wait utilisation is (L/R) / (L/R + RTT). Pipelining needs a window of about one bandwidth-delay product.
- Go-Back-N resends from the loss onward, with window up to 2ᵏ − 1. Selective Repeat retransmits timed-out unacknowledged frames, with window up to 2ᵏ⁻¹. Selective Repeat avoids retransmitting correctly received later frames solely because of an earlier gap.

## Further reading
- [Cyclic redundancy check — Wikipedia](https://en.wikipedia.org/wiki/Cyclic_redundancy_check)
- [RFC 1071: Computing the Internet Checksum](https://www.rfc-editor.org/rfc/rfc1071)
- [Koopman: Best CRC polynomials](https://users.ece.cmu.edu/~koopman/crc/)
- [Sliding window protocol — Wikipedia](https://en.wikipedia.org/wiki/Sliding_window_protocol)
- [Selective Repeat ARQ — Wikipedia](https://en.wikipedia.org/wiki/Selective_Repeat_ARQ)
- [End-to-end principle — Wikipedia](https://en.wikipedia.org/wiki/End-to-end_principle)

- [Koopman: CRC-32 distance table](https://users.ece.cmu.edu/~koopman/crc/crc32.html)
- [Stone and Partridge: When the CRC and TCP Checksum Disagree](https://conferences.sigcomm.org/sigcomm/2000/conf/paper/sigcomm2000-9-1.pdf)
- [RFC 3366: Advice to Link Designers on Link ARQ](https://www.rfc-editor.org/rfc/rfc3366.html)
- [MIT: ARQ protocols](https://ocw.mit.edu/courses/16-36-communication-systems-engineering-spring-2009/resources/mit16_36s09_lec18/)
