---
id: app-ntp-ssh-grpc
title: NTP, SSH, SFTP and gRPC on the wire
level: advanced
minutes: 18
summary: How NTP computes clock offset from four timestamps and why asymmetry fools it, the three layers of SSH and its binary packet, why SFTP is not FTP, and the exact bytes of a gRPC call over HTTP/2.
---

Four protocols that engineers use daily and rarely look inside. Each has one central mechanism worth knowing in detail: NTP's offset arithmetic, SSH's layered design, SFTP's request pipelining and gRPC's message framing on top of HTTP/2.

## NTP: agreeing on the time

Clocks drift. As an illustrative drift, 20 parts per million (ppm) accumulates about 1.7 seconds a day; actual oscillators and environmental conditions differ. Distributed systems need better than that for logs, certificates, Kerberos tickets, TOTP codes and lease timeouts.

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

`t1` and `t4` are read from the client's clock; `t2` and `t3` from the server's. From them:

```
offset = ((t2 - t1) + (t3 - t4)) / 2
delay  = (t4 - t1) - (t3 - t2)
```

**Delay** is the round trip minus the server's processing time. **Offset** estimates server time minus client time under the model of stable clock rates and symmetric path delay; it is not an instruction to step the clock immediately.

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

Check it: the client sends at its 10.000, which is server time 10.130; 20 ms later the server receives at 10.150. It replies at 10.152; 20 ms later it is server time 10.172, which on the client's clock is 10.042. The ideal arithmetic recovers 130 ms; floating-point computation has rounding error.

### The symmetry assumption

The formula assumes the outbound and return trips take **equal** time. If they don't, the error in the offset is half the difference. If the request takes 5 ms and the response 35 ms (for example, congestion on the return path), the offset estimate is biased by (5 − 35) / 2 = **−15 ms**. Those four timestamps alone cannot distinguish this from clock offset. With nonnegative delays and otherwise ideal timestamps, asymmetry error is bounded by ±delay/2. Low-delay samples reduce that bound but do not prove symmetry; multiple sources and filtering can help reject bad measurements.

### Disciplining the clock

Clock-discipline behaviour depends on implementation and configuration. Wall-clock steps can disrupt duration calculations and timestamp ordering:

- **Slew**: run the clock slightly fast or slow until the offset is gone. At an illustrative 500 ppm, correcting 1 second takes about 33 minutes. This is not a universal Linux limit: chrony supports higher slew rates on Linux.
- **Step**: set the time directly when policy permits. Classic ntpd uses a 128 ms step threshold with state-machine safeguards; stepping is not inherently restricted to boot.

Programs should measure durations with a **monotonic clock** (`time.monotonic()` in Python), which is never stepped, and use wall-clock time only for timestamps.

**Leap seconds** add a further wrinkle. Google documents a 24-hour **smear** centred on a leap second; it changes clock rate instead of presenting an abrupt insertion. Its offset from unsmeared UTC reaches half a second. Different smear policies need not agree, so do not mix incompatible sources. CGPM Resolution 4 (2022) calls for increasing the permitted UT1−UTC difference by or before 2035, allowing much longer intervals without leap adjustments; it does not specify an unconditional permanent abolition date.

### Wire format and security

The basic NTP header is 48 bytes (extensions/authentication can add bytes): leap indicator, version, mode, stratum, poll, precision, root delay and dispersion, reference ID, then four 64-bit timestamps. Each timestamp is 32 bits of seconds since **1 January 1900** and 32 bits of fraction (about 233 picoseconds of resolution). The seconds field wraps in **February 2036**; era-aware implementations use contextual date information to disambiguate it. Correct era handling is not guaranteed by the 32-bit field alone.

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
2. Both send **KEXINIT** listing supported algorithms in preference order: key exchange, host key types, ciphers, MACs, compression. Negotiation generally follows client preference among mutually supported choices, subject to compatibility rules between key-exchange and host-key algorithms.
3. **Key exchange**: an ephemeral Diffie-Hellman exchange, these days `curve25519-sha256` or a post-quantum hybrid. OpenSSH 9.0 made `sntrup761x25519-sha512@openssh.com` the default, and OpenSSH 10.0 switched to `mlkem768x25519-sha256`.
4. The server **signs** the exchange hash with its **host key**. The client checks that key against `~/.ssh/known_hosts`. Without a preconfigured trusted host key or host-certificate authority, a first connection can prompt for **trust on first use** (TOFU). Independently checking the fingerprint avoids blindly trusting that first peer.
5. Session keys are derived from the shared secret and the exchange hash. The first exchange hash becomes the permanent **session ID**.

After the version strings, SSH already uses the **binary packet protocol**; initial key-exchange packets are unencrypted. `NEWKEYS` activates the negotiated protection. The base packet structure is:

```
uint32  packet_length
byte    padding_length
byte[]  payload
byte[]  random padding (>= 4)
byte[]  MAC (or AEAD tag)
```

In the base RFC 4253 format, packet length including its four-byte length field but excluding the MAC is aligned to the cipher block size or 8 bytes, whichever is larger. Negotiated AEAD/Encrypt-then-MAC formats alter some framing and authentication details. Padding provides limited length hiding. Modern ciphers such as `chacha20-poly1305@openssh.com` and AES-GCM are AEADs, so integrity comes from the cipher's tag. Each direction has an implicit **sequence number**, used by its negotiated integrity construction. This normally detects packet insertion/deletion; the handshake interaction below exposed an exception for affected modes.

