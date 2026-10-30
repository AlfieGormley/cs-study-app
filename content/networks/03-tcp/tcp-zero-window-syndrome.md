---
id: tcp-zero-window-syndrome
sourceLesson: tcp-flow-control
title: Zero windows, persist probes and tiny windows
level: intermediate
minutes: 3
summary: What happens when the receiver's buffer fills, how persist probes avoid deadlock, and how to avoid tiny segments.
---

## Zero windows and the persist timer

When the receiver's buffer fills, it advertises a **zero window**: a window field of 0. The sender stops.

Later the application reads, and the receiver sends a **window update**. But that update is a pure ACK carrying no data, and TCP doesn't retransmit pure ACKs. If it is lost, the sender waits for a window to open and the receiver waits for data: **deadlock**.

The fix is the **persist timer**. With data awaiting transmission against a zero window, the sender uses **zero-window probes** to solicit the current window. Probe segment construction depends on the implementation; it should not be confused with permission for unrestricted out-of-window data. The receiver must reply with an ACK carrying its current window, so a delivered probe/reply exchange can reveal the reopened window. Continued loss or endpoint failure can still prevent progress. Probes back off exponentially, like retransmissions.

> [!analogy] Real-world analogy: A full warehouse and a lost "send more" message
> A warehouse tells its supplier "we're full, stop delivering". Later it clears space and emails "send more", but the email goes astray. The supplier waits for the go-ahead; the warehouse waits for lorries. Nothing moves until the supplier rings now and then to ask "any room yet?", and the answer restarts deliveries.
>
> **How it maps:** "We're full" is a zero window; the lost email is a lost window update, a pure ACK that TCP never retransmits; the supplier's periodic call is the persist timer's zero-window probe, and the reply carries the current window.
>
> **Where it stops:** The supplier would ring at a steady pace, whereas TCP backs its probes off exponentially. And the probe and its reply are ordinary TCP segments that can themselves be lost, so progress still depends on some of them getting through.

In `ss -ti` or a packet capture, repeated zero windows show a receiver-side flow-control restriction. Check application reads, memory pressure, socket policy and reassembly state; the capture alone does not uniquely identify a slow application or exclude concurrent network problems.

## Silly window syndrome

If a receiver advertises a window as soon as a few bytes free up, and a sender fills it immediately, the connection degenerates into tiny segments: 40 bytes of IPv4 and TCP headers carrying, say, 10 bytes of data, so four-fifths of what crosses the wire is overhead. That is **silly window syndrome**, and there are fixes on both sides:

- **Receiver** (Clark's algorithm): don't advertise a larger window until it can grow by at least one MSS or half the buffer, whichever is smaller. With a 1,460-byte MSS and a 64 KiB buffer, that means waiting until a full segment's worth of space has freed up.
- **Sender**: don't send tiny segments when you could wait and send a full one. That leads to Nagle.

## Key takeaways

- A zero window stops ordinary new-data sending; persist probes can recover a lost window update when replies get through.
- Repeated zero windows identify a receive-side restriction without uniquely proving its cause.
- Receiver window-update thresholds and sender batching avoid wasteful tiny-segment patterns.

## Further reading

- [RFC 1122: Requirements for Internet Hosts](https://www.rfc-editor.org/rfc/rfc1122)
