---
id: app-torrent-wire-and-selection
title: "BitTorrent wire messages, verification and choking"
level: advanced
minutes: 3
sourceLesson: app-p2p-webrtc
summary: "BitTorrent peers handshake, pipeline block requests and verify completed pieces against trusted metadata."
---

A BitTorrent v1 torrent identifies pieces through SHA-1 hashes in trusted metainfo. Peers advertise what they have and trade blocks; the wire protocol and selection policies perform different jobs.

### The peer wire protocol

Peers talk over TCP (or uTP, a UDP-based protocol with delay-based congestion control designed to yield to other traffic). The connection starts with a **68-byte handshake**:

```
1   pstrlen = 19
19  "BitTorrent protocol"
8   reserved (extension bits)
20  info_hash
20  peer_id
```

The fixed length lets a receiver read exactly 68 bytes, then check that the info-hash names a torrent it is serving before going further.

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

A length of 0 is a keep-alive. Ordinary request blocks are **16 KiB blocks**, with shorter blocks where a piece ends, and clients keep several requests outstanding per peer (pipelining again, for the same window/RTT reason as SFTP).

Each completed piece is hashed and compared with the metainfo. A mismatch means the piece is discarded and re-downloaded, and the peers that supplied it may be banned. This detects mismatching content without trusting each supplier, but still depends on trusted metadata and hash assumptions. A mixed-source bad piece does not identify which contributor supplied a bad block.

### Piece selection and choking

Two policies make swarms work:

- **Rarest first.** Download the pieces that the fewest of your peers have. This promotes availability of scarce pieces but cannot guarantee that every piece remains online and makes you useful to others sooner.
- **Tit-for-tat choking.** You upload only to a few peers at a time. BEP 3 describes decisions on a 10-second cadence and rotation of an optimistic slot every 30 seconds. The optimistic interested peer counts within the four allowed interested downloaders, rather than being an unconditional fifth slot; new connections receive selection bias. Seeders use upload performance rather than download reciprocation. Client policies can differ.

> [!analogy] Real-world analogy: A swap shop with a free-sample table
> At a swap shop, regulars trade mostly with the people who have recently given them the most. To give newcomers a chance, each trader also hands a free item to one stranger at a time, rotating every so often. A newcomer who receives something can start trading.
>
> **How it maps:** Trading with your best recent partners is tit-for-tat choking; the free item is the optimistic unchoke. Rarest first is choosing to pick up the items few people have, so you have something others want and the item survives if its owner leaves.
>
> **Where it stops:** BitTorrent's partners are judged on measured transfer rates and re-evaluated on a regular cadence (every ten seconds in BEP 3's description), not on goodwill. Seeders, which want nothing back, simply favour peers they can upload to well.

Near the end, **endgame mode** requests the last few blocks from every peer that has them and cancels duplicates on arrival, so one slow peer doesn't hold up completion.

## Key takeaways
- BitTorrent peers handshake, pipeline block requests and verify completed pieces against trusted metadata.
- Rarest-first and optimistic unchoking improve exchange without guaranteeing piece availability.

## Further reading
- [BEP 3](https://www.bittorrent.org/beps/bep_0003.html)
- [BEP 29](https://www.bittorrent.org/beps/bep_0029.html)
