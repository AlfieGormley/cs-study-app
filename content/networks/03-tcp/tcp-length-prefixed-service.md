---
id: tcp-length-prefixed-service
sourceLesson: tcp-sockets
title: A bounded length-prefixed TCP service
level: intermediate
minutes: 3
summary: A bounded length-prefixed TCP service, with worked examples and explicit assumptions.
---

## A length-prefixed server with threads

First, framing helpers. `recv_exact` loops until it has exactly `n` bytes, and treats EOF in the middle as an error:

```python
import socket, struct, threading

MAX_MSG = 1024 * 1024  # teaching limit

def recv_exact(sock, n):
    if type(n) is not int or n < 0:
        raise ValueError("invalid length")
    buf = bytearray()
    while len(buf) < n:
        # Request only the missing suffix.
        chunk = sock.recv(n - len(buf))
        if not chunk:
            # EOF before all requested
            # bytes.
            raise EOFError
        buf += chunk
    return bytes(buf)

def recv_msg(sock):
    hdr = recv_exact(sock, 4)
    # Decode an unsigned big-endian length.
    (n,) = struct.unpack("!I", hdr)
    # Reject oversized claims before reads.
    if n > MAX_MSG:
        raise ValueError("too large")
    return recv_exact(sock, n)

def send_msg(sock, data):
    if len(data) > MAX_MSG:
        raise ValueError("too large")
    hdr = struct.pack("!I", len(data))
    # Retry partial writes of prefix + body.
    sock.sendall(hdr + data)
```

`"!I"` is a 4-byte unsigned integer in network byte order (big-endian). Big-endian means the first byte on the wire is the most significant, so the receiver rebuilds the length like this:

```formula
n = b_0 × 2^24 + b_1 × 2^16
  + b_2 × 2^8 + b_3
n = 0 + 0 + 1 × 256 + 0 = 256
n_max = 2^32 − 1 = 4,294,967,295
where
n: the message length the prefix encodes, in bytes
b_0: the first byte received (most significant), 0 to 255
b_1: the second byte
b_2: the third byte
b_3: the fourth byte (least significant)
n_max: the largest length 4 bytes can express
In words: each byte is worth 256 times the byte after it, so the prefix 00 00 01 00 means 256; MAX_MSG then rejects anything above 1 MiB, far below the 4 GiB the field could claim.
```

Combining header and body avoids an application-created pause between two small writes, but one `sendall()` is not one packet and cannot guarantee freedom from Nagle, queueing or other delays.

Then the server, one thread per connection:

```python
def handle(conn, addr):
    with conn:
        conn.settimeout(5)
        try:
            while True:
                msg = recv_msg(conn)
                # Reply only to a complete
                # message.
                send_msg(conn, msg.upper())
        except (EOFError, OSError,
                ValueError):
            pass  # toy policy: close

srv = socket.create_server(
    ("127.0.0.1", 9000), backlog=128)
while True:
    conn, addr = srv.accept()
    # Each client owns a separate socket.
    threading.Thread(target=handle,
                     args=(conn, addr),
                     daemon=True).start()
```

And a client:

```python
with socket.create_connection(
        ("127.0.0.1", 9000),
        timeout=5) as s:
    s.settimeout(5)
    send_msg(s, b"hello")
    print(recv_msg(s))   # b'HELLO'
```

Details that make this correct:

- `with conn:` closes this socket when the handler exits. It cannot force a handler that never exits to finish; duplicated references and wrappers also affect lifetime.
- The helpers cap each body at 1 MiB. The handler has a per-operation timeout, not a total-message deadline: a trickling peer can keep a message in progress. Production code needs total deadlines, connection/thread limits and a deliberate error policy.
- `socket.create_server` sets **`SO_REUSEADDR`** on POSIX systems. Without suitable reuse settings, retained connection state can stop the port being bound again immediately. This is not an inevitable outcome of every restart; address, platform and old/new socket options matter.

> [!note] SO_REUSEADDR vs SO_REUSEPORT
> `SO_REUSEADDR` relaxes platform-specific bind rules; it does not grant arbitrary sharing with an active listener. Linux generally requires the reuse option on both the previous and new sockets for the relevant reuse case. `SO_REUSEPORT` (Linux 3.9+) supports multiple eligible listeners at the same address/port, each with its own queue. Sockets must set it before binding; Linux requires matching effective user IDs. Default selection and optional BPF policies do not guarantee perfectly balanced work.

## Key takeaways

- Loop until the requested header/body length is assembled and cap claimed body sizes.
- Network byte order makes the most significant prefix byte arrive first.
- Thread lifetimes, socket reuse rules and per-operation timeouts require explicit production policies.

## Further reading

- [Python socket module documentation](https://docs.python.org/3/library/socket.html)
- [Socket Programming HOWTO — Python docs](https://docs.python.org/3/howto/sockets.html)
- [Python selectors module documentation](https://docs.python.org/3/library/selectors.html)
- [Beej's Guide to Network Programming](https://beej.us/guide/bgnet/)
- [The C10K problem — Dan Kegel](http://www.kegel.com/c10k.html)
- [SYN packet handling in the wild — Cloudflare blog](https://blog.cloudflare.com/syn-packet-handling-in-the-wild/)
