---
id: nsec-ipsec-replay-window
title: Tracking authenticated packet replays
level: advanced
minutes: 4
summary: A replay window accepts unseen recent packets while rejecting duplicates and stale counters.
sourceLesson: nsec-vpns
---

IPsec sequence numbers protect against replay only when the receiver tracks which authenticated packets it already accepted. Reordering makes a bounded window more useful than requiring one strictly consecutive counter.

### Anti-replay

Each ESP packet carries a sequence number. The receiver keeps an **anti-replay window** (RFC 4303 recommends 64 packets) so that it tolerates packets arriving slightly out of order but rejects duplicates and anything too old. WireGuard and DTLS use the same idea.

The receiver accepts an authenticated packet only when both conditions on the first line hold, and then updates its highest-seen number:

```formula
s > s_top − W   and   s ∉ S
s_new = max(s_top, s)
where
s: the sequence number of the arriving packet
s_top: the highest sequence number accepted so far
W: the replay-window width, in packets; RFC 4303 recommends 64
S: the set of sequence numbers already accepted inside the window
∉: "is not a member of": s has not been accepted before
s_new: the highest accepted sequence number after this packet
max: the larger of the two values
In words: a packet is accepted only if it is newer than the bottom of the window and has not been seen before; a new highest number slides the window forward.
```

For example, a four-packet window with highest accepted sequence number five covers sequence numbers two through five. Packet three is accepted if unseen; packet one is stale; packet nine is accepted and moves the highest accepted number to nine.

```python
class ReplayWindow:
    def __init__(self, size):
        if (type(size) is not int
                or size < 1):
            raise ValueError("size > 0")
        self.size = size
        self.top = 0       # highest seen
        self.seen = set()  # seqs in window

    def accept(self, seq):
        if type(seq) is not int or seq < 1:
            return False
        if seq <= self.top - self.size:
            return False   # too old
        if seq in self.seen:
            return False   # duplicate
        # Already authenticated by caller.
        self.seen.add(seq)
        self.top = max(self.top, seq)
        low = self.top - self.size
        # Prune values outside the window.
        self.seen = {s for s in self.seen
                     if s > low}
        return True

w = ReplayWindow(4)
# Trace gaps and duplicates.
for seq in [1, 2, 5, 3, 5, 1, 9, 6]:
    print(seq, w.accept(seq))
```

Trace it with a window of 4:

| seq | top before | Result | Why |
|---|---|---|---|
| 1, 2, 5 | 0, 1, 2 | accept | new |
| 3 | 5 | accept | recent and unseen |
| 5 | 5 | reject | duplicate |
| 1 | 5 | reject | below current window |
| 9 | 5 | accept | new top |
| 6 | 9 | accept | recent and unseen |

This toy handles already authenticated positive sequence numbers for one SA, without wrapping. Never update replay state before integrity verification: a forged high counter could otherwise evict legitimate packets. Its set pruning takes time proportional to the replay-window width for every accepted packet. Efficient implementations can use bitmaps. The replay-window width is a trade-off: too small and legitimate reordering (common with multi-core senders or ECMP paths) causes drops; too large costs memory per SA.

## Key takeaways
- A replay window accepts unseen recent packets while rejecting duplicates and stale counters.
- Authenticate packets before changing replay state.
- The teaching set model omits counter wrapping and costs work proportional to its window.

## Further reading
- [RFC 4301: Security Architecture for the Internet Protocol](https://www.rfc-editor.org/rfc/rfc4301)
- [RFC 4303: IP Encapsulating Security Payload (ESP)](https://www.rfc-editor.org/rfc/rfc4303)
- [WireGuard: Next Generation Kernel Network Tunnel (whitepaper)](https://www.wireguard.com/papers/wireguard.pdf)
- [WireGuard: protocol and cryptography](https://www.wireguard.com/protocol/)
- [RFC 7348: Virtual eXtensible Local Area Network (VXLAN)](https://www.rfc-editor.org/rfc/rfc7348)
- [RFC 4459: MTU and Fragmentation Issues with In-the-Network Tunneling](https://www.rfc-editor.org/rfc/rfc4459)
