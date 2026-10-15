---
id: nf-stp-port-roles
sourceLesson: nf-arp-switching
title: Spanning-tree ports and path cost
level: intermediate
minutes: 3
summary: Choose root and designated ports and trace the equal-cost triangle.
---

### Step 2: each switch picks a root port

Every non-root switch chooses one **root port**: its port with the lowest total **path cost** to the root (the sum of the costs of every link on the way). Costs come from link speed; in the commonly used short path-cost table, 100 Mbit/s costs 19, 1 Gbit/s costs 4 and 10 Gbit/s costs 2. After equal root IDs and path costs, ties use the sender bridge ID, sender port ID, and finally local port ID. Costs may be configured; long path-cost values differ.

### Step 3: each link picks a designated port

On each segment, the port advertising the best root information becomes the **designated port**. With the same root ID, compare root path cost, then sender bridge ID and sender port ID. Root and designated ports forward data once the relevant state transitions have completed; a role alone does not imply immediate forwarding. In the simple point-to-point topology below, the root ends of inter-switch links are designated. Shared segments and multiple ports attached to one LAN segment need the full port-role rules.

In this stable classic-STP example, an enabled redundant port that is neither root nor designated is **blocked**: it still listens to BPDUs but forwards no data. During convergence, even a root or designated port can temporarily be listening or learning.

### The triangle, worked

All three links are 1 Gbit/s (cost 4), all priority/system-ID fields are equal, and the MAC ordering is S1 < S2 < S3.

| Switch | Cost to root | Root port |
|---|---|---|
| S1 | 0 (root) | none |
| S2 | 4 | to S1 |
| S3 | 4 | to S1 |

The S2–S3 link: both ends have cost 4, so the tie goes to the lower bridge ID, S2. S2's end is designated; S3's end is neither root nor designated, so it **blocks**.

```
        S1 (root)
       /  \
      R    R
     S2 -D-X- S3
 R: root port   D: designated
 X: blocked
```

If the S1–S3 link fails, S3 stops receiving BPDUs from S1, its blocked port becomes its new root port, and traffic flows via S2.

## Key takeaways
- Non-root switches choose a root port using full path cost and tie-breakers.
- A designated port forwards for each segment; blocking a redundant endpoint removes the loop.

## Further reading
- [RFC 826: An Ethernet Address Resolution Protocol](https://www.rfc-editor.org/rfc/rfc826)
- [RFC 5227: IPv4 Address Conflict Detection](https://www.rfc-editor.org/rfc/rfc5227)
- [Address Resolution Protocol — Wikipedia](https://en.wikipedia.org/wiki/Address_Resolution_Protocol)
- [ARP spoofing — Wikipedia](https://en.wikipedia.org/wiki/ARP_spoofing)
- [Spanning Tree Protocol — Wikipedia](https://en.wikipedia.org/wiki/Spanning_Tree_Protocol)
- [Broadcast storm — Wikipedia](https://en.wikipedia.org/wiki/Broadcast_storm)

- [Linux ARP implementation and neighbour parameters](https://man7.org/linux/man-pages/man7/arp.7.html)
- [RFC 9568: VRRP version 3](https://www.rfc-editor.org/rfc/rfc9568.html)
- [Cisco: Understand RSTP](https://www.cisco.com/c/en/us/support/docs/lan-switching/spanning-tree-protocol/24062-146.html)
- [IEEE: 802.1D consolidation into 802.1Q](https://www.ieee802.org/1/files/public/docs2021/maint-parsons-802.1D_withdrawal_status-0321-v1.pdf)
