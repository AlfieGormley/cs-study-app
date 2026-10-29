---
id: ip-ipv4-fragment-sizing
title: How IPv4 fragments a datagram
level: basic
minutes: 4
sourceLesson: ip-ipv4
summary: Explain how MTU, eight-byte offsets and the MF flag let a router split a DF-clear IPv4 datagram.
---

Different links carry different maximum packet sizes. This lesson explains what an IPv4 router does when a datagram is too big for the next link, and how the destination puts the pieces back together.

## Fragmentation

An IP interface's **maximum transmission unit** (MTU) is the largest IP packet it supports without IP fragmentation. Link-specific mechanisms may fragment below IP. Basic Ethernet commonly uses 1,500 bytes. PPPoE plus PPP consumes 8 bytes within its Ethernet payload, giving 1,492 unless larger payload support is negotiated as in RFC 4638. Encapsulation reduces the inner MTU for a fixed outer path MTU.

If a router must forward a datagram bigger than the next link's MTU, IPv4 gives it two choices:

1. **Fragment** it into smaller datagrams, if the **DF** (Don't Fragment) flag is clear.
2. **Drop** it if DF is set, and report ICMP "Fragmentation Needed" when error-generation and rate rules permit.

In ordinary IP forwarding, reassembly is performed at the **destination**, not as a normal transit-router step. Firewalls/NATs may track or reassemble fragments for their separate functions, and a tunnel endpoint is the destination of the outer packet. Each fragment has its own IP header; option-copy rules mean not every option appears in every fragment. Fragments share the same **Identification field** value, carry an **offset** in 8-byte units and have **MF** set unless they contain the end of the original payload.

Fragment sizes follow from one constraint. The offset field counts in 8-byte units, so every fragment except the last must carry a multiple of 8 bytes of data. A router therefore fills each non-final fragment with as much data as fits after the header, rounded down to a multiple of 8, and writes each fragment's starting position divided by 8 into the offset field.

> [!example] Fragmenting 4,000 bytes over a 1,500-byte link
> A datagram has a 20-byte header and 3,980 bytes of data. Each fragment can carry 1,500 − 20 = 1,480 bytes of payload, which is already a multiple of 8.
>
> - Fragment 1: 1,480 bytes, offset 0, MF set
> - Fragment 2: 1,480 bytes, offset 185 (byte 1,480 ÷ 8), MF set
> - Fragment 3: 1,020 bytes, offset 370 (byte 2,960 ÷ 8), MF clear
>
> Check: 1,480 + 1,480 + 1,020 = 3,980. Total lengths on the wire are 1,500, 1,500 and 1,040.

The rounding matters when the room left is not a multiple of 8. An MTU of 1,000 leaves 980 bytes after a 20-byte header, but a non-final fragment can only use 976: a second fragment starting at byte 980 would need an offset of 122.5, which the field cannot express.

The destination collects fragments with the same source, destination, protocol and Identification, places each one at its offset, and knows it has the end when it sees a fragment with MF clear. Only when every gap is filled can it hand the datagram up.

> [!analogy] Real-world analogy: Splitting a delivery across vans
> A removal firm has more boxes than one van can carry, so it loads several vans. Every van carries the same job number, a note saying where its boxes go in the sequence, and all but the last say "more vans coming". Only the destination house unpacks and reassembles the full load.
>
> **How it maps:** The job number is the Identification field, the sequence note is the fragment offset, "more vans coming" is the MF flag, and each van's own paperwork is the per-fragment IP header. Intermediate depots (routers) move vans without unpacking them.
>
> **Where it stops:** A real firm would resend one missing van. IP does not: if any fragment is lost, the whole datagram is abandoned and any recovery is left to TCP or the application. And unlike boxes, fragment payloads must be cut on 8-byte boundaries.

## Key takeaways
- Each fragment has an IP header; ordinary transit routers leave reassembly to the destination.
- Non-final fragment payloads must be multiples of eight bytes.
- Offsets count eight-byte units; MF is clear on the piece containing the payload end.
- The destination reassembles by Identification and offset; losing one fragment loses the datagram.

## Further reading
- [RFC 791: Internet Protocol](https://www.rfc-editor.org/rfc/rfc791)
- [RFC 8900: IP fragmentation fragility](https://www.rfc-editor.org/rfc/rfc8900.html)
- [RFC 6864: IPv4 Identification](https://www.rfc-editor.org/rfc/rfc6864)
