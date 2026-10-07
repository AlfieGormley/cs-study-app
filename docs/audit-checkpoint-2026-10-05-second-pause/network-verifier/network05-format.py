from pathlib import Path
changes={'nsec-vpns':{'raise TypeError("integer MTU required")':'raise TypeError("integer MTU needed")','raise ValueError("no inner capacity")':'raise ValueError("no capacity")','if type(size) is not int or size < 1:':'if (type(size) is not int\n                or size < 1):','raise ValueError("positive size")':'raise ValueError("size must be > 0")'},'nsec-wireless':{'raise ValueError("passphrase length")':'raise ValueError("password length")'},'nsec-tls':{'raw, server_hostname=host) as tls:':'raw,\n            server_hostname=host) as tls:'}}
for stem,rs in changes.items():
 p=Path('content/networks/05-network-security')/(stem+'.md');s=p.read_text()
 for a,b in rs.items():assert a in s;s=s.replace(a,b)
 p.write_text(s)
