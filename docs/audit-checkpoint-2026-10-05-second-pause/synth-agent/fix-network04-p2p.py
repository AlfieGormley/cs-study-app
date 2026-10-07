exec(open('/tmp/network04-helper.py').read());n='app-p2p-webrtc'
def m(a,b,why='Correct protocol scope, security assumptions or unsupported guarantee.'):md(n,a,b,why)
m('how Kademlia\'s XOR metric finds anything in O(log n) hops','how Kademlia\'s XOR metric supports logarithmic lookup under its routing assumptions')
m('Peer-to-peer systems turn every participant into a server too','Peer-to-peer systems let participants also serve data or resources')
m('A `.torrent` file is','For **BitTorrent v1**, a `.torrent` file is')
m('Dictionary keys must be **sorted**, so every encoder produces identical bytes for the same data.','Dictionary keys are byte strings and must be **sorted by raw bytes**. Canonical integer and string-length encodings also matter; hash the original encoded `info` substring or fully validate input before re-encoding.')
m('`piece length`, typically 256 KiB to a few MiB,','`piece length`, chosen when the torrent is created (256 KiB is one example),')
m('Because it covers the piece hashes, the info-hash commits to every byte of the content.','It ties the metadata to the piece hashes, subject to SHA-1\'s security limitations. An info-hash is not a publisher identity or proof that downloaded content is safe.')
a='''    return b"d" + b"".join(
        bencode(k) + bencode(v)
        for k, v in sorted(x.items())
    ) + b"e"'''
b='''    if isinstance(x, dict):
        pairs = []
        for k, v in x.items():
            if isinstance(k, str):
                k = k.encode("utf-8")
            if not isinstance(k, bytes):
                raise TypeError("key type")
            pairs.append((k, v))
        keys = [k for k, _ in pairs]
        if len(set(keys)) != len(keys):
            raise ValueError("duplicate key")
        pairs.sort(key=lambda pair: pair[0])
        return b"d" + b"".join(
            bencode(k) + bencode(v)
            for k, v in pairs) + b"e"
    raise TypeError("unsupported type")'''
