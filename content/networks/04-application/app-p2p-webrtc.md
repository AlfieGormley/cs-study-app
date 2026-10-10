---
id: app-p2p-webrtc
title: "Peer to peer: BitTorrent, Kademlia, WebRTC and RTP"
level: advanced
minutes: 18
summary: How BitTorrent splits, verifies and trades pieces, how Kademlia's XOR metric supports logarithmic lookup under its routing assumptions, how WebRTC gets two browsers talking through NATs with ICE, STUN and TURN, and how RTP carries real-time media.
---

Most of the internet is client-server. Peer-to-peer systems let participants also serve data or resources, which brings two hard problems: **finding** peers and content without a central index, and **reaching** peers that sit behind NATs and firewalls. BitTorrent and Kademlia solve the first; WebRTC's ICE solves the second; and RTP carries the media once a path exists.

## BitTorrent

### The metainfo file and the info-hash

For **BitTorrent v1**, a `.torrent` file is a **bencoded** dictionary. Bencoding has four types:

| Type | Example | Encodes |
|---|---|---|
| Integer | `i42e` | 42 |
| String | `4:spam` | "spam" |
| List | `l4:spami42ee` | ["spam", 42] |
| Dict | `d3:cow3:mooe` | {"cow": "moo"} |

Dictionary keys are byte strings and must be **sorted by raw bytes**. Canonical integer and string-length encodings also matter; hash the original encoded `info` substring or fully validate input before re-encoding. That matters because of the `info` dictionary:

- `name`, `length` (or a list of files),
- `piece length`, chosen when the torrent is created (256 KiB is one example),
- `pieces`: the **SHA-1 hashes** of every piece, 20 bytes each, concatenated.

The **info-hash** is the SHA-1 of the bencoded `info` dictionary. It identifies the torrent everywhere: to trackers, in the DHT, in the peer handshake and in magnet links (`magnet:?xt=urn:btih:<info-hash>`). It ties the metadata to the piece hashes, subject to SHA-1's security limitations. An info-hash is not a publisher identity or proof that downloaded content is safe.

```python
import hashlib

def bencode(x):
    if type(x) is int:
        return b"i%de" % x
    if isinstance(x, str):
        x = x.encode()
    if isinstance(x, bytes):
        return b"%d:%s" % (len(x), x)
    if isinstance(x, list):
        return (b"l" + b"".join(
            map(bencode, x)) + b"e")
    if isinstance(x, dict):
        pairs = []
        for k, v in x.items():
            if isinstance(k, str):
                k = k.encode("utf-8")
            if not isinstance(k, bytes):
                raise TypeError("key type")
            pairs.append((k, v))
        keys = [k for k, _ in pairs]
        if len(set(keys)) != len(keys):
            raise ValueError("same key")
        pairs.sort(key=lambda pair: pair[0])
        return b"d" + b"".join(
            bencode(k) + bencode(v)
            for k, v in pairs) + b"e"
    raise TypeError("unsupported type")

print(bencode({"spam": ["a", 42],
               "cow": "moo"}))
# b'd3:cow3:moo4:spaml1:ai42eee'
```

BitTorrent v2 (BEP 52) replaces SHA-1 with **SHA-256 Merkle trees** per file, with 16 KiB leaves (the final block can be shorter). With the necessary hashes/proofs, blocks can be verified against the per-file root; identical file contents share that root. The v2 info-hash is SHA-256, with protocol-specific truncation where a 20-byte identifier is required.

### Finding peers

A client finds others through a **BitTorrent tracker** (an HTTP or UDP server returning peer lists for an info-hash), the **DHT** (below) or **peer exchange** with already-connected peers. A magnet link can carry an info-hash and optional parameters such as tracker URLs or a display name; the client fetches the `info` dictionary itself from peers (BEP 9) and verifies it against the hash.

### The peer wire protocol

Peers talk over TCP (or uTP, a UDP-based protocol with delay-based congestion control designed to yield to other traffic). The connection starts with a **68-byte handshake**:

```
1   pstrlen = 19
19  "BitTorrent protocol"
8   reserved (extension bits)
20  info_hash
20  peer_id
```

The field sizes add up to the fixed length:

