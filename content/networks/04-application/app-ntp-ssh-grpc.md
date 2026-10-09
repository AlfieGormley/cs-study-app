---
id: app-ntp-ssh-grpc
title: NTP, SSH, SFTP and gRPC on the wire
level: advanced
minutes: 18
summary: How NTP computes clock offset from four timestamps and why asymmetry fools it, the three layers of SSH and its binary packet, why SFTP is not FTP, and the exact bytes of a gRPC call over HTTP/2.
---

Four protocols that engineers use daily and rarely look inside. Each has one central mechanism worth knowing in detail: NTP's offset arithmetic, SSH's layered design, SFTP's request pipelining and gRPC's message framing on top of HTTP/2.

## NTP: agreeing on the time

Clocks drift. A clock's error rate is quoted in parts per million (ppm): how many microseconds it gains or loses per second. Multiplying by the time elapsed gives the accumulated error:

```formula
E = r × t
E = 20 × 10^−6 × 86,400 s ≈ 1.7 s
where
E: the accumulated clock error, in seconds (s)
r: the drift rate as a fraction; 20 parts per million (ppm) is 20 × 10^−6 = 0.00002
t: the elapsed time, in seconds; one day is 86,400 s
^: "to the power of"; 10^−6 is one millionth
≈: approximately equal to
s: seconds
In words: a clock that is off by 20 parts in a million drifts by about 1.7 seconds every day if nothing corrects it.
```

This is an illustrative rate; actual oscillators and environmental conditions differ. Distributed systems need better than that for logs, certificates, Kerberos tickets, TOTP codes and lease timeouts.

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

`t1` and `t4` are read from the client's clock; `t2` and `t3` from the server's. From them the client estimates how far its clock is from the server's, and how long the network took:

```formula
θ = ((t_2 − t_1) + (t_3 − t_4)) / 2
δ = (t_4 − t_1) − (t_3 − t_2)
where
θ: theta, the clock offset: the estimate of server time minus client time, in seconds (s). Positive means the client is behind
δ: delta, the round-trip delay: the whole exchange time minus the time the server held the request, in seconds
t_1: when the client sent the request, by the client's clock
t_2: when the server received it, by the server's clock
t_3: when the server sent the reply, by the server's clock
t_4: when the client received the reply, by the client's clock
s: seconds
In words: the offset averages the apparent clock difference seen in each direction, which cancels the travel time if both directions take equally long; the delay is the time on the wire.
```

**Round-trip delay** is the round trip minus the server's processing time. **Clock offset** estimates server time minus client time under the model that each clock runs at a steady rate and the path delay is symmetric; it is not an instruction to step the clock immediately.

Why does averaging work? The outbound difference t_2 − t_1 is the offset *plus* the outbound travel time, and t_3 − t_4 is the offset *minus* the return travel time. Adding them cancels the travel times only when the two are equal. The same arithmetic in Python:

```python
def ntp(t1, t2, t3, t4):
    offset = ((t2 - t1) + (t3 - t4)) / 2
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
θ = ((10.150 − 10.000)
  + (10.152 − 10.042)) / 2
θ = (0.150 s + 0.110 s) / 2 = 0.130 s
δ = (10.042 − 10.000) − (10.152 − 10.150)
δ = 0.042 s − 0.002 s = 0.040 s
where
θ: theta, the estimated clock offset (server minus client), in seconds (s)
δ: delta, the estimated round-trip network delay, in seconds
s: seconds
In words: the client is 130 ms behind the server, and the network round trip took 40 ms (20 ms each way).
```

The ideal arithmetic recovers 130 ms; floating-point computation has rounding error.

### The symmetry assumption

The formula assumes the outbound and return trips take **equal** time. If they don't, the error in the offset is half the difference:

```formula
ε = (d_out − d_back) / 2
ε = (5 ms − 35 ms) / 2 = −15 ms
|ε| ≤ δ / 2
where
ε: epsilon, the error in the offset estimate caused by unequal paths, in milliseconds (ms)
d_out: the one-way time from client to server; here 5 ms
d_back: the one-way time from server back to client; here 35 ms, for example because of congestion on the return path
δ: delta, the measured round-trip delay, here 40 ms
|ε|: the size of the error, ignoring its sign
≤: is at most
ms: milliseconds, thousandths of a second
In words: if the reply takes 30 ms longer than the request, the offset comes out 15 ms wrong, and the error can never be more than half the round trip.
```

