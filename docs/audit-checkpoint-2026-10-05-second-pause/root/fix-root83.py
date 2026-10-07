from pathlib import Path
p=Path('content/networks/03-tcp/tcp-flow-control.md');s=p.read_text()
def r(a,b):
 global s
 assert a in s,a[:100]
 s=s.replace(a,b)
r('the classic 40 ms stall when Nagle\'s algorithm meets delayed ACKs','how Nagle and delayed ACKs can interact to delay small messages')
r('in every segment, how much more data it is willing to accept. The sender never has more unacknowledged data in flight than that.','through valid window advertisements, which sequence range it is prepared to receive. The sender limits new transmissions accordingly; advertisements are delayed feedback, and window shrinkage or special probes require more detailed rules.')
r('can send = min(rwnd, cwnd) - in flight','budget = max(0, min(rwnd, cwnd) - flight)')
r('## The receive window','This is a simplified new-data budget with both windows expressed in bytes and measured from a consistent ACK point. Actual sending also depends on available data, pacing, recovery state and socket/packetisation rules.\n\n## The receive window')
r('That number is essentially the free space in the socket\'s receive buffer.','It is a sequence-space advertisement, not an exact measurement of unused socket memory: bookkeeping, buffered out-of-order data, scaling and window-update policy matter.')
a=s.index('receive buffer (64 KB)');z=s.index('\n```',a)
s=s[:a]+'''accepted contiguous data | advertised range
-------------------------+-----------------
                         ^ ACK / RCV.NXT
                         <---- rwnd ------>

Some accepted data may still await app reads.
Out-of-order data may occupy the range.
''' .rstrip()+s[z:]
r('with no application code involved.','at the transport boundary. An application that keeps accumulating work in its own queue can still grow memory unless it propagates backpressure further.')
r('Every ACK moves the left edge forward;','An ACK acknowledging new data advances the left edge; duplicate or stale ACKs do not.')
r('A sender can have at most one window of data unacknowledged, and it takes one round trip for ACKs to come back. So, however fast the link:','In a steady-state model with fixed usable byte window and ACK round-trip delay, the window imposes this throughput ceiling (other limits can make the actual rate lower):')
r('from then on the window field is multiplied by 2^shift.','when scaling is successfully negotiated, each side’s later advertised window uses that side’s shift. Window fields in SYN and SYN+ACK segments themselves are **not scaled**.')
r('about **1 GiB**.','**1,073,725,440 bytes**, just below 1 GiB.')
r('A large file transfer that runs at exactly window/RTT is the giveaway.','A rate near that modelled bound is a clue; endpoint and on-path captures are needed to establish missing or inconsistent negotiation.')
r('On recent kernels `tcp_rmem` defaults to `4096 131072 6291456`: a 128 KB start, growing to 6 MB.','Defaults vary with kernel version, available memory and distribution settings. The retrieved kernel documentation lists a 131,072-byte default receive-buffer allocation and a memory-dependent autotuning maximum; inspect the running system rather than assume a universal 6 MB cap.')
r('fixes that socket\'s buffer and disables autotuning for it.','sets an explicit receive-buffer limit and disables receive autotuning for that socket. Linux doubles the requested value for accounting and reports that doubled value through `getsockopt`; neither value directly equals the advertised payload window.')
r('Unless you\'ve measured, leave it alone and raise the sysctl maximum instead.','Compare measured receive windows, buffer settings and application read behaviour before changing limits.')
r('With a 6 MB maximum, the same sum tells you where the ceiling is: at 100 ms RTT, 6 MB / 0.1 s ≈ 480 Mbit/s for one connection at best, and somewhat less in practice because part of the buffer is reserved for bookkeeping overhead. Transatlantic 10 Gbit/s transfers need larger maxima.','If the **effective advertised window** were 6,000,000 bytes, the modelled ceiling at 100 ms RTT would be 480 Mbit/s. A configured 6 MiB memory limit is a different quantity and unit. At a target 10 Gbit/s payload rate and 100 ms RTT, the model requires 125 MB of usable in-flight capacity, plus implementation-specific memory overhead.')
r('While the window is zero, the sender periodically sends a **window probe** (a segment with one byte, or zero bytes, beyond the window).','With data awaiting transmission against a zero window, the sender uses **zero-window probes** to solicit the current window. Probe segment construction depends on the implementation; it should not be confused with permission for unrestricted out-of-window data.')
r('so a lost update is eventually repaired.','so a delivered probe/reply exchange can reveal the reopened window. Continued loss or endpoint failure can still prevent progress.')
r('repeated zero windows mean the **receiving application** is too slow, not the network.','repeated zero windows show a receiver-side flow-control restriction. Check application reads, memory pressure, socket policy and reassembly state; the capture alone does not uniquely identify a slow application or exclude concurrent network problems.')
r('So at most one small segment is in flight at a time.','In the simplified classic rule, further short new-data sends wait while data is outstanding unless enough data forms a full segment. Retransmissions, FIN handling and implementation variants require additional rules.')
r('Bulk transfers are unaffected because they send full segments.','Full-sized ready segments are not delayed by Nagle’s small-segment condition; partially filled tails or incremental application writes can still be affected.')
r('[RFC 1122](https://www.rfc-editor.org/rfc/rfc1122) allows up to 500 ms, and requires an ACK for at least every second full-sized segment.','RFC 9293 requires delayed ACKs to be delayed by **less than 500 ms** and says an ACK **SHOULD** be generated for at least every second full-sized segment or 2×RMSS bytes of new data. Other conditions can call for prompt ACKs.')
r('Real timers are shorter: Linux uses between about **40 ms** and 200 ms, adapting to the connection; Windows defaults to **200 ms**.','Actual ACK scheduling depends on stack version, mode, connection state and configuration. The example below assumes a measured 40 ms delayed-ACK timer; that is not a universal Linux or Windows default.')
r('Consider a client that sends a request as two writes, a header and then a body, and waits for the response:','Consider a trace where a short header has already been sent, a separate short body is held by Nagle, and the receiver delays its ACK while waiting for the complete request:')
r('   ...  ~40 ms (Linux) ... 200 ms  ...','   ... measured delay (example: 40 ms) ...')
r('Every request pays the delayed-ACK timeout: 40 ms on Linux, up to 200 ms with a Windows peer. On a 1 ms data-centre RTT, that is a 40× slowdown.','That particular exchange incurs the delayed-ACK wait. Not every pair of writes reproduces it: coalescing, ACK modes, message sizes and timing vary. A 40 ms extra wait can dominate a 1 ms path, but does not by itself prove an exact 40× total-response slowdown.')
r('Fixes, best first:','Possible fixes after confirming this interaction:')
r('One write, one segment, no stall. This also saves system calls.','This supplies the data together and can avoid the split-message dependency, but one API call does not guarantee one packet, full `sendmsg` completion or no other stall. Handle partial writes where required.')
r('Most RPC frameworks and databases\' client libraries do this, and Go sets it by default on every TCP connection.','Go’s `net.TCPConn` documentation specifies NoDelay enabled by default. Other libraries require their own documentation/configuration checks.')
r('hold everything until you uncork,','delay partial-segment output while assembling data; full segments can still be sent and Linux documents a timeout ceiling,')
a=s.index('s = socket.create_connection(');z=s.index('\n```',a)
s=s[:a]+'''def send_request(s, header, body):
    # Caller owns a connected TCP socket.
    # header/body are bytes; set a timeout
    # suitable for the application first.
    s.setsockopt(socket.IPPROTO_TCP,
                 socket.TCP_NODELAY, 1)
    s.sendall(header + body)
''' .rstrip()+s[z:]
r('With Nagle off, ten tiny writes become ten tiny packets, so batching your writes is still worth doing.','Other buffering, pacing, congestion/flow control and packetisation still apply. Ten writes need not become ten packets; batching can nevertheless reduce overhead.')
r('so applications re-set it after reads.','so one call is not a permanent “never delay ACKs” policy. Whether repeated requests help requires measurement; it is not a portable solution.')
r('The receive window is the free space in the receiver\'s buffer;','The receive window advertises acceptable sequence space and reflects buffer/update policy;')
s+='\n> [!note] Content omitted after review\n> Universal Linux/Windows delayed-ACK times, a universal 6 MB autotuning limit and one-write/one-packet guarantees are omitted because they are not supported across versions and configurations. Timing scenarios are explicit examples, not benchmarks.\n\n- [Linux TCP socket options](https://man7.org/linux/man-pages/man7/tcp.7.html)\n- [Linux socket buffer accounting](https://man7.org/linux/man-pages/man7/socket.7.html)\n- [Go TCPConn.SetNoDelay](https://pkg.go.dev/net#TCPConn.SetNoDelay)\n'
p.write_text(s)