m(a,b,'Validate dictionary key types and sort encoded byte keys; avoid unsupported objects and duplicate encoded keys.')
m('if isinstance(x, int):','if type(x) is int:','Reject bool rather than silently encoding it as a protocol integer.')
m('so pieces can be verified in 16 KiB blocks and identical files share hashes across torrents.','with 16 KiB leaves (the final block can be shorter). With the necessary hashes/proofs, blocks can be verified against the per-file root; identical file contents share that root. The v2 info-hash is SHA-256, with protocol-specific truncation where a 20-byte identifier is required.')
m('A magnet link carries only the info-hash;','A magnet link can carry an info-hash and optional parameters such as tracker URLs or a display name;')
m('every message is a 4-byte length, a 1-byte ID and a payload:','non-keepalive messages carry a 4-byte big-endian length, a 1-byte ID and a payload:')
m('| 2 / 3 | (not) interested | none |','| 2 / 3 | interested / not interested | none |','The original table reversed the message labels.')
m('You never need to trust a peer.','This detects mismatching content without trusting each supplier, but still depends on trusted metadata and hash assumptions. A mixed-source bad piece does not identify which contributor supplied a bad block.')
m('This keeps every piece available in the swarm','This promotes availability of scarce pieces but cannot guarantee that every piece remains online')
m('Every 10 seconds, the classic algorithm unchokes the **4 peers giving you the best download rate**, and every 30 seconds it **optimistically unchokes** one random peer, which lets newcomers with nothing to trade get started and lets you discover faster partners.','BEP 3 describes decisions on a 10-second cadence and rotation of an optimistic slot every 30 seconds. The optimistic interested peer counts within the four allowed interested downloaders, rather than being an unconditional fifth slot; new connections receive selection bias. Seeders use upload performance rather than download reciprocation. Client policies can differ.')
m('It has millions of nodes.','A current population estimate is absent because this review did not establish a reliable measurement.')
m('so lookups from different nodes converge on the same nodes. A key is stored on the k nodes whose IDs are closest to it.','so all nodes can consistently rank IDs for a target. Successful convergence also requires adequate live routing information. Original Kademlia replicates values near the k closest nodes; Mainline DHT stores peer contact information associated with the hash.')
m('Bucket i holds','In the basic distance-bucket model, bucket i holds')
m('So a node knows many contacts close to it and progressively fewer, but at least some, in each exponentially larger region further away.','The capacity per bucket is bounded by k; contact **density** falls across exponentially larger distance regions. Mainline DHT uses a splitting routing-table implementation rather than a literal permanently allocated array of 160 buckets.')
m('This also resists attackers flooding the table with fresh fake nodes.','This impedes simple replacement flooding but does not eliminate Sybil or eclipse attacks.')
m("4. Stop when a round doesn't find anyone closer.","4. If a round finds no closer contact, query the remaining unqueried contacts among the k closest seen. Complete when the closest responsive candidates have been checked; handle failed contacts/timeouts rather than stopping after the first non-improving round.")
m('Each step at least halves the distance (fixes at least one more leading bit), so a lookup takes **O(log n)** steps. With 10 million nodes, log2(10^7) ≈ 23, but because each hop typically fixes several bits at once in practice, lookups usually complete in a handful of rounds.','With populated, maintained routing buckets and the model\'s ID-distribution assumptions, prefix progress supports **O(log n)** lookup scaling. It is not a guarantee that every response halves numeric XOR distance or that an unavailable key will be found. Churn, timeouts, sparse tables and adversaries matter. Measured round counts are omitted because no representative current deployment measurement was verified.')
m('a short-lived **token** that the requester must present when announcing.','an IP-bound **token** that the requester must return to the issuing node when announcing. It limits announcement of other IP addresses; it does not prove the announcing peer actually has the content.')
m('The browser API (JSEP) generates and consumes the SDP.','The browser peer-connection API follows JSEP\'s offer/answer processing. The following fragment is illustrative and wrapped for display: candidate attributes are single lines on the wire, and the fingerprint/password here are abbreviated placeholders.')
m('ICE then pairs local and remote candidates, sorts pairs by priority (host > srflx > relay) and runs **connectivity checks**: STUN binding requests on each pair, authenticated with the ice-ufrag/ice-pwd from SDP. The first pairs that succeed in both directions are nominated.','ICE forms compatible candidate pairs and checks them in a prioritised process using authenticated STUN requests. Type/local preferences and both candidate priorities matter; peer-reflexive candidates may be discovered during checks. The controlling agent nominates a valid pair, rather than every first-success pair being automatically selected.')
m("the mapping exists and A's NAT lets it in.","the relevant mapping and filtering state may permit it. Success depends on both NATs\' mapping and filtering behaviour; a STUN-observed mapping is not guaranteed to apply to every destination.")
m('XORed with the magic cookie,','with the port XORed against the cookie\'s high 16 bits and IPv4 address against the cookie; IPv6 additionally uses the transaction ID,')
a='Hole punching fails with **symmetric NATs** (which pick a new external port for every destination) and with firewalls that block UDP. Then only the **TURN relay** works: all media goes through your server. A meaningful share of real calls need TURN (estimates commonly range from around 10 to 20%), and it costs bandwidth: every 1 Mbit/s stream relayed through TURN costs your server 1 Mbit/s in and 1 Mbit/s out. TURN can run over TCP or TLS on port 443 as a last resort.'
b='Endpoint-dependent NAT mappings (often called **symmetric NAT**) and restrictive filtering can defeat direct UDP hole punching, but NAT labels alone do not prove that every direct path fails. TURN provides a relay path when one is reachable and permitted. A 1 Mbit/s stream relayed once accounts for about 1 Mbit/s ingress and 1 Mbit/s egress, excluding overhead; provider charging varies. Client-to-TURN transport can use TCP or TLS, including a configured port 443, but this does not guarantee firewall traversal. A universal percentage of calls requiring TURN is absent because no reliable representative measurement was established.'
m(a,b)
m('Everything, including STUN checks, DTLS, SRTP and SCTP, is usually multiplexed on **one UDP port** ("bundle" and rtcp-mux), with receivers telling them apart by the first byte.','With BUNDLE and RTP/RTCP multiplexing, several protocols share an ICE transport. First-byte ranges distinguish outer STUN, DTLS and RTP/RTCP packets; SCTP is inside DTLS, not a separate outer packet type. Connectivity-check headers and ordinary RTP headers are not all encrypted. TURN/TCP paths add their own transport framing.')
m('| Mesh | n − 1 streams | None |','| Mesh | n − 1 streams | No media forwarding if paths are direct |')
m('beyond many home uplinks.','before protocol overhead; whether an uplink supports this is deployment-specific.')
m('Most video conferencing (Google Meet and Jitsi, for example) uses SFUs.','An SFU reduces client upload replication at the cost of server forwarding. With ordinary per-hop DTLS-SRTP, the SFU holds media keys; an additional mechanism such as SFrame is needed to hide media content from it.')
m('TCP would be wrong here: a retransmitted audio packet that arrives 300 ms late is useless, and waiting for it stalls everything behind it.','UDP allows late media to be discarded without transport head-of-line blocking. RTP can also use other transports; TCP-based fallback can be useful on restrictive networks despite its latency tradeoffs. Whether a late packet is useful depends on the playout deadline.')
m('**90,000 Hz for video**','**90,000 Hz for common video payload formats such as H.264**')
m('at 30 frames per second each video frame advances it by 3,000, and every packet of the same frame shares one timestamp.','for constant-rate 30 fps video using a 90 kHz RTP clock, successive picture sampling times differ by 3,000 ticks. Packet timestamp and marker rules are defined by the payload format.')
m('Version 2, payload type 111 (commonly Opus in WebRTC), sequence 6699, timestamp 960: the second 20 ms Opus frame if the stream started at 0.','This header fixture decodes as version 2, PT 111, sequence 6699 and timestamp 960. PT 111 means Opus only if negotiated that way. With an illustrative initial timestamp of zero and one 20 ms Opus frame per packet, 960 is the second frame; real initial timestamps and sequence numbers are randomised. This snippet parses only the fixed header, not a complete validated RTP packet.')
m('LSR is the timestamp of its last sender report echoed back, and DLSR is how long the receiver held it.','LSR is the compact middle-32-bit NTP timestamp echoed from the last sender report, and DLSR is elapsed time since receiving it, in 1/65536-second units. A uses the same compact representation, with modular arithmetic and clock-stability assumptions.')
m('**PLI** (picture loss, send a new keyframe)','**PLI** (picture loss indication, allowing an encoder to respond with recovery information such as an intra picture)')
m('Interactive calls aim for mouth-to-ear delay under about 150 ms.','A suitable latency budget depends on the application; a universal 150 ms cutoff is omitted because this review did not establish one applicable to every interactive call.')
m('BitTorrent identifies content by the SHA-1 info-hash','BitTorrent v1 identifies content by the SHA-1 info-hash')
m('so any key is found in O(log n) steps','to support logarithmic lookup under maintained-routing assumptions')
m('and hole punching fails on symmetric NATs.','and tests connectivity rather than inferring success solely from a NAT label.')
m('All WebRTC traffic is encrypted:','WebRTC encrypts media and data content, while some transport headers and connectivity checks remain visible:')
