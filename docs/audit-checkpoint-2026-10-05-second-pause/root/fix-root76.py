from pathlib import Path
base=Path('content/networks/02-ip-routing')
changes={
'ip-ipv4': [('    # Parse a captured header, not its payload.','    # Header only; no payload validation.'),('    # Model one unfragmented, DF-clear packet.\n    # Equal header sizes; no option-copy logic.','    # Unfragmented, DF-clear input.\n    # Equal headers; no option-copy logic.'),('    if not all(isinstance(v, int)\n               for v in (data_len, mtu, hdr)):','    sizes = (data_len, mtu, hdr)\n    if not all(type(v) is int for v in sizes):'),('        size = left if left <= capacity else per','        size = min(left, capacity)\n        if left > capacity:\n            size = per')],
'ip-subnetting':[('    usable = count if net.prefixlen >= 31 else (\n        count - 2)','    usable = count\n    if net.prefixlen < 31:\n        usable -= 2')],
'ip-nat-ipv6':[('        self.ip = str(\n            ipaddress.IPv4Address(public_ip))','        addr = ipaddress.IPv4Address\n        self.ip = str(addr(public_ip))'),('        if not 1 <= sport <= 65535:','        if (type(sport) is not int\n                or not 1 <= sport <= 65535):'),('                raise ValueError("ports exhausted")','                raise ValueError(\n                    "ports exhausted")')],
'ip-interior-routing':[('                    or not isinstance(c, int)','                    or type(c) is not int'),('            if nd < dist.get(v, float("inf")):','            old = dist.get(v, float("inf"))\n            if nd < old:'),('                    pq, (nd, next(order), v))','                    pq,\n                    (nd, next(order), v))')],
'ip-bgp':[('    dict(name="transit", lp=100, path=[64500, 3356, 65010],','    dict(name="transit", lp=100,\n         path=[64500, 3356, 65010],'),('    dict(name="peer", lp=200, path=[64600, 64700, 65010],','    dict(name="peer", lp=200,\n         path=[64600, 64700, 65010],'),('    dict(name="customer", lp=300, path=[65010, 65010, 65010],','    dict(name="customer", lp=300,\n         path=[65010, 65010, 65010],')],
'ip-dhcp':[('            raise ValueError("missing option length")','            raise ValueError(\n                "missing option length")'),('            raise ValueError("truncated option payload")','            raise ValueError(\n                "truncated option payload")'),('        opts[code] = opts.get(code, b"") + b[i + 2:i + 2 + n]','        part = b[i + 2:i + 2 + n]\n        opts[code] = opts.get(code, b"") + part'),('    # Nominal defaults only; 0xffffffff represents infinity in DHCPv4.\n    if type(lease) is not int or not 0 < lease < 0xffffffff:\n        raise ValueError("expected a positive finite lease in seconds")','    # Nominal defaults for finite seconds.\n    # 0xffffffff represents infinity.\n    if (type(lease) is not int\n            or not 0 < lease < 0xffffffff):\n        raise ValueError("bad finite lease")')]
}
for name,rs in changes.items():
 p=base/(name+'.md');s=p.read_text()
 for a,b in rs:
  assert a in s,(name,a)
  s=s.replace(a,b)
 p.write_text(s)
