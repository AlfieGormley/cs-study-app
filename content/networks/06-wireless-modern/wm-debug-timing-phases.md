---
id: wm-debug-timing-phases
title: Separating DNS, TCP and TLS timing phases
level: advanced
minutes: 3
summary: Subtract cumulative milestones only under a connection model that makes that interpretation valid.
sourceLesson: wm-debugging
---

"The API is slow" usually means one phase of a request is slow: name lookup, connection setup, TLS, waiting for the server, or the download itself. Splitting a request into those phases is often the fastest way to find which part of the system to look at.

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

Each value is measured from the very start of the command, like a stopwatch that is never reset, so each phase is the difference between neighbouring milestones:

| Phase | Calculation | Time |
|---|---|---|
| DNS | 0.004 | 4 ms |
| TCP handshake | 0.088 − 0.004 | 84 ms (≈ 1 RTT) |
| TLS | 0.262 − 0.088 | 174 ms (≈ 2 RTT) |
| Post-TLS to first byte | 0.910 − 0.262 | 648 ms |
| Download | 0.955 − 0.910 | 45 ms |

Reading the result:

- **The TCP handshake approximates one RTT.** Under an ideal handshake model, 84 ms is a good RTT estimate; actual connect time can include scheduling, retries and address selection.
- **TLS takes about two RTTs here.** That is consistent with several handshake patterns; the duration alone does not identify the TLS version.
- **The biggest phase is after TLS.** The 648 ms until the first byte includes sending the request, network and queueing delay, and server work. Subtracting one guessed RTT does not isolate backend processing, but it says where to look next: server-side timing and traces.
- **The download is quick.** The response is small or the path is fast; throughput is not the problem in this sample.

The same milestones can be timed inside an application by recording a clock around name resolution, the TCP connect and the TLS handshake. Confirm conclusions with protocol negotiation details, captures and server traces.

## Key takeaways
- Subtract cumulative milestones only under a connection model that makes that interpretation valid.
- A timing interval does not independently identify a TLS version or pure backend execution time.

## Further reading
- [Write out (curl -w) — Everything curl](https://everything.curl.dev/usingcurl/verbose/writeout.html)
