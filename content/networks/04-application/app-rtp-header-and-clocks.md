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
- **Timestamp** (32 bits) is in **media clock** units, not wall time: **48,000 Hz for Opus** audio and **90,000 Hz for common video payload formats such as H.264**. It advances by the clock rate times the media time a packet covers, so a 20 ms Opus packet moves it on by 960 (Opus uses the 48 kHz RTP clock whatever sampling rate the audio itself uses) and each picture of 30-frames-per-second video by 3,000. Packet timestamp and marker rules are defined by the payload format.
- **Marker bit** (M) typically flags the last packet of a video frame.
- **SSRC** identifies the stream source; **CSRC** lists contributing sources when a mixer combined streams.

The two counters answer different questions. The sequence number says how many packets were sent, so a gap in it means loss or reordering. The timestamp says how much media time has passed, so it can jump without any loss: an Opus sender using discontinuous transmission (DTX) sends nothing during silence, and the next packet's timestamp leaps ahead while its sequence number is the next one in line. Several packets of one video frame share the same timestamp.

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

This header fixture decodes as version 2, PT 111, sequence 6699 and timestamp 960. The top two bits of the first byte are the version, and the second byte holds the marker bit on top of a 7-bit payload type, so a parser must mask the marker off. PT 111 means Opus only if SDP negotiated that mapping. With an illustrative initial timestamp of zero and one 20 ms Opus frame per packet, 960 is the second frame; real initial timestamps and sequence numbers are randomised. This snippet parses only the fixed header, not a complete validated RTP packet.

## Key takeaways
- RTP sequence numbers count packets while timestamps follow payload-specific media clocks.
- A fixed-header parser illustrates fields but does not validate a complete RTP packet.

## Further reading
- [RFC 3550](https://www.rfc-editor.org/rfc/rfc3550)
- [RFC 7587](https://www.rfc-editor.org/rfc/rfc7587)
- [RFC 6184](https://www.rfc-editor.org/rfc/rfc6184)