```formula
H = 1 B + 19 B + 8 B + 20 B + 20 B = 68 B
where
H: the length of the handshake, in bytes (B)
B: bytes: 1 for pstrlen, 19 for the text "BitTorrent protocol", 8 reserved, 20 for the info-hash and 20 for the peer ID
In words: every BitTorrent v1 handshake is exactly 68 bytes, so a receiver knows how much to read before checking the info-hash.
```

After that, every message except the zero-length keep-alive carries a 4-byte big-endian length, a 1-byte ID and a payload:

| ID | Message | Payload |
|---|---|---|
| 0 / 1 | choke / unchoke | none |
| 2 / 3 | interested / not interested | none |
| 4 | have | piece index |
| 5 | bitfield | pieces I have |
| 6 | request | index, offset, length |
| 7 | piece | index, offset, block |
| 8 | cancel | as request |

A length of 0 is a keep-alive. Pieces are requested in **16 KiB blocks**, and clients keep several requests outstanding per peer (pipelining again, for the same window/RTT reason as SFTP).

Each completed piece is hashed and compared with the metainfo. A mismatch means the piece is discarded and re-downloaded, and the peers that supplied it may be banned. This detects mismatching content without trusting each supplier, but still depends on trusted metadata and hash assumptions. A mixed-source bad piece does not identify which contributor supplied a bad block.

### Piece selection and choking

Two policies make swarms work:

- **Rarest first.** Download the pieces that the fewest of your peers have. This promotes availability of scarce pieces but cannot guarantee that every piece remains online and makes you useful to others sooner.
- **Tit-for-tat choking.** You upload only to a few peers at a time. BEP 3 describes decisions on a 10-second cadence and rotation of an optimistic slot every 30 seconds. The optimistic interested peer counts within the four allowed interested downloaders, rather than being an unconditional fifth slot; new connections receive selection bias. Seeders use upload performance rather than download reciprocation. Client policies can differ.

Near the end, **endgame mode** requests the last few blocks from every peer that has them and cancels duplicates on arrival, so one slow peer doesn't hold up completion.

## Kademlia: the XOR metric

A **distributed hash table** (DHT) maps keys to values with no central server. BitTorrent's **Mainline DHT** (BEP 5) is based on **Kademlia** (Maymounkov and Mazières, 2002) and stores "which peers have info-hash X". A current population estimate is absent because this review did not establish a reliable measurement.

Nodes and keys share a 160-bit ID space (info-hashes are 160 bits, so they fit). The distance between two IDs is their **XOR** (exclusive or: compare the IDs bit by bit, writing 1 where they differ and 0 where they match), read as an integer. With 4-bit IDs:

```formula
d(a, b) = a ⊕ b
d(0110, 0011) = 0101 = 5
where
d(a, b): the Kademlia distance between IDs a and b, a whole number
a, b: two node or key IDs, written here in binary (base 2); 160 bits long in Mainline DHT
⊕: XOR, exclusive or: each result bit is 1 if the two input bits differ and 0 if they are the same
In words: two IDs are as far apart as the binary number marking where their bits differ; 0110 and 0011 differ in the second and fourth bits, giving 0101, which is 5.
```

In Python the XOR operator is `^`, so `0b0110 ^ 0b0011` gives 5. A difference in a high bit outweighs all the lower bits together, so IDs that share a longer prefix are always closer.

XOR distance is a true metric, meaning it behaves like ordinary distance:

```formula
d(a, a) = 0
d(a, b) = d(b, a)
d(a, c) ≤ d(a, b) + d(b, c)
where
d(a, b): the XOR distance between IDs a and b
a, b, c: any three IDs
≤: is less than or equal to
In words: every ID is at distance zero from itself, distance is the same in both directions, and going via a third ID is never shorter than going direct (the triangle inequality).
```

Crucially, **for any point and any distance there is exactly one ID at that distance**, so all nodes can consistently rank IDs for a target. Successful convergence also requires adequate live routing information. Original Kademlia replicates each value on a small, fixed number of the closest nodes (the parameter k, introduced below); Mainline DHT stores peer contact information associated with the hash.

### k-buckets

Each node keeps a DHT routing table made of **k-buckets**. In the basic distance-bucket model, each bucket covers a band of distances twice as wide as the one before:

