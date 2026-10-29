---
id: ip-dhcp-lease-timers
title: Renew and rebind a DHCP lease
level: intermediate
minutes: 3
sourceLesson: ip-dhcp
summary: Predict what a client does at each lease threshold and distinguish renewal, rebinding, expiry and reservations.
---

A DHCP address is borrowed, not owned. This lesson follows what a client does as its lease ages, and what happens when its server disappears.

## Leases

Dynamic address assignment uses **DHCP leases**, allowing addresses to be reused after clients release them or leases expire. DHCP also supports other allocation arrangements; reuse depends on concurrent demand and lease retention, not just visitor count.

For a finite lease, nominal default timers are below. Servers can supply different T1/T2 values; RFC 2131 recommends random timing variation, and a client may seek renewal early:

- **T1**, at 50% of the lease: start **renewing**. Unicast a Request directly to the server that granted the lease.
- **T2**, at 87.5% of the lease: if the server hasn't answered, start **DHCP rebinding**. Broadcast a Request so another server with sufficient state and authority may extend it.

If the lease expires with no answer, the client must stop using the address and start again from Discover. The timers are measured from the lease-start reference (not simply from delayed ACK arrival).

For a 24-hour lease starting at midnight, with the nominal defaults, that means renewing from 12:00, rebinding from 21:00 and expiry at 24:00. The design asks the original server first, from halfway through, and only from seven eighths onwards lets any other server that shares the lease state extend it, leaving a final window before the client loses its address.

> [!analogy] Real-world analogy: A library loan
> You borrow a book for four weeks. Halfway through, you ask the branch that lent it to extend the loan. If that branch is closed, near the end you ask any branch in the network, which can see the shared records. If nobody extends it by the due date, the book must go back.
>
> **How it maps:** The loan period is the lease; asking the lending branch is renewal at T1 (a unicast request to the original server); asking any branch is rebinding at T2 (a broadcast request any authorised server can answer); returning the book is expiry, when the client stops using the address.
>
> **Where it stops:** A late library book earns a fine; a DHCP client simply loses its address and rediscovers. Libraries may refuse extensions to some borrowers; DHCP servers decide using pool availability and policy, and often hand the same client the same address again.

A client leaving cleanly can send **DHCPRELEASE**, but many just disappear and let the lease expire.

Lease length is a trade-off. Short leases (an hour) recycle addresses quickly in busy guest networks but generate more traffic and make the server more critical. Long leases (days) suit stable office networks.

Servers usually hand the same client the same address again where they can, keyed on its MAC or client identifier. **DHCP reservations** associate a stable address with configured client identification, which may be a MAC or a client identifier depending on the server. MAC randomisation or identifier changes can affect that mapping.

## Key takeaways
- Nominal T1/T2 fractions are 50% and 87.5% of the finite lease.
- Overrides, randomisation and early renewal change real timing.
- Renewal targets the original server; rebinding seeks an authorised available server.
- Expiry ends permission to use the address; reservations depend on configured client identity.

## Further reading
- [RFC 2131: Dynamic Host Configuration Protocol](https://www.rfc-editor.org/rfc/rfc2131)
- [RFC 2132: DHCP Options](https://www.rfc-editor.org/rfc/rfc2132)
