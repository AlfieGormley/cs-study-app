---
id: wm-debug-pmtu-and-resources
title: PMTU failures and connection-resource limits
level: advanced
minutes: 3
summary: Size-sensitive probes help investigate PMTU but ICMP policy and cached state also matter.
sourceLesson: wm-debugging
---

This unit focuses on PMTU failures and connection-resource limits. It builds on the earlier units in this module; the examples below state their additional assumptions.

## MTU black holes

Classic IPv4 PMTUD uses DF and ICMP “fragmentation needed”; IPv6 routers do not fragment and use ICMPv6 Packet Too Big. Blocking those messages can prevent learning a smaller path MTU, but packetization-layer probing or black-hole detection may recover without them. A persistent black hole depends on the actual stack and path.

Symptoms: TCP connects; small requests work; anything large hangs. SSH logs in but freezes on a long directory listing. TLS hangs during the handshake when the certificate chain is big. Common around VPNs, tunnels and overlays.

Test with "don't fragment" pings of decreasing size (Linux):

```
ping -4 -M do -s 1472 host  # IPv4 1500
ping -4 -M do -s 1372 host  # IPv4 1400
```

The `-s` value is the ICMP payload only; the headers make up the rest of the IP packet:

```formula
L_IP = L_data + H_ICMP + H_IP
L_IP = 1,472 B + 8 B + 20 B = 1,500 B
L_IP = 1,372 B + 8 B + 20 B = 1,400 B
where
L_IP: the total IPv4 packet size, in bytes (B)
L_data: the ICMP echo payload size set with -s
H_ICMP: the ICMP echo header, 8 B
H_IP: the IPv4 header without options, 20 B
B: byte
In words: to test a 1,500-byte path, ask for 28 bytes less payload than the MTU.
```

These sizes assume IPv4 without options. Probe success/failure also depends on ICMP policy, reverse-path size and local cached PMTU; it is evidence, not proof of the application’s exact PMTU. Correct filtering of relevant ICMP errors, suitable MTU and, for TCP, carefully configured MSS clamping can help. MSS clamping does not repair UDP or every directional problem.

## Other usual suspects

- **DNS**: stale records after a migration; resolver timeouts adding seconds; broken AAAA records.
- **Duplex or link errors**: inspect driver/interface counters (`ip -s link`, and driver-specific tools where needed). CRC errors support a physical-link investigation, but aggregate input errors do not uniquely identify a cable or optic.
- **Asymmetric routing through a stateful firewall**: a stateful device may reject traffic when required state is absent; asymmetric routing need not fail if state is shared or policy supports it.
- **Conntrack or NAT table exhaustion**: new connections fail under load while established ones work; Linux conntrack may log a rate-limited "table full" message; remote NAT services expose different telemetry.
- **Ephemeral port exhaustion**: a client opening many short connections to one destination runs out of source ports, with many sockets in TIME_WAIT. Reuse connections.

> [!example] Putting it together
> Upload stalls after a VPN change, with large DF echo probes failing and smaller ones succeeding, support a PMTU hypothesis. Compare both-end captures, effective tunnel MTU and ICMP errors before concluding. If the evidence confirms an encapsulation/PMTU problem, correct the relevant MTU or error handling; apply TCP MSS clamping only where it addresses the measured path.

## Key takeaways
- Size-sensitive probes help investigate PMTU but ICMP policy and cached state also matter.
- New-flow failures can reflect NAT, tracking or local port resources; inspect the constrained resource.

## Further reading
- [Path MTU Discovery — Wikipedia](https://en.wikipedia.org/wiki/Path_MTU_Discovery)
- [RFC 2923: TCP Problems with Path MTU Discovery](https://www.rfc-editor.org/rfc/rfc2923)
