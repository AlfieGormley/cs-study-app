---
id: ip-dhcp-message-options
title: Decode DHCP message options
level: intermediate
minutes: 3
sourceLesson: ip-dhcp
summary: Read BOOTP-derived DHCP fields and parse bounded type-length-value options in Python.
---

Read BOOTP-derived DHCP fields and parse bounded type-length-value options in Python.

### The message

A DHCPv4 message uses the BOOTP-format header, a magic cookie and options. Option overload can also place options in designated BOOTP fields:

| Field | What it holds |
|---|---|
| xid | Transaction ID |
| ciaddr | Client's current IP, if any |
| yiaddr | "Your" address: the one offered |
| giaddr | Relay agent's address |
| chaddr | Client hardware address (a MAC for Ethernet) |
| options | Type-length-value list |

The options carry everything interesting:

| Code | Option |
|---|---|
| 1 | Subnet mask |
| 3 | Router (default gateway) |
| 6 | DNS servers |
| 50 | Requested IP address |
| 51 | Lease time |
| 53 | Message type (1 = Discover … 5 = Ack) |
| 54 | Server identifier |
| 55 | Parameter request list |

Most options use type-length-value encoding; Pad and End are single-byte exceptions. This teaching parser accepts one options field **after** the magic cookie, checks lengths, concatenates repeated option payloads (RFC 3396) and requires End. It does not validate option-specific semantics or process overloaded fields:

```python
def parse_options(b):
    opts, i = {}, 0
    while i < len(b):
        code = b[i]
        if code == 255:      # End
            break
        if code == 0:        # Pad
            i += 1
            continue
        if i + 1 >= len(b):
            raise ValueError(
                "missing option length")
        n = b[i + 1]
        if i + 2 + n > len(b):
            raise ValueError(
                "truncated option payload")
        part = b[i + 2:i + 2 + n]
        previous = opts.get(code, b"")
        # Join repeated option payloads.
        opts[code] = previous + part
        # Skip this complete option.
        i += 2 + n
    else:
        raise ValueError("missing End")
    return opts

# Ack, one-hour lease, then gateway.
raw = bytes([53, 1, 5,
             51, 4, 0, 0, 0x0e, 0x10,
             3, 4, 192, 168, 1, 1,
             255])
o = parse_options(raw)
print(o[53][0])                    # 5
print(int.from_bytes(o[51], "big"))  # 3600
```

Message type 5 is an Ack; the lease is 0x0e10 seconds, which is hexadecimal (base 16) for 14 × 256 + 1 × 16 + 0 = 3,600 seconds, one hour; the gateway is 192.168.1.1.

## Key takeaways
- DHCP fields distinguish current, offered and relay addresses.
- Most options have type and length; Pad and End are one-byte exceptions.
- The teaching parser checks bounds and concatenates repeated payloads.
- It requires End and omits option-specific validation and overloaded fields.

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