```formula
2^i ≤ d < 2^{i+1}
s = 159 − i
where
i: the bucket number, from 0 (nearest) to 159 (farthest) for 160-bit IDs
d: the XOR distance from our own ID to a contact
s: the number of leading bits the contact's ID shares with ours
^: "to the power of"; 2^i is i copies of 2 multiplied together
≤: is less than or equal to
<: is less than
In words: bucket i holds contacts whose first differing bit is bit i counted from the right, so they share the 159 − i bits above it with us.
```

Each bucket holds a fixed maximum number of contacts, a parameter the paper calls k: 20 in the original paper, and **8 in Mainline DHT**.

The capacity per bucket is bounded by k; contact **density** falls across exponentially larger distance regions. Mainline DHT uses a splitting routing-table implementation rather than a literal permanently allocated array of 160 buckets. It's like knowing every house on your street, a few people in your town and one person in each country.

When a bucket is full and a new contact appears, Kademlia **pings the least recently seen** contact and drops the newcomer if the old one answers. Nodes that have been up a long time are statistically likely to stay up, so the table favours them. This impedes an attacker simply displacing old contacts with a flood of new IDs, but does not eliminate Sybil or eclipse attacks.

### Lookup

To find the nodes closest to a target T:

1. Pick the few closest contacts you know (the paper calls this concurrency parameter α, alpha, typically 3) and send each `find_node(T)` (or `get_peers(T)` in BitTorrent) in parallel.
2. Each reply contains the k closest contacts *it* knows.
3. Query the closest ones you haven't asked yet.
4. If a round finds no closer contact, query the remaining unqueried contacts among the k closest seen. Complete when the closest responsive candidates have been checked; handle failed contacts/timeouts rather than stopping after the first non-improving round.

With populated, maintained routing buckets and the model's ID-distribution assumptions, prefix progress supports **O(log n)** lookup scaling, where n is the number of nodes in the network. Big O notation describes how a cost grows as n grows, ignoring constant factors; log n is the logarithm of n, which grows very slowly. Roughly, each round fixes at least one more bit of shared prefix, and the number of bits needed to single out the closest nodes among n is about the base-2 logarithm of n: how many times you can halve n before reaching 1, about 20 for a million nodes. It is not a guarantee that every response halves numeric XOR distance or that an unavailable key will be found. Churn, timeouts, sparse tables and adversaries matter. Measured round counts are omitted because no representative current deployment measurement was verified.

Mainline DHT messages are bencoded dictionaries over UDP (KRPC): `ping`, `find_node`, `get_peers` (returns peers, or closer nodes) and `announce_peer`. To stop arbitrary IPs being announced, `get_peers` replies include an IP-bound **announce token** that the requester must return to the issuing node when announcing. It limits announcement of other IP addresses; it does not prove the announcing peer actually has the content.

> [!warning] Sybil attacks
> Anyone can choose a node ID. An attacker who creates many IDs close to a target info-hash can hide or censor it ("eclipse"). Mitigations include tying IDs to IP addresses (BEP 42) and querying several disjoint paths.

## WebRTC: browsers talking directly

WebRTC lets two browsers exchange audio, video and data directly. The hard part isn't the media; it's getting a packet from one to the other when both are behind NATs.

### Signalling is your problem

WebRTC deliberately **does not specify signalling**. Peers exchange **SDP** offers and answers (session descriptions: codecs, ICE credentials, DTLS fingerprints) through any channel you like, usually a WebSocket to your server. The browser peer-connection API follows JSEP's offer/answer processing. The following fragment is illustrative and wrapped for display: candidate attributes are single lines on the wire, and the fingerprint/password here are abbreviated placeholders.

```
a=ice-ufrag:F7gI
a=ice-pwd:x9cml/YzichV2+XlhiMu8g
a=fingerprint:sha-256 4A:AD:B9:...
a=candidate:1 1 udp 2122260223
  192.168.1.20 54400 typ host
a=candidate:2 1 udp 1686052607
  203.0.113.5 61234 typ srflx
  raddr 192.168.1.20 rport 54400
```

### ICE, STUN and TURN