So in this example the offset estimate is biased by **−15 ms**. Those four timestamps alone cannot distinguish this from clock offset. With nonnegative delays and otherwise ideal timestamps, asymmetry error is bounded by ±delay/2. Low-delay samples reduce that bound but do not prove symmetry; multiple sources and filtering can help reject bad measurements.

### Disciplining the clock

Clock-discipline behaviour depends on implementation and configuration. Wall-clock steps can disrupt duration calculations and timestamp ordering:

- **Slewing**: run the clock slightly fast or slow until the offset is gone. The time needed is the offset divided by the slew rate; at an illustrative 500 ppm, correcting 1 second takes 1 ÷ 0.0005 = 2,000 seconds, about 33 minutes (see the formula below). This is not a universal Linux limit: chrony supports higher slew rates on Linux.
- **Stepping the clock**: set the time directly when policy permits. Classic ntpd uses a 128 ms step threshold with state-machine safeguards; stepping is not inherently restricted to boot.

```formula
T = θ / r
T = 1 s / (500 × 10^−6) = 2,000 s ≈ 33 min
where
T: how long slewing takes to remove the offset, in seconds (s)
θ: theta, the offset to correct; here 1 second
r: the slew rate as a fraction; 500 parts per million (ppm) is 500 × 10^−6 = 0.0005, so the clock gains or loses half a millisecond per second
^: "to the power of"; 10^−6 is one millionth
≈: approximately equal to
s: seconds
min: minutes
In words: running the clock 0.05% fast takes about 33 minutes to catch up one second, which is why big offsets are usually stepped.
```

Programs should measure durations with a **monotonic clock** (`time.monotonic()` in Python), which is never stepped, and use wall-clock time only for timestamps.

**Leap seconds** add a further wrinkle. Google documents a 24-hour **leap smear** centred on a leap second; it changes the clock's rate instead of presenting an abrupt insertion. Its offset from unsmeared UTC reaches half a second. Different smear policies need not agree, so do not mix incompatible sources. CGPM Resolution 4 (2022) calls for increasing the permitted UT1−UTC difference by or before 2035, allowing much longer intervals without leap adjustments; it does not specify an unconditional permanent abolition date.

### Wire format and security

The basic NTP header is 48 bytes (extensions/authentication can add bytes): leap indicator, version, mode, stratum, poll, precision, root delay and dispersion, reference ID, then four 64-bit timestamps. Each timestamp is 32 bits of seconds since **1 January 1900** and 32 bits of fraction. Both limits follow from the field width:

```formula
r = 1 s / 2^32 ≈ 2.33 × 10^−10 s ≈ 233 ps
W = 2^32 s ≈ 4.29 × 10^9 s ≈ 136 yr
where
r: the resolution: the smallest time step the 32-bit fraction can represent
W: how long the 32-bit seconds count lasts before it wraps back to zero
^: "to the power of"; 2^32 = 4,294,967,296
≈: approximately equal to
s: seconds
ps: picoseconds, trillionths (10^−12) of a second
yr: years; one year is about 31.6 million seconds
In words: splitting a second into 2^32 steps gives steps of about 233 picoseconds, and counting 2^32 whole seconds from 1900 runs out after about 136 years.
```

So the seconds field wraps in **February 2036**; era-aware implementations use contextual date information to disambiguate it. Correct era handling is not guaranteed by the 32-bit field alone.

