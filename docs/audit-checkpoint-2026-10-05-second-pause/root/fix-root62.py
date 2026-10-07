from pathlib import Path
import json
p=Path('content/networks/01-foundations/nf-error-control.md');s=p.read_text()
def r(a,b):
 global s
 assert a in s,a[:70]
 s=s.replace(a,b)
a=s.index('Every physical link');b=s.index('\n1. **Detect**',a)
s=s[:a]+'Physical links can introduce errors through noise, interference or equipment faults. Error rates depend on the link, operating conditions and coding; there is no single Ethernet or wireless rate. A reliability design must consider two distinct functions:'+s[b:]
r('So detection is cheap, and correction needs much more redundancy. That asymmetry shapes everything below.','For a given worst-case number of bit errors, correction requires a larger minimum distance than detection. These are alternative decoding guarantees; a distance-3 correcting decoder cannot also promise to identify every two-bit error as uncorrectable.')
r('Parity is still used where errors are rare and independent, such as some memory buses and serial lines. Networks see **burst errors** (a spike of noise wiping out several consecutive bits), and parity is hopeless at those.','A **burst error** spans from the first changed bit to the last; intermediate bits need not all change. Parity misses bursts containing an even number of flips, so it cannot guarantee detection of even a two-bit burst.')
r('16 bits means a random corruption slips through about 1 time in 65,536.','A roughly uniform random checksum result suggests an undetected-error probability on the order of 2⁻¹⁶. Structured corruptions, such as word reordering, do not follow that model.')
r("The culprits were bugs and bad memory in hosts, routers and NICs, which corrupt data *after* the link CRC has been checked and recomputed. The link layer can't catch an error introduced inside a router.","The authors inferred causes including memory and software errors, but could not explain every observed pattern. Corruption introduced after an incoming CRC check and before a new outgoing CRC is computed can pass both link checks.")
r('A remainder of zero means "no detected error".','A remainder of zero means "no detected error" in this unreflected, zero-initialised model. Real protocols can use other initialisation and final-XOR conventions.')
r('    r = len(gen) - 1','    if not data or set(data) - {"0", "1"}:\n        raise ValueError("binary data required")\n    if (len(gen) < 2 or gen[0] != "1"\n            or gen[-1] != "1"\n            or set(gen) - {"0", "1"}):\n        raise ValueError("invalid generator")\n    r = len(gen) - 1')
r('With a well-chosen generator of degree *r*, a CRC detects:','For a generator of degree *r* ≥ 1 with leading and constant coefficients 1, the CRC detects:')
r('any run of corruption no longer than the CRC.','the span between first and last flipped bits is at most *r*.')
r('Longer bursts with probability about 1 − 2⁻ʳ.','For suitably random long error patterns, approximately a 2⁻ʳ fraction are undetected. This is not a guarantee for arbitrary or adversarial errors.')
r("Ethernet's **CRC-32** (generator `0x04C11DB7`) therefore catches every burst of up to 32 bits. Philip Koopman's analysis shows it has Hamming distance 4 for messages up to about 91,000 bits, which covers a full-size frame and even a 9000-byte jumbo frame. So any error of 1, 2 or 3 bits anywhere in the frame is guaranteed to be caught. (Distance 5 only holds up to about 3,000 bits.) Other generators do better at particular lengths; iSCSI, SCTP and ext4 use CRC-32C (Castagnoli) instead.","Ethernet's **CRC-32** uses generator `0x04C11DB7` with the x³² term implicit. It detects every burst of up to 32 bits within the protected codeword. Koopman's table gives distance at least 4 through 91,607 data bits (excluding the 32 check bits), and at least 5 through 2,974 data bits. Thus all 1–3-bit errors within the FCS-protected region of ordinary 1518-byte or 9000-byte frames are detected. This excludes preamble/SFD and assumes fixed framing, rather than inserted or deleted bits. Other generators, including CRC-32C, have different guarantees.")
r('NICs compute CRCs at line rate for free.','NICs can compute CRCs at line rate using hardware resources and power.')
r('modern CPUs have instructions for CRC-32C.','some CPU instruction sets accelerate particular CRC polynomials; the supported polynomial must match the protocol.')
r('| Cost | Overhead on every frame | Only when errors happen |','| Cost | Redundancy and coding work | ACK/state overhead plus retransmissions |')
r('| Latency | None added | At least one RTT per loss |','| Latency | Encoding/decoding and possible buffering delay | Loss detection, retransmission and propagation delay |')
r('Real systems mix them. Wi-Fi and 4G/5G use strong FEC (LDPC and similar codes) *and* link-layer retransmission, because radio errors are common and an end-to-end retransmission would be slow. Ethernet does neither: the CRC drops the rare bad frame and TCP recovers. Deep-space links, with RTTs of hours, are almost pure FEC.','Real systems can combine FEC with retransmission. FEC is not absent from Ethernet: several PHYs use it, including Reed–Solomon coding in high-speed variants. Ordinary Ethernet MAC handling discards invalid-FCS frames without a MAC-level request to resend them; a higher layer may recover, depending on the protocol. FEC can avoid a retransmission round trip, but adds coding work and cannot correct arbitrary damage.\n\n> [!note] Content omitted after review\n> Universal bit-error rates and blanket claims about coding or retransmission across all wireless and deep-space links are omitted. Those require a specific standard, mode, mission or measurement that this lesson has not established.')
r('It is correct, and terribly slow on long paths. Let *L* be the frame size, *R* the link rate and RTT the round-trip time. The sender is busy for *L*/*R* out of every *L*/*R* + RTT:','Assume ordered channels, detectable corruption, no arbitrarily delayed duplicates surviving sequence-number reuse, and retry behaviour that eventually permits delivery. For the loss-free timing model, let *L* be the complete frame size, *R* the data-link rate and RTT the round-trip propagation delay, excluding data-frame transmission. Ignore ACK transmission, processing, queueing and framing gaps. The sender is busy for *L*/*R* out of each *L*/*R* + RTT:')
r('N to fill = (L/R + RTT) / (L/R)','N to fill = ceil((L/R + RTT) / (L/R))')
r('On a timeout the sender resends the lost frame **and every frame after it**.','On timeout, the sender retransmits the oldest unacknowledged frame and all later **outstanding** frames in its window.')
r('but one loss costs a whole window of retransmissions.','but a gap can require retransmission of several already received frames.')
r('but a loss costs one retransmission.','and it avoids retransmitting correctly acknowledged later frames merely because an earlier frame was lost. Lost ACKs or repeated loss can still cause more retransmissions.')
r('TCP is a hybrid: cumulative ACKs like Go-Back-N, plus SACK so the sender can resend selectively.','TCP uses cumulative byte acknowledgements and can negotiate SACK to report non-contiguous received ranges. Its recovery and congestion-control rules are more complex than these textbook models.')
r('The window must be small enough that the receiver can never mistake a **retransmitted old frame** for a **new one** with the same number.','Under the ordered-channel and bounded-old-duplicate assumptions above, window limits avoid confusing retransmissions from the outstanding window with new data. Finite sequence numbers alone cannot handle packets delayed across arbitrary numbers of wraps. The table assumes equal sender and receiver windows for Selective Repeat.')
r('means the old and new windows can never overlap.','separates the old retransmissions from the next receive window in this scenario.')
r('TCP sidesteps this by numbering bytes with 32 bits, plus timestamps (PAWS) to reject old segments on very fast links.','TCP numbers bytes using 32 bits and constrains window sizes; negotiated timestamps support PAWS rejection of old segments. Byte numbering alone does not remove wraparound concerns.')
a=s.index('If each frame is lost');b=s.index('\n## Key takeaways',a)
s=s[:a]+'''If attempts independently fail with probability *p* < 1 and retries continue until success, the geometric distribution gives **1 / (1 − p)** expected attempts. This counts attempts, not elapsed time: timeout and ACK behaviour still matter.

If individual bits flip independently with probability *b*, an *n*-bit frame has at least one flipped bit with probability **p = 1 − (1 − b)ⁿ**, approximately *nb* when *nb* is small. Treating this as frame-loss probability additionally assumes every such frame is rejected; FEC and undetected errors change that mapping.

For a hypothetical uncoded 12,000-bit frame at *b* = 10⁻⁶:

- p ≈ **1.1928%**.
- Expected attempts ≈ **1.0121** under the independent retry model.
- A continuously busy sender retransmitting only failed frames spends a fraction **1 − p ≈ 98.8072%** of frame transmission time on successful attempts. This is an ideal efficiency, not a finite-window throughput prediction.

Go-Back-N also retransmits later outstanding frames discarded after a gap. Its actual goodput depends on timer values, acknowledgements, propagation, window size and the loss process.

> [!note] Content omitted after review
> The previous Go-Back-N throughput formula and numerical 3.2% prediction are omitted because their timing and recovery assumptions were not established. No measured protocol-performance comparison is available here; the worked loss trace above shows the retransmission difference directly.
'''+s[b:]
r('Detection is far cheaper than correction.','These are alternative guarantees for bounded bit flips.')
r("Ethernet's CRC-32 catches every 1–3 bit error in any Ethernet frame.","Ethernet's CRC-32 catches every 1–3-bit error within its protected region at the frame lengths discussed here.")
r('Link checks can\'t catch corruption inside routers or hosts.','Corruption between an incoming link check and outgoing check generation can escape both.')
r('Under loss with big windows, Selective Repeat wins by a wide margin.','Selective Repeat avoids retransmitting correctly received later frames solely because of an earlier gap.')
s+='\n- [Koopman: CRC-32 distance table](https://users.ece.cmu.edu/~koopman/crc/crc32.html)\n- [Stone and Partridge: When the CRC and TCP Checksum Disagree](https://conferences.sigcomm.org/sigcomm/2000/conf/paper/sigcomm2000-9-1.pdf)\n- [RFC 3366: Advice to Link Designers on Link ARQ](https://www.rfc-editor.org/rfc/rfc3366.html)\n- [MIT: ARQ protocols](https://ocw.mit.edu/courses/16-36-communication-systems-engineering-spring-2009/resources/mit16_36s09_lec18/)\n'
p.write_text(s)