**ICE** (Interactive Connectivity Establishment, [RFC 8445](https://www.rfc-editor.org/rfc/rfc8445)) gathers **ICE candidates**, addresses where a peer might be reachable:

- **Host candidates**: the device's own interface addresses.
- **Server-reflexive (srflx) candidates**: the public address and port a NAT has mapped, learned by asking a **STUN** server "what address do you see me as?".
- **Relayed candidates**: an address on a **TURN** server that forwards packets for you.

Each side sends its candidates to the other (with **trickle ICE**, as they're found rather than all at once). ICE forms compatible candidate pairs and checks them in a prioritised process using authenticated STUN requests. Type/local preferences and both candidate priorities matter; peer-reflexive candidates may be discovered during checks. The controlling agent nominates a valid pair, rather than every first-success pair being automatically selected.

Why this works through NATs: when A sends a check to B's srflx address, A's NAT creates an outbound mapping. When B's check arrives at A's srflx address, the relevant mapping and filtering state may permit it. Success depends on both NATs' mapping and filtering behaviour; a STUN-observed mapping is not guaranteed to apply to every destination. This is **UDP hole punching**.

STUN messages are tiny: a 20-byte header with the **magic cookie** `0x2112A442` and a 96-bit transaction ID, plus attributes. The server reports your address in **XOR-MAPPED-ADDRESS**, with the port XORed against the cookie's high 16 bits and IPv4 address against the cookie:

```formula
X_port = p ⊕ 0x2112
X_addr = A ⊕ 0x2112A442
where
X_port: the port value as it appears in the attribute
p: your actual mapped port
X_addr: the IPv4 address value as it appears in the attribute
A: your actual mapped IPv4 address, read as one 32-bit number
⊕: XOR (exclusive or), applied bit by bit; applying the same XOR again restores the original
In words: the server scrambles the address with the fixed magic cookie, and the client unscrambles it with the same XOR, so the real address never appears literally in the packet.
```

IPv6 additionally uses the STUN transaction ID, because some NATs "helpfully" rewrote IP addresses they spotted inside packet payloads.

Endpoint-dependent NAT mappings (often called **symmetric NAT**) and restrictive filtering can defeat direct UDP hole punching, but NAT labels alone do not prove that every direct path fails. TURN provides a relay path when one is reachable and permitted. A 1 Mbit/s stream relayed once accounts for about 1 Mbit/s ingress and 1 Mbit/s egress, excluding overhead; provider charging varies. Client-to-TURN transport can use TCP or TLS, including a configured port 443, but this does not guarantee firewall traversal. A universal percentage of calls requiring TURN is absent because no reliable representative measurement was established.

### Security: DTLS-SRTP and SCTP

Encryption is **mandatory** in WebRTC:

- After ICE, peers run a **DTLS** handshake (TLS for UDP) over the chosen path. Each checks that the other's certificate matches the `a=fingerprint` received over signalling. So the signalling channel must be trustworthy; whoever controls it can swap fingerprints and sit in the middle.
- Media keys are exported from DTLS into **SRTP** (DTLS-SRTP, RFC 5764).
- **Data channels** run **SCTP over DTLS over UDP** (RFC 8831), giving multiple streams with reliable or unreliable, ordered or unordered delivery per channel.

With BUNDLE and RTP/RTCP multiplexing, several protocols share an ICE transport. First-byte ranges distinguish outer STUN, DTLS and RTP/RTCP packets; SCTP is inside DTLS, not a separate outer packet type. Connectivity-check headers and ordinary RTP headers are not all encrypted. TURN/TCP paths add their own transport framing.

### Group calls

A two-party call is naturally peer-to-peer. With more people:

| Topology | Each client uploads | Server work |
|---|---|---|
| Mesh | One per other participant | No media forwarding if paths are direct |
| SFU | 1 (or a few) | Forward packets |
| MCU | 1 | Decode, mix, encode |

In a mesh, each client sends its own copy of its stream to every other participant, so upload grows with the size of the call:

```formula
U = (n − 1) × r
U = (5 − 1) × 1.5 Mbit/s = 6 Mbit/s
where
U: the upload rate each client needs, in megabits per second (Mbit/s)
n: the number of participants in the call; here 5
r: the bit rate of one video stream; here 1.5 Mbit/s
Mbit/s: megabits per second, millions of bits per second
In words: with five people, each client uploads four copies of its 1.5 Mbit/s video, 6 Mbit/s in total.
```

So with five people at 1.5 Mbit/s video, a **full mesh** needs each client to upload 6 Mbit/s, before protocol overhead; whether an uplink supports this is deployment-specific. An **SFU** (selective forwarding unit) takes one upload per client and forwards copies, and with **simulcast** each client sends, say, three resolutions so the SFU can give each receiver the one that suits its bandwidth. An SFU reduces client upload replication at the cost of server forwarding. With ordinary per-hop DTLS-SRTP, the SFU holds media keys; an additional mechanism such as SFrame is needed to hide media content from it.

## RTP: real-time media packets

Media in WebRTC (and VoIP, IPTV and many broadcast systems) rides on **RTP** ([RFC 3550](https://www.rfc-editor.org/rfc/rfc3550)) over UDP. UDP allows late media to be discarded without transport head-of-line blocking. RTP can also use other transports; TCP-based fallback can be useful on restrictive networks despite its latency tradeoffs. Whether a late packet is useful depends on the playout deadline.

The fixed header is **12 bytes**:

```
+-+-+-+----+-+-------+----------+
|V|P|X| CC |M|  PT   | Seq (16) |
+-+-+-+----+-+-------+----------+
|        Timestamp (32)         |
+-------------------------------+
|           SSRC (32)           |
+-------------------------------+
|  CSRC list (0-15 x 32 bits)   |
+-------------------------------+
V = version (2 bits), P = padding,
X = extension, CC = CSRC count
```

- **Payload type** (PT, 7 bits) says which codec, mapped in SDP (`a=rtpmap:111 opus/48000/2`).
- **RTP sequence number** (16 bits) increases by 1 per packet: detects loss and reordering.
- **Timestamp** (32 bits) is in **media clock** units, not wall time: **48,000 Hz for Opus** audio and **90,000 Hz for common video payload formats such as H.264**. The advance per packet is the clock rate times the time the packet covers (see the formula after this list). Packet timestamp and marker rules are defined by the payload format.
- **Marker bit** (M) typically flags the last packet of a video frame.
- **SSRC** identifies the stream source; **CSRC** lists contributing sources when a mixer combined streams.

```formula
Δ = f × t
Δ_audio = 48,000 Hz × 0.020 s = 960
Δ_video = 90,000 Hz × (1 / 30) s = 3,000
where
Δ: delta, how much the RTP timestamp advances, in clock ticks
f: the RTP clock rate, in hertz (Hz), ticks per second
t: the media time covered, in seconds (s): 20 ms = 0.020 s for one Opus packet, 1/30 s between pictures for 30 frames per second (fps) video
Δ_audio: the advance per 20 ms Opus packet
Δ_video: the advance between successive pictures of 30 fps video
Hz: hertz, one tick per second
s: seconds
In words: a 20 ms Opus packet moves the 48 kHz timestamp on by 960 ticks, and each 30 fps video picture moves the 90 kHz timestamp on by 3,000 ticks.
```

```python
import struct

pkt = bytes.fromhex(
    "806f1a2b000003c0deadbeef")
b0, b1, seq, ts, ssrc = struct.unpack(
    "!BBHII", pkt[:12])
print(b0 >> 6, b1 & 0x7F, seq, ts)
# 2 111 6699 960
```

This header fixture decodes as version 2, PT 111, sequence 6699 and timestamp 960. By hand, the top two bits of the first byte are the version, and the low 7 bits of the second byte are the payload type:

```formula
V = ⌊b_0 / 64⌋ = ⌊128 / 64⌋ = 2
PT = b_1 − 128 × M
PT = 111 − 128 × 0 = 111
where
V: the RTP version field
b_0: the first byte, 0x80 = 128 in decimal
⌊ ⌋: floor, round down to a whole number; dividing by 64 and rounding down keeps only the top two of the eight bits
b_1: the second byte, 0x6f = 6 × 16 + 15 = 111
M: the marker bit, the top bit of b_1, worth 128 when set; here 0
PT: the payload type, the remaining 7 bits
In words: 0x80 means version 2 with no padding, extension or contributing sources, and 0x6f means marker off and payload type 111.
```

The sequence bytes `1a 2b` give 26 × 256 + 43 = 6,699, and the timestamp bytes `00 00 03 c0` give 3 × 256 + 192 = 960. PT 111 means Opus only if negotiated that way. With an illustrative initial timestamp of zero and one 20 ms Opus frame per packet, 960 is the second frame; real initial timestamps and sequence numbers are randomised. This snippet parses only the fixed header, not a complete validated RTP packet.

### RTCP: feedback

RTP's companion, **RTCP**, sends periodic reports:

- **Sender reports** map the RTP timestamp to wall-clock (NTP format) time, which is how receivers **lip-sync** audio and video streams that have unrelated RTP clocks.
- **Receiver reports** give fraction lost, cumulative loss and **interarrival jitter**, a running estimate of how much packet transit times vary (formula below).
- **Round-trip time**: the sender works out the network round trip from the report it gets back, subtracting the time the receiver held it (formula below).

The jitter estimate is updated for every packet, moving one sixteenth of the way towards the latest measurement:

```formula
D = (R_j − R_i) − (S_j − S_i)
J_new = J + (|D| − J) / 16
where
D: the change in transit time between packets i and j: how much later (or earlier) packet j arrived than its send timestamp predicts
R_i, R_j: the arrival times of packets i and j, measured in RTP timestamp units
S_i, S_j: the RTP timestamps carried in packets i and j
J: the previous jitter estimate, in RTP timestamp units
J_new: the updated estimate
|D|: the size of D, ignoring its sign
In words: if packets keep arriving with uneven spacing, J climbs towards the typical unevenness; dividing by 16 smooths out one-off spikes.
```

The round-trip time uses three values carried in or measured around the reports:

```formula
RTT = A − LSR − DLSR
where
RTT: the round-trip network time between sender and receiver
A: when the receiver report arrived back at the sender, by the sender's clock
LSR: last sender report: the timestamp of the sender report the receiver last got, echoed back (the middle 32 bits of its NTP timestamp)
DLSR: delay since last sender report: how long the receiver held that report before replying, in units of 1/65,536 second
In words: take the time from sending the report to getting the answer, and subtract the time the receiver sat on it; what is left is time spent on the network.
```

A and LSR come from the sender's own clock, so the two machines' clocks need not agree. On the wire A and LSR use the same compact representation, so the subtraction needs modular arithmetic (it must handle the counters wrapping round) and assumes the clocks run at stable rates.

WebRTC adds RTCP feedback messages: **NACK** (please resend packet 6702, if there's time), **PLI** (picture loss indication, allowing an encoder to respond with recovery information such as an intra picture) and transport-wide congestion feedback, which drives Google Congestion Control in adjusting the encoder's bitrate.

On the receiving side, a **jitter buffer** holds packets briefly to reorder them and smooth out variable delay. It is a direct trade: a bigger buffer survives more jitter but adds latency. A suitable latency budget depends on the application; a universal 150 ms cutoff is omitted because this review did not establish one applicable to every interactive call.

## Key takeaways
- BitTorrent v1 identifies content by the SHA-1 info-hash of the bencoded info dictionary, verifies every piece against its hash, and uses rarest-first and tit-for-tat choking.
- Kademlia uses XOR distance and k-buckets to support logarithmic lookup under maintained-routing assumptions; it prefers long-lived contacts and is exposed to Sybil attacks.
- WebRTC leaves signalling to you; ICE tries host, STUN-learned server-reflexive and TURN-relayed candidates, and tests connectivity rather than inferring success solely from a NAT label.
- WebRTC encrypts media and data content, while some transport headers and connectivity checks remain visible: DTLS keyed by fingerprints from SDP, SRTP for media, SCTP over DTLS for data channels.
- RTP's 12-byte header carries sequence numbers for loss detection and media-clock timestamps (48 kHz Opus, 90 kHz video); RTCP gives loss, jitter, RTT and lip-sync.

## Further reading
- [BEP 3: The BitTorrent Protocol Specification](https://www.bittorrent.org/beps/bep_0003.html)
- [BEP 5: DHT Protocol](https://www.bittorrent.org/beps/bep_0005.html)
- [Kademlia: A Peer-to-peer Information System Based on the XOR Metric (paper)](https://pdos.csail.mit.edu/~petar/papers/maymounkov-kademlia-lncs.pdf)
- [WebRTC for the Curious](https://webrtcforthecurious.com/)
- [RFC 8445: Interactive Connectivity Establishment — IETF](https://www.rfc-editor.org/rfc/rfc8445)
- [RFC 3550: RTP — IETF](https://www.rfc-editor.org/rfc/rfc3550)