Plain NTP is unauthenticated, so an on-path attacker can shift your clock and, for example, make expired certificates look valid. **NTS** (Network Time Security, [RFC 8915](https://www.rfc-editor.org/rfc/rfc8915)) uses TLS key establishment (TCP port 4460), then protects NTP exchanges with negotiated AEAD keys and authenticators. Opaque cookies carry server state; they are not themselves the per-packet integrity check. Authentication does not prevent an on-path attacker from delaying valid packets.

Legacy ntpd's unauthenticated `monlist` response could amplify spoofed requests, documented as CVE-2013-5211. Exposure depends on implementation, version and access controls. A universal amplification ratio and present-day deployment prevalence are omitted because this review did not establish reliable measurements.

**PTP** (IEEE 1588) can achieve sub-microsecond synchronisation in appropriately engineered networks. Hardware timestamping and PTP-aware transparent clocks reduce timestamp and switch-residence errors; the protocol name alone does not guarantee a particular accuracy.

## SSH: three protocols in a stack

SSH (RFCs 4251 to 4254) runs over **TCP port 22** and is really three protocols layered on top of each other:

```
+-----------------------------+
| Connection: channels       |
|  (shell, exec, sftp, -L)   |
+-----------------------------+
| User authentication        |
|  (publickey, password)     |
+-----------------------------+
| Transport: key exchange,   |
|  encryption, integrity     |
+-----------------------------+
| TCP                        |
+-----------------------------+
```

### Transport layer

1. Both sides send a **version string** in plaintext, such as `SSH-2.0-OpenSSH_9.6`.
2. Both send **KEXINIT** listing supported algorithms in preference order: key exchange, host key types, ciphers, message authentication codes (MACs), compression. Negotiation generally follows client preference among mutually supported choices, subject to compatibility rules between key-exchange and host-key algorithms.
3. **Key exchange**: an ephemeral Diffie-Hellman exchange, these days `curve25519-sha256` or a post-quantum hybrid. OpenSSH 9.0 made `sntrup761x25519-sha512@openssh.com` the default, and OpenSSH 10.0 switched to `mlkem768x25519-sha256`.
4. The server **signs** the exchange hash with its **host key**. The client checks that key against `~/.ssh/known_hosts`. Without a preconfigured trusted host key or host-certificate authority, a first connection can prompt for **trust on first use** (TOFU). Independently checking the fingerprint avoids blindly trusting that first peer.
5. Session keys are derived from the shared secret and the exchange hash. The first exchange hash becomes the permanent **SSH session ID**.

After the version strings, SSH already uses the **binary packet protocol**; initial key-exchange packets are unencrypted. `NEWKEYS` activates the negotiated protection. The base packet structure is:

```
uint32  packet_length
byte    padding_length
byte[]  payload
byte[]  random padding (>= 4)
byte[]  MAC (or AEAD tag)
```

In the base RFC 4253 format, packet length including its four-byte length field but excluding the message authentication code is aligned to the cipher block size or 8 bytes, whichever is larger. Negotiated AEAD/Encrypt-then-MAC formats alter some framing and authentication details. Padding provides limited length hiding. Modern ciphers such as `chacha20-poly1305@openssh.com` and AES-GCM are AEADs, so integrity comes from the cipher's tag. Each direction has an implicit **sequence number**, used by its negotiated integrity construction. This normally detects packet insertion/deletion; the handshake interaction below exposed an exception for affected modes.

> [!warning] Terrapin (2023)
> Sequence numbers were not reset after the handshake. With affected encryption modes (notably ChaCha20-Poly1305 or CBC with Encrypt-then-MAC), an on-path attacker could inject a message during the unencrypted phase and delete one afterwards, keeping the counts consistent, and so silently strip extension negotiation. The fix, "strict KEX", resets sequence numbers at NEWKEYS and forbids stray messages during the handshake; both client and server must support it.

### User authentication

Within the encrypted transport, the client requests the `ssh-userauth` service and tries methods: **publickey**, password, keyboard-interactive (for OTPs). For publickey, the client signs a blob containing the **SSH session ID**, so a captured signature can't be replayed on another connection. A server talking to an attacker in the middle would have a different session ID, so the signature would not verify.

**Agent forwarding** (`ssh -A`) lets a remote host ask your local agent to sign for you. A privileged attacker on that host can request signatures through an unconstrained forwarded agent while it remains accessible. Confirmation, destination and hardware constraints can limit use; forwarding does not normally reveal the private key itself. `ProxyJump` (`ssh -J`) is safer for hopping through bastions: the end-to-end session is negotiated from your laptop.

### Connection layer: channels

Everything useful happens in **SSH channels** multiplexed over one transport:

- `session` channels run a shell, a command (`exec`) or an **SSH subsystem** such as `sftp`.
- `direct-tcpip` channels carry `ssh -L` local port forwards.
- `tcpip-forward` global requests set up `ssh -R` remote forwards.

Each channel has its own **channel window**, adjusted with `CHANNEL_WINDOW_ADJUST`, just like HTTP/2 streams. A small channel window caps throughput at the window divided by the round-trip time (the same window-over-round-trip ceiling as HTTP/2 flow control), which is why bulk transfers over high-latency SSH links can be slow even on fast networks (HPN-SSH exists to raise these limits). Ordinary SSH port forwarding relays application bytes between separate TCP connections; it does not encapsulate complete inner TCP packets. Loss on the shared SSH TCP connection can nevertheless stall delivery for every multiplexed channel.

## SFTP: not FTP

SFTP is **not** FTP over SSH. It is a separate binary protocol (draft-ietf-secsh-filexfer; OpenSSH implements version 3) that runs as the `sftp` subsystem inside one SSH session channel. Since OpenSSH 9.0, the `scp` command uses the SFTP protocol by default too.

It works like a remote file system API:

```
C: SSH_FXP_OPEN  id=1 "/data/a.bin"
S: SSH_FXP_HANDLE id=1 h="\x00\x01"
C: SSH_FXP_READ id=2 h off=0     len=32768
C: SSH_FXP_READ id=3 h off=32768 len=32768
C: SSH_FXP_READ id=4 h off=65536 len=32768
S: SSH_FXP_DATA id=2 ...
S: SSH_FXP_DATA id=3 ...
C: SSH_FXP_CLOSE id=9 h
```

(Simplified; the real messages are binary.) File-operation requests carry an **SFTP request ID** (the INIT/VERSION negotiation is an exception), so a client can have many READs outstanding at once. That **pipelining** is what makes SFTP fast: OpenSSH's client keeps up to 64 requests in flight by default. A naive client that issues one 32 KiB read and waits for the reply gets at most one block per round trip:

```formula
T = k × b / RTT
T = 1 × 32,768 B / 0.1 s = 327,680 B/s
T = 327,680 × 8 bit/s ≈ 2.6 Mbit/s
where
T: the best possible transfer rate, in bytes per second (B/s) or megabits per second (Mbit/s)
k: the number of read requests kept outstanding at once; 1 for the naive client, up to 64 for OpenSSH
b: the size of each read; 32 KiB = 32 × 1,024 = 32,768 bytes
RTT: the round-trip time, in seconds (s); here 100 ms = 0.1 s
B: bytes
s: seconds
bit: one binary digit; 8 bits make a byte
Mbit: megabit, one million bits
≈: approximately equal to
In words: one 32 KiB read per 100 ms round trip limits the client to about 2.6 megabits per second; keeping 64 reads outstanding raises that ceiling 64-fold.
```

## gRPC on the wire

This section describes native gRPC over **HTTP/2**. Each call is one HTTP/2 stream. Knowing the framing helps you debug it with ordinary HTTP tools.

### The request

```
HEADERS (stream 1)
  :method POST
  :scheme https
  :path /shop.Catalog/GetItem
  :authority api.shop.example
  content-type application/grpc
  te trailers
  grpc-timeout 250m
DATA (stream 1, END_STREAM)
  <length-prefixed message>
```

- The **path** is `/package.Service/Method`, which is how proxies route and authorise per method.
- `te: trailers` tells proxies the client understands trailers, which gRPC needs.
- `grpc-timeout` carries the **gRPC deadline**: `250m` means 250 milliseconds (units are H, M, S, m, u, n). Applications should propagate the remaining budget downstream; automatic support and configuration differ by language/library.

### Message framing

Inside DATA frames, each protobuf message is prefixed with **5 bytes**: a 1-byte compressed flag and a 4-byte big-endian length. Take this message:

```
message GetItemRequest {
  int32 id = 1;
  string name = 2;
}
```

Protobuf encodes each field as a **protobuf tag** followed by the value. The tag packs the field number and the wire type into one varint: shifting left by 3 bits (`<< 3` in code) multiplies by 8, leaving the low 3 bits for the wire type.

```formula
g = f × 8 + w
g_1 = 1 × 8 + 0 = 8 = 0x08
g_2 = 2 × 8 + 2 = 18 = 0x12
where
g: the tag byte value
f: the field number from the .proto definition; id is 1, name is 2
w: the wire type: 0 for a varint, 2 for length-delimited data such as a string
g_1: the tag for field 1 (id, a varint)
g_2: the tag for field 2 (name, a string); 18 is written 0x12 in hexadecimal (1 × 16 + 2)
In words: multiply the field number by 8 and add the wire type to get the tag byte.
```

```python
import struct

def pb_varint(n):
    # Unsigned uint64 helper only.
    if (type(n) is not int
            or not 0 <= n < 2**64):
        raise ValueError("expected uint64")
    out = bytearray()
    while True:
        b = n & 0x7F
        n >>= 7
        if n:
            out.append(b | 0x80)
        else:
            out.append(b)
            return bytes(out)

# id=150, name="hi"
msg = (b"\x08" + pb_varint(150)
       + b"\x12\x02hi")
frame = struct.pack("!BI", 0,
                    len(msg)) + msg
print(frame.hex(" "))
# 00 00 00 00 07 08 96 01 12 02 68 69
```

- `08` = field 1, varint. `96 01` = 150. Each varint byte carries 7 bits of the number, least significant group first, and its top bit (worth 128) means "more bytes follow" (see the formula below).
- `12` = field 2, length-delimited. `02` = 2 bytes. `68 69` = "hi".
- The 5-byte prefix `00 00 00 00 07`: not compressed, 7 bytes.

```formula
v = (b_1 − 128) + b_2 × 128
v = (150 − 128) + 1 × 128
v = 22 + 128 = 150
where
v: the decoded varint value
b_1: the first byte, 0x96 = 150 in decimal; subtracting 128 removes its continuation bit, leaving the low 7 bits, 22 (0x16)
b_2: the second byte, 0x01 = 1, which has no continuation bit, so it is the last; it is worth 128 times its value because it holds the next 7 bits
In words: strip the continuation bit from each byte, then add the groups with each later group worth 128 times more.
```

This helper demonstrates nonnegative values; signed `int32` negatives use sign-extended varints, while `sint32` uses ZigZag encoding.

The message boundaries are independent of DATA frame boundaries: one message can span many DATA frames, and one DATA frame can carry several messages. **Streaming RPCs** simply send more length-prefixed messages on the same stream.

### The response and trailers

```
HEADERS  :status 200
         content-type application/grpc
DATA     <length-prefixed messages>
HEADERS  (END_STREAM)  trailers:
         grpc-status 0
         grpc-message ""
```

The **status is in the trailers**, because a streaming server only knows whether the call succeeded at the end. A conforming gRPC response uses HTTP status 200 even for a gRPC error; HTTP intermediaries and protocol errors can produce other HTTP statuses. A call that fails immediately can send a single "Trailers-Only" HEADERS frame.

Common codes:

| Code | Name | Retry? |
|---|---|---|
| 0 | OK | n/a |
| 3 | INVALID_ARGUMENT | No |
| 4 | DEADLINE_EXCEEDED | Maybe |
| 5 | NOT_FOUND | No |
| 8 | RESOURCE_EXHAUSTED | Depends on quota/resource cause |
| 13 | INTERNAL | Rarely |
| 14 | UNAVAILABLE | Consider retry if safe and budget permits |

Retry decisions need method semantics, duplicate-effect protection, retry policy and remaining deadline. A timeout can occur after a server has committed a change.

### Operational consequences

- **Browsers** can't read HTTP/2 trailers or control framing through `fetch`, so browsers use **gRPC-Web**, which moves trailers into the body and needs a proxy (or server support) to translate.
- **Load balancing.** A client using one long-lived HTTP/2 connection sends its streams to the backend chosen for that connection by a connection-oriented layer-4 balancer. A channel can also use multiple connections; the pinning lasts for a connection, not forever. Use a layer-7 (HTTP/2-aware) proxy such as Envoy, or client-side balancing across several connections.
- **gRPC keepalives** are HTTP/2 PING frames. Pinging more often than the server allows gets a GOAWAY with `ENHANCE_YOUR_CALM` and the debug data `too_many_pings`.
- **Message size.** Receive limits are configurable and implementation-specific; exceeding an enforced limit can produce RESOURCE_EXHAUSTED. A cross-language table of current defaults is absent because this review did not verify every supported implementation.

## Key takeaways
- NTP's offset is ((t2 − t1) + (t3 − t4)) / 2; under the ideal timestamp model, path asymmetry can cause an error of up to half the delay that one exchange cannot distinguish from clock offset, so low-delay samples are preferred.
- Clock clients can slew or step according to policy; measure durations with a monotonic clock.
- SSH is transport (key exchange, host key, binary packets), user authentication bound to the session ID, and multiplexed channels with their own windows.
- SFTP is a binary protocol for remote file-system operations inside an SSH channel; request IDs allow pipelining, which is what makes it fast.
- gRPC is a POST per call on HTTP/2, messages framed with a 5-byte prefix, status in trailers, deadlines in `grpc-timeout`.

## Further reading
- [RFC 5905: Network Time Protocol Version 4 — IETF](https://www.rfc-editor.org/rfc/rfc5905)
- [Network Time Protocol — Wikipedia](https://en.wikipedia.org/wiki/Network_Time_Protocol)
- [RFC 4253: The SSH Transport Layer Protocol — IETF](https://www.rfc-editor.org/rfc/rfc4253)
- [Terrapin Attack](https://terrapin-attack.com/)
- [gRPC over HTTP2 protocol spec — GitHub](https://github.com/grpc/grpc/blob/master/doc/PROTOCOL-HTTP2.md)
- [Protocol Buffers encoding — protobuf.dev](https://protobuf.dev/programming-guides/encoding/)
