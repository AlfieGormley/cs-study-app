---
id: app-rtp-header-and-clocks
title: "RTP packet fields and media-clock timestamps"
level: advanced
minutes: 4
sourceLesson: app-p2p-webrtc
summary: "RTP sequence numbers count packets while timestamps follow payload-specific media clocks."
---

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
Δ = ft
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
# Read only the twelve-byte fixed header.
b0, b1, seq, ts, ssrc = struct.unpack(
    "!BBHII", pkt[:12])
# Isolate version and payload-type bits.
print(b0 >> 6, b1 & 0x7F, seq, ts)
# 2 111 6699 960
```

This header fixture decodes as version 2, PT 111, sequence 6699 and timestamp 960. By hand, the top two bits of the first byte are the version, and the low 7 bits of the second byte are the payload type:

```formula
V = ⌊b_0 / 64⌋ = ⌊128 / 64⌋ = 2
PT = b_1 − 128M
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

## Key takeaways
- RTP sequence numbers count packets while timestamps follow payload-specific media clocks.
- A fixed-header parser illustrates fields but does not validate a complete RTP packet.

## Further reading
- [RFC 3550](https://www.rfc-editor.org/rfc/rfc3550)
- [RFC 7587](https://www.rfc-editor.org/rfc/rfc7587)
- [RFC 6184](https://www.rfc-editor.org/rfc/rfc6184)
