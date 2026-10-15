---
id: app-ntp-four-timestamps
title: "NTP drift and four-timestamp arithmetic"
level: advanced
minutes: 5
sourceLesson: app-ntp-ssh-grpc
summary: "Four NTP timestamps estimate clock offset and network round-trip delay under an explicit timing model."
---

## NTP: agreeing on the time

Clocks drift. A clock's error rate is quoted in parts per million (ppm): how many microseconds it gains or loses per second. Multiplying by the time elapsed gives the accumulated error:

```formula
E = rt
E = 20 × 10^{−6} × 86,400 s ≈ 1.7 s
where
E: the accumulated clock error, in seconds (s)
r: the drift rate as a fraction; 20 parts per million (ppm) is 20 × 10^{−6} = 0.00002
t: the elapsed time, in seconds; one day is 86,400 s
^: "to the power of"; 10^{−6} is one millionth
≈: approximately equal to
s: seconds
In words: a clock that is off by 20 parts in a million drifts by about 1.7 seconds every day if nothing corrects it.
```

This is an illustrative rate; actual oscillators and environmental conditions differ. Clock synchronisation matters for logs, certificates, Kerberos tickets, TOTP codes and lease timeouts. Acceptable error depends on each protocol and application policy.

**NTP** (version 4, [RFC 5905](https://www.rfc-editor.org/rfc/rfc5905)) runs over **UDP port 123**. Servers are arranged in **strata**: reference clocks (such as GPS or atomic sources) are informally called stratum 0, stratum 1 is a server attached to one, stratum 2 syncs from stratum 1, and so on. Stratum 16 means "unsynchronised". In an NTP packet, a stratum field of zero instead means unspecified/invalid and can identify a Kiss-o'-Death response; it is not an ordinary reference-clock server reply.

### Four timestamps

One request/response gives the client four times:

```
client           server
 t1 ---request--->
                  t2  (server rx)
                  t3  (server tx)
 t4 <--response---
```

The first and fourth timestamps come from the client's clock; the middle two come from the server's clock. From them the client estimates how far its clock is from the server's, and how long the network took:

```formula
θ = ((t_2 − t_1) + (t_3 − t_4)) / 2
δ = (t_4 − t_1) − (t_3 − t_2)
where
θ: theta, the clock offset: the estimate of server time minus client time, in seconds (s). Positive means the client is behind
δ: delta, the round-trip delay: the whole exchange time minus the time the server held the request, in seconds
t_1: client send time in seconds (s), by the client's clock
t_2: server receive time in seconds (s), by the server's clock
t_3: server send time in seconds (s), by the server's clock
t_4: client receive time in seconds (s), by the client's clock
s: seconds
In words: the offset averages the apparent clock difference seen in each direction, which cancels the travel time if both directions take equally long; the delay is the time on the wire.
```

**Round-trip delay** is the round trip minus the server processing time. **Clock offset** estimates server time minus client time under the model that each clock runs at a steady rate and the path delay is symmetric; it is not an instruction to step the clock immediately.

Why does averaging work? Subtracting the client-send timestamp from the server-receive timestamp gives the offset *plus* outbound travel time. Subtracting the client-receive timestamp from the server-send timestamp gives the offset *minus* return travel time. Adding them cancels the travel times only when the two are equal. The same arithmetic in Python:

```python
def ntp(t1, t2, t3, t4):
    # Average apparent differences.
    offset = ((t2 - t1) + (t3 - t4)) / 2
    # Exclude the server handling interval.
    delay = (t4 - t1) - (t3 - t2)
    return offset, delay

# client clock 130 ms behind,
# 20 ms each way, 2 ms processing
o, d = ntp(10.000, 10.150,
           10.152, 10.042)
print(round(o, 3), round(d, 3))
# 0.13 0.04
```

Check it: the client sends at its 10.000, which is server time 10.130; 20 ms later the server receives at 10.150. It replies at 10.152; 20 ms later it is server time 10.172, which on the client's clock is 10.042. Substituting:

```formula
θ = ((10.150 s − 10.000 s)
  + (10.152 s − 10.042 s)) / 2
θ = (0.150 s + 0.110 s) / 2 = 0.130 s
δ = (10.042 s − 10.000 s)
  − (10.152 s − 10.150 s)
δ = 0.042 s − 0.002 s = 0.040 s
where
θ: theta, the estimated clock offset (server minus client), in seconds (s)
δ: delta, the estimated round-trip network delay, in seconds
s: seconds
In words: the client is 130 ms behind the server, and the network round trip took 40 ms (20 ms each way).
```

The ideal arithmetic recovers 130 ms; floating-point computation has rounding error.

## Key takeaways
- Four NTP timestamps estimate clock offset and network round-trip delay under an explicit timing model.
- The delay calculation subtracts the time spent handling the request at the server.

## Further reading
- [RFC 5905](https://www.rfc-editor.org/rfc/rfc5905)