> [!warning] Terrapin (2023)
> Sequence numbers were not reset after the handshake. With affected encryption modes (notably ChaCha20-Poly1305 or CBC with Encrypt-then-MAC), an on-path attacker could inject a message during the unencrypted phase and delete one afterwards, keeping the counts consistent, and so silently strip extension negotiation. The fix, "strict KEX", resets sequence numbers at NEWKEYS and forbids stray messages during the handshake; both client and server must support it.

### User authentication

Within the encrypted transport, the client requests the `ssh-userauth` service and tries methods: **publickey**, password, keyboard-interactive (for OTPs). For publickey, the client signs a blob containing the **session ID**, so a captured signature can't be replayed on another connection. A server talking to an attacker in the middle would have a different session ID, so the signature would not verify.

**Agent forwarding** (`ssh -A`) lets a remote host ask your local agent to sign for you. A privileged attacker on that host can request signatures through an unconstrained forwarded agent while it remains accessible. Confirmation, destination and hardware constraints can limit use; forwarding does not normally reveal the private key itself. `ProxyJump` (`ssh -J`) is safer for hopping through bastions: the end-to-end session is negotiated from your laptop.

### Connection layer: channels

Everything useful happens in **channels** multiplexed over one transport:

- `session` channels run a shell, a command (`exec`) or a **subsystem** such as `sftp`.
- `direct-tcpip` channels carry `ssh -L` local port forwards.
- `tcpip-forward` global requests set up `ssh -R` remote forwards.

Each channel has its own **window**, adjusted with `CHANNEL_WINDOW_ADJUST`, just like HTTP/2 streams. A small channel window caps throughput at window ÷ RTT, which is why bulk transfers over high-latency SSH links can be slow even on fast networks (HPN-SSH exists to raise these limits). Ordinary SSH port forwarding relays application bytes between separate TCP connections; it does not encapsulate complete inner TCP packets. Loss on the shared SSH TCP connection can nevertheless stall delivery for every multiplexed channel.

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

(Simplified; the real messages are binary.) File-operation requests carry an **ID** (the INIT/VERSION negotiation is an exception), so a client can have many READs outstanding at once. That **pipelining** is what makes SFTP fast: OpenSSH's client keeps up to 64 requests in flight by default. A naive client that issues one 32 KiB read and waits for the reply gets at most 32 KiB per round trip, about 2.6 Mbit/s at 100 ms RTT.

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
- `grpc-timeout` carries the **deadline**: `250m` means 250 milliseconds (units are H, M, S, m, u, n). Applications should propagate the remaining budget downstream; automatic support and configuration differ by language/library.

### Message framing

Inside DATA frames, each protobuf message is prefixed with **5 bytes**: a 1-byte compressed flag and a 4-byte big-endian length. Take this message:

```
message GetItemRequest {
  int32 id = 1;
  string name = 2;
}
```

Protobuf encodes each field as a **tag**, `(field_number << 3) | wire_type`, followed by the value. Wire type 0 is a varint and 2 is length-delimited.

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

- `08` = field 1, varint. `96 01` = 150 (low 7 bits `0x16` with a continuation bit, then `0x01` × 128).
- `12` = field 2, length-delimited. `02` = 2 bytes. `68 69` = "hi".
- The 5-byte prefix `00 00 00 00 07`: not compressed, 7 bytes.

This helper demonstrates nonnegative values; signed `int32` negatives use sign-extended varints, while `sint32` uses ZigZag encoding.

The message boundaries are independent of DATA frame boundaries: one message can span many frames, and one frame can carry several messages. **Streaming** RPCs simply send more length-prefixed messages on the same stream.

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
- **Keepalives** are HTTP/2 PING frames. Pinging more often than the server allows gets a GOAWAY with `ENHANCE_YOUR_CALM` and the debug data `too_many_pings`.
- **Message size.** Receive limits are configurable and implementation-specific; exceeding an enforced limit can produce RESOURCE_EXHAUSTED. A cross-language table of current defaults is absent because this review did not verify every supported implementation.

## Key takeaways
- NTP's offset is ((t2 − t1) + (t3 − t4)) / 2; under the ideal timestamp model, path asymmetry can cause an error of up to half the delay that one exchange cannot distinguish from clock offset, so low-delay samples are preferred.
- Clock clients can slew or step according to policy; measure durations with a monotonic clock.
- SSH is transport (key exchange, host key, binary packets), user authentication bound to the session ID, and multiplexed channels with their own windows.
- SFTP is a binary file-system protocol inside an SSH channel; request IDs allow pipelining, which is what makes it fast.
- gRPC is a POST per call on HTTP/2, messages framed with a 5-byte prefix, status in trailers, deadlines in `grpc-timeout`.

## Further reading
- [RFC 5905: Network Time Protocol Version 4 — IETF](https://www.rfc-editor.org/rfc/rfc5905)
- [Network Time Protocol — Wikipedia](https://en.wikipedia.org/wiki/Network_Time_Protocol)
- [RFC 4253: The SSH Transport Layer Protocol — IETF](https://www.rfc-editor.org/rfc/rfc4253)
- [Terrapin Attack](https://terrapin-attack.com/)
- [gRPC over HTTP2 protocol spec — GitHub](https://github.com/grpc/grpc/blob/master/doc/PROTOCOL-HTTP2.md)
- [Protocol Buffers encoding — protobuf.dev](https://protobuf.dev/programming-guides/encoding/)
