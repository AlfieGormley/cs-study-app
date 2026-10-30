---
id: wm-fabric-flow-selection
title: ECMP and stable per-flow selection
level: intermediate
minutes: 3
summary: A stable hash and stable next-hop mapping keep a flow on one selected path.
sourceLesson: wm-datacentre
---

A leaf-spine fabric has several equally good paths between racks. Using them all without scrambling the order of each connection's packets is the job of equal-cost multi-path forwarding, and the way it chooses a path explains both its strengths and its blind spots.

## ECMP: using all the paths

With routing, a leaf sees, say, four routes to the destination rack's prefix, all with the same cost. **Equal-cost multi-path** (ECMP) can install multiple eligible next hops, subject to configuration and implementation limits. The forwarding lookup selects a next hop for each packet, commonly using a flow-stable hash.

Choosing per *packet* can reorder TCP segments, which TCP treats as possible loss. Implementations therefore commonly select per **packet flow**: they hash header fields, usually the 5-tuple, and use the hash to pick a next hop. The simplest mapping takes the remainder after dividing by the number of paths:

```formula essential
i = h mod N
where
i: the index of the chosen next hop (uplink), from 0 to N − 1
h: the flow's hash: a large whole number computed from its 5-tuple, the same for every packet of the flow
N: the number of equal-cost next hops
mod: modulo: the remainder after whole-number division, so 11 mod 4 = 3 because 11 = 4 × 2 + 3
In words: every packet of a flow has the same hash, so it always gets the same remainder and the same uplink.
```

The Python below uses CRC-32 as the hash; `%` is Python's mod operator:

```python
import zlib

def pick_uplink(flow, n_paths):
    if (type(n_paths) is not int
            or n_paths < 1):
        raise ValueError("bad path count")
    # Same ordered headers give the same
    # key.
    key = "|".join(map(str, flow)).encode()
    # Modulo maps the checksum to an uplink.
    return zlib.crc32(key) % n_paths

flows = [("10.0.1.5", 40001 + i,
          "10.0.9.7", 443, "tcp")
         for i in range(6)]
print([pick_uplink(f, 4) for f in flows])
# Uplink IDs: collisions are permitted.
# [1, 3, 2, 2, 3, 1]
```

With unchanged inputs and next-hop mapping, a flow selects the same next hop. This avoids reordering caused by this path selector but does not guarantee no reordering elsewhere or during changes. Distinct flows can have different keys and still collide. Note that uplink 0 got nothing here: hashing is statistical, not a perfect balance. The selector also ignores load: it does not know whether the chosen uplink is already busy. The next lesson looks at what that costs.

## Key takeaways
- A stable hash and stable next-hop mapping keep a flow on one selected path.
- Different flows can collide, so a selector does not guarantee equal byte load.

## Further reading
- [Equal-cost multi-path routing — Wikipedia](https://en.wikipedia.org/wiki/Equal-cost_multi-path_routing)
- [RFC 2992: Analysis of an Equal-Cost Multi-Path Algorithm](https://www.rfc-editor.org/rfc/rfc2992)
