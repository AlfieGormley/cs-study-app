---
id: ip-dhcp-lease-timers
title: Renew and rebind a DHCP lease
level: intermediate
minutes: 3
sourceLesson: ip-dhcp
summary: Calculate nominal lease thresholds and distinguish renewal, rebinding, expiry and reservations.
---

Calculate nominal lease thresholds and distinguish renewal, rebinding, expiry and reservations.

## Leases

Dynamic address assignment uses **DHCP leases**, allowing addresses to be reused after clients release them or leases expire. DHCP also supports other allocation arrangements; reuse depends on concurrent demand and lease retention, not just visitor count.

For a finite lease, nominal default timers are below. Servers can supply different T1/T2 values; RFC 2131 recommends random timing variation, and a client may seek renewal early:

- **T1**, at 50% of the lease: start **renewing**. Unicast a Request directly to the server that granted the lease.
- **T2**, at 87.5% of the lease: if the server hasn't answered, start **DHCP rebinding**. Broadcast a Request so another server with sufficient state and authority may extend it.

If the lease expires with no answer, the client must stop using the address. Ignoring timing variation and explicit overrides, the two timers are fixed fractions of the lease, measured from the lease-start reference (not simply from delayed ACK arrival):

```formula
T_1 = 0.5L
T_2 = 0.875L
T_1 = 0.5 × 24 h = 12 h
T_2 = 0.875 × 24 h = 21 h
where
T_1: the renewal time (T1): how long after the lease starts the client begins renewing with its own server
T_2: the rebinding time (T2): how long after the lease starts the client asks any server
L: the lease length granted by the server, here 24 hours
0.5, 0.875: the default fractions, 50% and 87.5% (seven eighths) of the lease
h: hours
In words: a client tries its own server halfway through the lease, tries any server when seven eighths has passed, and gives the address up when the lease runs out.
```

For a 24-hour lease starting at midnight, that means renewing from 12:00, rebinding from 21:00 and expiry at 24:00. The same calculation in seconds:

```python
def timers(lease):
    # Nominal defaults for finite seconds.
    # 0xffffffff represents infinity.
    if (type(lease) is not int
            or not 0 < lease < 0xffffffff):
        raise ValueError("bad finite lease")
    # Seconds since the lease start.
    return lease * 0.5, lease * 0.875

print(timers(86400))  # (43200.0, 75600.0)
```

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
- [RFC 2132: DHCP Options and BOOTP Vendor Extensions](https://www.rfc-editor.org/rfc/rfc2132)
- [Dynamic Host Configuration Protocol — Wikipedia](https://en.wikipedia.org/wiki/Dynamic_Host_Configuration_Protocol)
- [DHCP snooping — Wikipedia](https://en.wikipedia.org/wiki/DHCP_snooping)
- [RFC 5227: IPv4 Address Conflict Detection](https://www.rfc-editor.org/rfc/rfc5227)
- [RFC 9915: DHCP for IPv6 (replaces RFC 8415)](https://www.rfc-editor.org/rfc/rfc9915.html)


- [RFC 3396: long DHCPv4 options](https://www.rfc-editor.org/rfc/rfc3396)
- [RFC 3927: IPv4 link-local addressing](https://www.rfc-editor.org/rfc/rfc3927)
- [RFC 3118: DHCP authentication](https://www.rfc-editor.org/rfc/rfc3118)
