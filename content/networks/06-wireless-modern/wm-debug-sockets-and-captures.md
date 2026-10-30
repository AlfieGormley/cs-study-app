---
id: wm-debug-sockets-and-captures
title: Socket counters and packet-capture hypotheses
level: advanced
minutes: 3
summary: Socket queues, recovery counters and receive-window adverts describe different constraints.
sourceLesson: wm-debugging
---

When higher-level tools disagree, the kernel's per-connection state and the packets themselves are the ground truth. Knowing what each counter and capture pattern does and does not prove turns them into hypotheses you can test.

## ss: what the kernel knows about each connection

`ss` (the modern `netstat`) shows sockets, and with `-i` the kernel's TCP state for each one:

```
$ ss -tni dst 203.0.113.80
ESTAB 0 1843200 10.0.0.5:51234
                203.0.113.80:443
  cubic rtt:84.2/3.1 cwnd:10
  retrans:0/57 send 1.4Mbps
```

- For an established TCP socket, a growing **Send-Q** indicates outstanding locally queued/unacknowledged data. Sender, path and receiver constraints can contribute; listener queue fields have different meanings.
- **rtt** is the kernel's smoothed estimate; **cwnd** the congestion window in segments.
- **retrans 0/57**: 57 retransmissions in total. A small cwnd and rising retransmission counters motivate recovery analysis, but counts can include spurious retransmissions and are not automatically an application-path loss probability.
- `ss -ltnp` lists listening sockets with their processes: the first check when you get "connection refused".

## tcpdump: packet evidence

When tools disagree, look at the packets.

```
tcpdump -ni eth0 -w cap.pcap \
  'host 203.0.113.80 and tcp port 443'
```

Capture on both ends when authorised and compare timestamps and sequence numbers. Captures can drop packets; offloads can change apparent segmentation/checksums, and encryption hides payload details. Patterns below are hypotheses to investigate:

- **Repeated SYNs without an observed reply**: setup is not completing at that capture point. Check endpoint availability, both directions, filtering and overload. Retry schedules are version/configuration-specific; current Linux also documents an initial linear-timeout feature, so 0/1/3/7/15 seconds is not universal. Either way, the later gaps grow (after any initial linear retries, each wait doubles), so an unanswered `connect()` can hang for a long time: the current Linux kernel documentation says its default settings give up only after about 131 seconds. Set an application deadline that matches your needs instead of relying on the kernel's.
- **SYN answered by RST**: consistent with an explicit refusal; identify who sent it before attributing it to the destination process.
- **Large packets repeatedly fail while small ones pass**: investigate PMTU and size-dependent policy rather than declaring an MTU black hole solely from symptoms.
- **Duplicate ACKs/retransmissions**: can reflect loss, reordering, duplication or spurious recovery. Correlate both ends.
- **Zero receive window**: the peer is advertising no further receive-window allowance. Slow application consumption is common, but receive-memory limits, protocol behaviour and other resource constraints need checking.

## Key takeaways
- Socket queues, recovery counters and receive-window adverts describe different constraints.
- Compare authorised captures and endpoint state before attributing silent setup failure to one cause.

## Further reading
- [ss(8) — Linux manual page](https://man7.org/linux/man-pages/man8/ss.8.html)
- [tcpdump(1) manual page](https://www.tcpdump.org/manpages/tcpdump.1.html)
- [Linux kernel IP sysctl documentation: tcp_syn_retries and tcp_syn_linear_timeouts](https://docs.kernel.org/networking/ip-sysctl.html)
