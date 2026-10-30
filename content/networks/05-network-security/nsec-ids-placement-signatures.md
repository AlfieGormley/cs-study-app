---
id: nsec-ids-placement-signatures
title: IDS placement and signature meaning
level: advanced
minutes: 4
summary: Passive IDS sensors analyse a copy; inline IPS devices can block traffic.
sourceLesson: nsec-detection
---

The earlier units focused on preventive controls. Prevention can fail: a password is phished, a VPN appliance is unpatched, a firewall rule is too broad. The question then is how quickly you notice. **Dwell time** is the interval from intrusion to detection.

Detection on the network rests on three kinds of evidence, which trade detail against cost:

| Source | Detail | Cost to keep |
|---|---|---|
| Packet capture | Captured packet bytes, subject to truncation and loss | Potentially high |
| Protocol logs (Zeek) | Selected connection, protocol-exchange or file events | Depends on logging |
| Flow records | Aggregated traffic sharing selected attributes | Depends on export |

On top of the evidence sit detection systems that raise alerts. This unit introduces alerting engines; the following units examine alert precision and the evidence those engines consume.

## IDS and IPS

An **intrusion detection system** (IDS) watches traffic and raises alerts. An **intrusion prevention system** (IPS) sits inline and can also drop traffic.

```
 IDS (passive):
 net ---+---> switch ---> LAN
        | SPAN/TAP copy
        v
      [IDS] --> alerts

 IPS (inline):
 net ---> [IPS] ---> LAN
            |
       drop or pass
```

- An IDS is fed a copy of traffic from a switch **SPAN** (mirror) port or a network **TAP**, or in the cloud via traffic mirroring. A passive sensor is outside the forwarding path; automatic response integrations can still affect traffic. A mirror can lose packets when the copied traffic exceeds its monitoring-port capacity.
- An IPS can stop an attack in progress, but it adds latency and becomes a point of failure. You must choose **fail-open** (traffic flows if the IPS dies, unprotected) or **fail-closed** (the network goes down with it). A false positive on a blocking rule can disrupt legitimate traffic; alert-only rules do not themselves block it.

> [!analogy] Real-world analogy: a CCTV room and a door supervisor
> A shop can watch its entrance on CCTV from a back room, or post a supervisor at the door. The CCTV operator sees a copy of everything and can raise the alarm, but cannot stop anyone directly; if the camera feed drops out, the shop stays open. The supervisor can turn people away, but every customer queues past them, and if the supervisor leaves the door has to be either locked or left unguarded.
>
> **How it maps:** The CCTV room is a passive IDS fed from a SPAN port or TAP: it analyses a copy of the traffic and raises alerts. The door supervisor is an inline IPS: it can drop traffic, adds delay and is a point of failure. Locking or leaving the door when the supervisor is absent is the fail-closed or fail-open choice. Turning away a regular customer by mistake is a false positive on a blocking rule.
>
> **Where it stops:** A camera feed shows everything in view, but a mirror port can silently lose packets under load and encrypted traffic hides its contents from both devices. A passive sensor can also trigger automated responses elsewhere, so "only watching" is not always harmless.

Network IDS (NIDS) watch the wire; host IDS (HIDS) and EDR agents watch processes and files on each machine. They complement each other: hosts see what happened inside encrypted sessions, networks see machines that have no agent, such as printers, cameras and anything the attacker brought.

### Signatures and anomalies

**Signature-based** detection matches known patterns. Snort and Suricata are examples of open-source engines. A Suricata rule (backslashes continue a rule across lines):

```suricata
alert http any any -> $HOME_NET any ( \
  msg:"SQLi attempt in URI"; \
  flow:established,to_server; \
  http.uri; content:"union select"; \
  nocase; \
  classtype:web-application-attack; \
  sid:1000001; rev:1;)
```

The header (`alert http any any -> $HOME_NET any`) says what traffic to consider; the options say what to look for. `flow:established,to_server` selects traffic towards the server in a flow the engine considers established. This is connection tracking, not cryptographic peer authentication or a guarantee against forged traffic; midstream handling also depends on configuration. `http.uri` selects the normalised URI buffer. The string match is only a teaching example, not a complete SQL-injection detector.

Signatures match specified patterns, which can occur in both known and previously unseen attacks, or in benign traffic. **Anomaly-based** detection learns a baseline (normal hosts, ports, volumes and times) and alerts on deviations: a workstation suddenly talking SMB to fifty others, a server uploading gigabytes at 3 a.m. It can flag previously unseen behaviour, but deviations can be legitimate. Relative false-positive rates depend on the detector, data and threshold.

## Key takeaways
- Passive IDS sensors analyse a copy; inline IPS devices can block traffic.
- Inline failure policy trades continued connectivity against unfiltered passage.
- An established flow is connection state, not cryptographic sender authentication.

## Further reading
- [Intrusion detection system — Wikipedia](https://en.wikipedia.org/wiki/Intrusion_detection_system)
- [Suricata rules format — Suricata docs](https://docs.suricata.io/en/latest/rules/intro.html)
- [Zeek documentation](https://docs.zeek.org/en/v7.1.1/logs/index.html)
