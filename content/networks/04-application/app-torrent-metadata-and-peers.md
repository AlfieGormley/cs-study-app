---
id: app-torrent-metadata-and-peers
title: "BitTorrent metadata, bencoding and peer discovery"
level: advanced
minutes: 3
sourceLesson: app-p2p-webrtc
summary: "BitTorrent v1 hashes the bencoded info dictionary, which commits to piece hashes rather than publisher identity."
---

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

> [!analogy] Real-world analogy: A packing list with a fingerprint for every box
> Someone ships a flat-pack wardrobe in many boxes, which you may collect from different strangers. The packing list gives a unique fingerprint for each box, and the whole list has its own fingerprint, which a friend you trust read out to you.
>
> **How it maps:** The packing list is the `info` dictionary, each box fingerprint is a piece hash, and the fingerprint of the whole list is the info-hash. Knowing the info-hash lets you check a list fetched from strangers, and the list then lets you check every box.
>
> **Where it stops:** The fingerprints prove the boxes match the list, not that the wardrobe is safe or who designed it. And because the list's fingerprint is taken over its exact bytes, everyone must write the list identically, which is why bencoding sorts dictionary keys.

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
        # Reject str/bytes key collisions.
        if len(set(keys)) != len(keys):
            raise ValueError("same key")
        # Canonical order uses key bytes.
        pairs.sort(key=lambda pair: pair[0])
        return b"d" + b"".join(
            bencode(k) + bencode(v)
            for k, v in pairs) + b"e"
    raise TypeError("unsupported type")

# The output is sorted: cow, then spam.
print(bencode({"spam": ["a", 42],
               "cow": "moo"}))
# b'd3:cow3:moo4:spaml1:ai42eee'
```

BitTorrent v2 (BEP 52) replaces SHA-1 with **SHA-256 Merkle trees** per file, with 16 KiB leaves (the final block can be shorter). With the necessary hashes/proofs, blocks can be verified against the per-file root; identical file contents share that root. The v2 info-hash is SHA-256, with protocol-specific truncation where a 20-byte identifier is required.

### Finding peers

A client finds others through a **BitTorrent tracker** (an HTTP or UDP server returning peer lists for an info-hash), the **DHT** (below) or **peer exchange** with already-connected peers. A magnet link can carry an info-hash and optional parameters such as tracker URLs or a display name; the client fetches the `info` dictionary itself from peers (BEP 9) and verifies it against the hash.

## Key takeaways
- BitTorrent v1 hashes the bencoded info dictionary, which commits to piece hashes rather than publisher identity.
- Trackers, DHT lookups and peer exchange discover suppliers; magnet metadata must match its hash.

## Further reading
- [BEP 3](https://www.bittorrent.org/beps/bep_0003.html)
- [BEP 9](https://www.bittorrent.org/beps/bep_0009.html)
- [BEP 52](https://www.bittorrent.org/beps/bep_0052.html)
