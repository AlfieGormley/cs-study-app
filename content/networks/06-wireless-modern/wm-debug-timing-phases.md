---
id: wm-debug-timing-phases
title: Separating DNS, TCP and TLS timing phases
level: advanced
minutes: 4
summary: Subtract cumulative milestones only under a connection model that makes that interpretation valid.
sourceLesson: wm-debugging
---

This unit focuses on separating DNS, TCP and TLS timing phases. It builds on the earlier units in this module; the examples below state their additional assumptions.

## curl timings: where the time goes

curl can report cumulative timing milestones. The subtraction example assumes one new, direct TCP/TLS connection without proxy, redirects, retries or reuse; HTTP/3 and multiplexing need different interpretation. The output below is illustrative:

```
$ cat fmt.txt
dns     %{time_namelookup}\n
connect %{time_connect}\n
tls     %{time_appconnect}\n
ttfb    %{time_starttransfer}\n
total   %{time_total}\n
$ curl -so /dev/null -w @fmt.txt \
    https://api.example.com/orders
dns     0.004
connect 0.088
tls     0.262
ttfb    0.910
total   0.955
```

Each value is measured from the start, so subtract the previous milestone to get each phase:

```formula
T_phase = t_end − t_start
T_tcp = t_connect − t_dns
T_tcp = 0.088 s − 0.004 s = 0.084 s = 84 ms
where
T_phase: the duration of one phase, in seconds (s)
t_end: the cumulative time at which the phase finished
t_start: the cumulative time at which the phase began (the previous milestone)
T_tcp: the duration of the TCP handshake
t_connect: curl's time_connect value, 0.088 s here
t_dns: curl's time_namelookup value, 0.004 s here
s: second
ms: millisecond, one thousandth of a second
In words: every curl timer runs from the very start, so each phase is the difference between two neighbouring timers.
```

Applying the same subtraction to every milestone:

| Phase | Calculation | Time |
|---|---|---|
| DNS | 0.004 | 4 ms |
| TCP handshake | 0.088 − 0.004 | 84 ms (≈ 1 RTT) |
| TLS | 0.262 − 0.088 | 174 ms (≈ 2 RTT) |
| Post-TLS to first byte | 0.910 − 0.262 | 648 ms |
| Download | 0.955 − 0.910 | 45 ms |

Under an ideal handshake model, 84 ms approximates RTT. Actual connect time can include scheduling, retries and address selection. The 174 ms TLS phase does not by itself identify the TLS version. The 648 ms interval can include request transmission, network/queueing and server work; subtracting one guessed RTT does not isolate backend processing. Confirm with protocol negotiation details, captures and server traces.

The same breakdown from inside an application:

```python
import socket, ssl, time

def phases(host, port=443, timeout=5):
    # First address only; no fallback.
    ctx = ssl.create_default_context()
    # Convert phase differences to
    # milliseconds.
    ms = lambda a, b: round((b-a) * 1000)
    t0 = time.perf_counter()
    # Resolve before opening the chosen
    # family.
    info = socket.getaddrinfo(
        host, port, type=socket.SOCK_STREAM)
    family, kind, proto, _, addr = info[0]
    t1 = time.perf_counter()
    with socket.socket(family, kind,
                       proto) as sock:
        sock.settimeout(timeout)
        # This milestone ends the TCP
        # connect.
        sock.connect(addr)
        t2 = time.perf_counter()
        # Default context verifies TLS
        # identity.
        with ctx.wrap_socket(
                sock, server_hostname=host):
            t3 = time.perf_counter()
    return {"dns": ms(t0, t1),
            "tcp": ms(t1, t2),
            "tls": ms(t2, t3)}

```

The function includes address resolution once, preserves IPv6 socket-address fields, verifies TLS using the default trust configuration and closes owned sockets. Its timeout applies to socket operations, not necessarily DNS or the whole procedure. It does not send HTTP, implement Happy Eyeballs or measure server response time.

## Key takeaways
- Subtract cumulative milestones only under a connection model that makes that interpretation valid.
- A timing interval does not independently identify a TLS version or pure backend execution time.

## Further reading
- [Write out (curl -w) — Everything curl](https://everything.curl.dev/usingcurl/verbose/writeout.html)
