---
id: app-ssh-channels-and-sftp
title: "SSH channel credit and pipelined SFTP"
level: advanced
minutes: 3
sourceLesson: app-ntp-ssh-grpc
summary: "SSH channels have separate credit but still share one ordered TCP transport."
---

SSH runs an encrypted transport, authenticates a user and multiplexes channels inside that transport. A session channel can run a command or a subsystem; port forwarding uses other channel/request types.

### Connection layer: channels

Everything useful happens in **SSH channels** multiplexed over one transport:

- `session` channels run a shell, a command (`exec`) or an **SSH subsystem** such as `sftp`.
- `direct-tcpip` channels carry `ssh -L` local port forwards.
- `tcpip-forward` global requests set up `ssh -R` remote forwards.

Each channel has its own **channel window**, adjusted with `CHANNEL_WINDOW_ADJUST`, just like HTTP/2 streams. A small channel window caps throughput at the window divided by the round-trip time (the same window-over-round-trip ceiling as HTTP/2 flow control), which is why bulk transfers over high-latency SSH links can be slow even on fast networks (HPN-SSH exists to raise these limits). Ordinary SSH port forwarding relays application bytes between separate TCP connections; it does not encapsulate complete inner TCP packets. Loss on the shared SSH TCP connection can nevertheless stall delivery for every multiplexed channel.

## SFTP: not FTP

SFTP is **not** FTP over SSH. It is a separate binary protocol (draft-ietf-secsh-filexfer; OpenSSH implements version 3) that runs as the `sftp` subsystem inside one SSH session channel. Since OpenSSH 9.0, the `scp` command uses the SFTP protocol by default too.

It works like a remote file system API:

```
C: SSH_FXP_OPEN  id=1 "/data/a.bin"
S: SSH_FXP_HANDLE id=1 h="\x00\x01"
C: SSH_FXP_READ id=2 h off=0     len=32768
C: SSH_FXP_READ id=3 h off=32768 len=32768
C: SSH_FXP_READ id=4 h off=65536 len=32768
S: SSH_FXP_DATA id=2 ...
S: SSH_FXP_DATA id=3 ...
C: SSH_FXP_CLOSE id=9 h
```

(Simplified; the real messages are binary.) File-operation requests carry an **SFTP request ID** (the INIT/VERSION negotiation is an exception), so a client can have many READs outstanding at once. That **pipelining** is what makes SFTP fast: OpenSSH's client keeps up to 64 requests in flight by default. A naive client that issues one 32 KiB read and waits for the reply gets at most one block per round trip. Over a 100 ms round trip that is about 2.6 Mbit/s, however fast the link; keeping 64 reads outstanding raises the ceiling 64-fold, until bandwidth, channel windows or the server become the limit. It is the same one-window-per-round-trip ceiling as HTTP/2 flow control:

```formula reference
T ≤ (k × b) / RTT
where
T: the best possible transfer rate, in bytes per second (B/s)
k: the number of read requests kept outstanding at once; 1 for a naive client, up to 64 for OpenSSH's sftp by default
b: the size of each read, in bytes (B); 32 KiB = 32,768 B is common
RTT: the round-trip time, in seconds (s)
≤: is at most
B: bytes
KiB: kibibyte, 1,024 bytes
s: seconds
In words: a client can receive at most the data it has asked for in each round trip, so more outstanding reads or bigger reads raise the ceiling, and a longer round trip lowers it.
```

## Key takeaways
- SSH channels have separate credit but still share one ordered TCP transport.
- SFTP is a separate binary file-operation protocol; request IDs permit pipelined reads.

## Further reading
- [RFC 4254](https://www.rfc-editor.org/rfc/rfc4254)
- [SFTP v3 protocol draft](https://datatracker.ietf.org/doc/html/draft-ietf-secsh-filexfer-02)
- [OpenSSH SFTP manual](https://man.openbsd.org/sftp.1)
