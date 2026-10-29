---
id: net-dns-resolution-transport
title: "DNS referrals and transport"
level: basic
minutes: 3
summary: "Follow a recursive resolver and explain why DNS needs both UDP and TCP."
sourceLesson: net-dns
---
DNS (the Domain Name System) maps names like `api.example.com` to the addresses and services behind them. It's one of the oldest and largest distributed databases on the internet, and it's on the critical path of almost every request.

For a system designer, DNS matters for three reasons:

- It adds latency to the first request.
- Its **caching** decides how fast you can move traffic during a failover.
- It's a cheap, global **load-balancing and routing layer**.

## The cast of characters

| Component | Role |
|---|---|
| Stub resolver | Library in your OS; asks one resolver |
| Recursive resolver | Does the legwork, caches answers |
| Root servers | Know who runs each TLD |
| TLD servers | Know who runs each domain |
| Authoritative server | Holds the actual records |

There are 13 root server *identities* (a.root-servers.net to m.root-servers.net), run by 12 independent organisations. Each identity is served from many sites via **anycast**, and together they are deployed at many locations worldwide (the site count changes over time), so "13 root servers" is a naming detail, not a capacity limit. (The number 13 comes from fitting all their addresses into one small, original-size DNS response.)

## A full resolution, step by step

```
App -> Stub -> Recursive resolver
                 |
   1 "www.example.com?"   -> Root
     "ask .com servers"   <-
   2 "www.example.com?"   -> .com TLD
     "ask ns1.example.com"<-
   3 "www.example.com?"   -> ns1.example
     "A 192.0.2.10"       <-
                 |
          cache + return
```

1. The recursive resolver asks a **root server**, which replies with a *referral* to the `.com` servers.
2. It asks a **`.com`** server, which refers it to `example.com`'s name servers (from the `NS` records registered with the registrar).
3. It asks the **authoritative server**, which returns the answer.

The recursive resolver does **iterative queries** (it follows referrals itself); the stub makes a single **recursive DNS query** ("give me the final answer"). In practice, the root and TLD referrals are almost always cached, so most lookups need only step 3 or are answered entirely from cache.

> [!analogy] Real-world analogy: A librarian following "ask over there" notes
> You ask the help desk one question and wait. The librarian doesn't know the answer, so they check the main directory, which says "ask the science floor"; the science floor says "ask the chemistry desk"; the chemistry desk has the answer. The librarian writes the useful notes in a notebook so the next person's question is quicker.
>
> **How it maps:** you are the stub resolver making one recursive request. The librarian is the recursive resolver making iterative queries. The directory, the floor and the desk are the root, TLD and authoritative servers, each returning a referral or the final answer, and the notebook is the resolver's cache.
>
> **Where it stops:** each cached DNS answer carries its own TTL and must be discarded when it expires, unlike a notebook entry. Delegation follows zone boundaries chosen by domain owners rather than subject areas, and each "desk" is usually several servers, often anycast copies sharing one address.

DNS normally runs over **UDP port 53**: one small packet each way, no handshake. If an answer is too big for the UDP size the client advertised (EDNS(0) lets clients advertise larger buffers; around 1,232 bytes is the common safe default since DNS Flag Day 2020, to avoid IP fragmentation), the server sets the *truncated* flag and the client retries over **TCP**. TCP support is mandatory, not optional (RFC 7766), and matters for DNSSEC-signed answers. DNS is also increasingly carried over TLS (DNS over TLS, DoT) or HTTPS (DNS over HTTPS, DoH) for privacy.

## Key takeaways

- A stub asks for a final answer; the recursive resolver follows referrals itself.
- Root server identities are served from many anycast locations.
- Large or truncated DNS responses need working TCP fallback; blocking TCP 53 can break resolution.

## Further reading

- [Domain names: implementation and specification (RFC 1035)](https://www.rfc-editor.org/rfc/rfc1035)
- [DNS transport over TCP (RFC 7766)](https://www.rfc-editor.org/rfc/rfc7766)
- [Root server operators](https://root-servers.org/)
