from pathlib import Path
p=Path('content/networks/03-tcp/tcp-connections.md');s=p.read_text()
def r(a,b):
 global s
 assert a in s,a[:100]
 s=s.replace(a,b)
r('Before any data can flow, both sides must agree on where their byte numbering starts and confirm that the other side is really there. When they finish, both must agree that every byte has been delivered.','Normal establishment synchronises sequence spaces and checks bidirectional reachability; this is not cryptographic peer authentication. Data can accompany handshake segments, and extensions such as TCP Fast Open can allow early application delivery. Graceful closure acknowledges the byte stream in each direction, not application processing or durable storage of those bytes.')
r('the number of the first byte of data in this segment.','the first sequence-space position in the segment; a SYN occupies its own position before any data.')
r('Most are negotiated only on SYN segments.','MSS, window scale and SACK permission are exchanged on SYN segments. Negotiated timestamps accompany later segments, and SACK blocks can appear on later ACKs.')
r('even though they carry no data.','independently of any data carried in the same segment.')
r('The ACK number means "I have everything **before** this byte; send me this one next."','The cumulative ACK identifies the next expected sequence-space position in that direction, modulo 2^32. It acknowledges contiguous received stream data/control positions, not successful application processing.')
r('No connection is created from a ghost.','If that response arrives, the server abandons the stale attempt. With no reply, it can retain half-open state until timeout; the handshake is not a defence against every spoof or replay scenario.')
r("This was the basis of Kevin Mitnick's famous 1994 attack.",'Predictable sequence numbers have historically enabled off-path spoofing; reachability and other validation assumptions also matter.')
r('Modern stacks follow [RFC 6528](https://www.rfc-editor.org/rfc/rfc6528): ISN = a clock that ticks every 4 µs, plus a keyed hash of the 4-tuple and a secret.','[RFC 6528](https://www.rfc-editor.org/rfc/rfc6528), incorporated into RFC 9293, describes a clock component plus a keyed function of endpoint addresses/ports. RFC 9293 discusses an approximately 4 µs clock; actual implementations can differ. The construction aims to make new ISNs hard for an off-path attacker to predict while separating connection incarnations.')
r('it creates a small **request socket** (on Linux, roughly 300 bytes), puts it in the **SYN queue**, and sends SYN+ACK.','normal stateful Linux processing creates **request-socket** state associated with the listener and sends SYN+ACK. Exact memory use depends on kernel/configuration.')
r('on Linux, 5 times by default, giving up after about 63 seconds.','the Linux documentation retrieved here specifies five SYN+ACK retries by default, with a one-second initial timeout and a final timeout near 63 seconds. This is a documented default, not a universal timing guarantee.')
r('A **SYN flood** sends huge numbers of SYNs from spoofed source addresses.','A **SYN flood** attempts to exhaust connection-establishment resources with SYN traffic, often using spoofed addresses.')
r("Dan Bernstein's 1996 fix: when the SYN queue is full, **store nothing**. Encode the essential state into the server's ISN, and let the client hand it back in its ACK.","A **SYN cookie** avoids retaining an ordinary per-attempt half-open entry: encode enough information in the server's sequence-number construction to validate a returning ACK and reconstruct connection state. Secret keys and other shared server state still exist, and processing consumes CPU and bandwidth.")
a=s.index("In Bernstein's original design,");z=s.index('\nCosts:',a)
s=s[:a]+'''A conceptual flow is:

```
SYN + endpoint tuple
        |
        v
secret + time + supported option state
        |
        v
cookie sequence number -> SYN+ACK
        |
client returns ACK acknowledging cookie
        |
validate freshness/authenticator
        |
create established-connection state
```

The exact encoding is implementation-specific. Recovering the acknowledged server sequence number uses `ack - 1` modulo 2^32, followed by the implementation's validation rules. An off-path attacker that cannot observe the SYN+ACK must guess a valid value; finite cookie authenticators do not make guessing mathematically impossible.
''' +s[z:]
r('- Only 8 possible MSS values.','- Limited cookie space constrains the amount of MSS/option state encoded; the set of supported MSS values depends on the implementation.')
r('- Options such as window scaling and SACK are lost, unless (as Linux does) they are squeezed into the TCP timestamp option.','- Option support can be reduced; implementations may encode extra state in negotiated timestamp fields. Behaviour varies by version and client options.')
r("- The server can't retransmit a SYN+ACK it has no record of.","- Without per-attempt timer state, there is no autonomous SYN+ACK retransmission timer for that attempt. A retransmitted client SYN can elicit another SYN+ACK.")
r('Linux uses its own arithmetic but the same three ingredients (a time counter, an MSS index and a keyed hash). Its default,','Linux has its own cookie construction. Its documented default,')
r('so normal traffic keeps full options.','when the kernel is built with SYN-cookie support; value 2 requests unconditional generation. Cookies do not remedy every overload or network-capacity problem.')
r('The side that sends the **first FIN** (the active closer) ends in **TIME_WAIT**,','In the ordinary sequential graceful close above, the active closer ends in **TIME_WAIT**,')
r('Two reasons:','Simultaneous close can put both endpoints in TIME_WAIT; aborts and special reuse cases follow different rules. Two purposes of TIME_WAIT are:')
a=s.index('1. **The final ACK might be lost.**');z=s.index('\nRFC 793 suggested',a)
s=s[:a]+'''1. **A retransmitted FIN may need another ACK.** Keeping connection state lets the endpoint acknowledge a repeated FIN if the peer missed the final ACK. The TIME_WAIT timer can restart when the FIN is received again. MSL is a segment-lifetime assumption, not the peer's retransmission timeout, so adding two presumed network delays is not a proof of the retransmission schedule.
2. **Old duplicates must expire.** Retaining the connection incarnation for the specified interval reduces confusion if the same endpoint tuple is reused. The guarantee relies on the MSL/sequence-number assumptions; TCP also specifies constrained early-reuse cases.
''' + s[z:]
r('Linux hard-codes TIME_WAIT at **60 seconds**.','Linux defines its ordinary TIME_WAIT interval as **60 seconds**; reuse, retransmitted segments and resource handling can affect an observed entry’s lifetime.')
r('but it ties up the **5-tuple**. That matters to whichever side closes first:','but it constrains reuse of the **5-tuple** under the implementation’s rules:')
r('that rarely matters, because each has a different client tuple.','a large connection count is still possible because peers have distinct tuples. Memory, churn and reuse patterns can nevertheless matter.')
r('Fixes, best first:','Possible approaches, chosen for the application and deployment:')
r('Let the **client** close first, so the TIME_WAIT lands on the side with spare ports.','Changing which endpoint performs the sequential active close moves TIME_WAIT ownership; it does not create spare ports or solve the problem universally.')
r('allows new **outgoing** connections to reuse a TIME_WAIT tuple when timestamps prove it is safe. Linux now defaults this to 2 (loopback only).','enables reuse subject to Linux’s protocol-safety checks; timestamps are not a cryptographic proof. The retrieved Linux documentation lists default 2 (loopback only) and a separate reuse delay. Do not treat this as a universal replacement for pooling.')
r('Here are the transitions you will see in practice:','The table below abbreviates successful ordinary events. Sequence/ACK validity, acceptable in-order FIN processing, queued data, duplicate packets, reset/error paths and API details are omitted:')
r('| FIN_WAIT_1 | recv ACK | FIN_WAIT_2 |','| FIN_WAIT_1 | own FIN acknowledged; no peer FIN processed | FIN_WAIT_2 |')
r('| FIN_WAIT_1 | recv FIN, send ACK | CLOSING |','| FIN_WAIT_1 | peer FIN processed; own FIN not acknowledged | CLOSING |\n| FIN_WAIT_1 | peer FIN processed and own FIN acknowledged | TIME_WAIT |')
r('| CLOSING | recv ACK | TIME_WAIT |','| CLOSING | own FIN acknowledged | TIME_WAIT |')
r('| LAST_ACK | recv ACK | CLOSED |','| LAST_ACK | own FIN acknowledged | CLOSED |')
r('at the same moment','before receiving the other’s FIN and then process the crossing FINs before ACKs of their own FINs')
r('$ ss -tan state close-wait | wc -l','$ ss -Htan state close-wait | wc -l')
r('> [!tip] Lots of CLOSE_WAIT means a bug in your code\n> CLOSE_WAIT means "the peer closed; waiting for **my application** to call `close()`". The kernel cannot leave it alone. Thousands of CLOSE_WAIT sockets almost always mean the application leaks connections, for example an error path that forgets to close. TIME_WAIT is normal; CLOSE_WAIT piling up is not.','> [!tip] Investigate persistent CLOSE_WAIT growth\n> CLOSE_WAIT means a peer FIN has been processed and the local send direction remains open. The application may legitimately still be preparing a response. Persistent unexplained growth can indicate leaked sockets or stalled handlers; use process-level descriptor and application evidence before diagnosing a leak. `shutdown(SHUT_WR)` or closing the final relevant descriptor can initiate the local FIN; process exit or an abort can also change the state.')
r('A segment with RST tells the peer','An accepted, valid RST tells the peer')
r('There is no acknowledgement and no TIME_WAIT.','A reset is not itself acknowledged and normally aborts the connection without a graceful FIN/TIME_WAIT sequence. Invalid RSTs can be ignored or challenged, and existing TIME_WAIT handling has additional rules.')
r('the reply is RST, which the client reports','normal unfiltered TCP processing replies with RST, which the client can report')
r('The client sees `ECONNRESET`.','The client can receive a reset once traffic reaches the rebooted peer; the exact API error depends on state and operations.')
r('`SO_LINGER` with a timeout of 0,','on Linux, enabled `SO_LINGER` with a timeout of 0,')
r('which a genuine peer will answer and an off-path attacker cannot see.','which can elicit a correctly sequenced reset from a peer that has lost the connection. This is a robustness check, not cryptographic authentication; rate limits and side channels affect practical attack resistance.')
r('CLOSE_WAIT piling up is an application bug.','unexplained CLOSE_WAIT growth warrants investigation of application lifecycle and descriptor ownership.')
s+='\n> [!note] Content omitted after review\n> A universal request-socket byte size, original cookie bit layout, historical attacker attribution and unconditional timeout/option guarantees are omitted because this pass did not establish adequate implementation-specific evidence. Cookie handling and state diagrams here are teaching models, not an exhaustive TCP implementation.\n\n- [Linux TCP configuration defaults](https://kernel.org/doc/html/latest/networking/ip-sysctl.html)\n'
p.write_text(s)
