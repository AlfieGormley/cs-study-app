exec(open('/tmp/network04-helper.py').read())
n='app-http-wire'
md(n,'and every cookie attribute and what it really protects.','and the cookie attributes covered here and their security limits.','Lesson is not an exhaustive cookie attribute catalogue.')
md(n,'There are no packets or message boundaries in TCP, just bytes.','TCP carries segments on the network but exposes an ordered byte stream without application-message boundaries.','TCP does have segments; the API lacks message boundaries.')
md(n,'Every line ends with **CRLF**','The start line and header field lines end with **CRLF**','Body bytes are not universally line-delimited.')
md(n,'You can speak HTTP with nothing more than a socket:','This bounded wire-inspection example opens a plain HTTP socket. It collects bytes until close; it does not implement a complete response parser, decode transfer codings, or authenticate the server:','Clearly scope demonstration and network-dependent output.')
a='''s = socket.create_connection(
    ("example.com", 80))
s.sendall(b"GET / HTTP/1.1\\r\\n"
          b"Host: example.com\\r\\n"
          b"Connection: close\\r\\n"
          b"\\r\\n")
reply = b""
while chunk := s.recv(4096):
    reply += chunk
head, _, body = reply.partition(
    b"\\r\\n\\r\\n")
print(head.split(b"\\r\\n")[0])
# b'HTTP/1.1 200 OK' '''.rstrip()
b='''with socket.create_connection(
        ("example.com", 80), timeout=3) as s:
    s.sendall(b"GET / HTTP/1.1\\r\\n"
              b"Host: example.com\\r\\n"
              b"Connection: close\\r\\n"
              b"\\r\\n")
    reply = bytearray()
    while chunk := s.recv(4096):
        reply.extend(chunk)
        if len(reply) > 1_000_000:
            raise ValueError("demo limit")
head, sep, body = bytes(reply).partition(
    b"\\r\\n\\r\\n")
if not sep:
    raise ValueError("incomplete headers")
print(head.split(b"\\r\\n")[0])
# Example: b'HTTP/1.1 200 OK'
# Actual status depends on the server.'''
md(n,a,b,'Close socket, bound reads, reject missing header terminator and avoid guaranteed external response.')
md(n,'so "read until `recv` returns nothing" works. Without it, HTTP/1.1 connections are **persistent** by default and the loop would hang waiting for bytes that never come.','so EOF can end this inspection loop when the peer complies. EOF alone does not establish a valid or complete response. Without it, HTTP/1.1 connections are **persistent** by default, so a read-until-close loop can wait after the response is complete. Timeouts and server policy still apply.','EOF is not a validity check and persistence does not imply an inevitable infinite hang.')
a='''1. Responses to `HEAD`, all `1xx`, `204 No Content` and `304 Not Modified` responses **never have a body**, whatever the headers say.
2. If `Transfer-Encoding` is present and its final coding is `chunked`, the body is a series of chunks (below).
3. Otherwise, if `Content-Length` is present, the body is exactly that many bytes.
4. Otherwise, a **request** has no body, and a **response** body runs until the server closes the connection.'''
b='''1. Responses to `HEAD`, all `1xx`, `204 No Content` and `304 Not Modified` responses **never have a message body**, whatever the headers say. An informational response may precede a final response; a `101` switches protocols.
2. A successful `2xx` response to `CONNECT` starts a tunnel after the headers; ignore framing fields for its length.
3. `Transfer-Encoding` overrides `Content-Length`. Senders must not send both. Reject ambiguous requests; a forwarding intermediary that processes such a message must remove `Content-Length`.
4. If transfer coding ends in `chunked`, decode chunks. If it ends in another coding, a response is close-delimited; a request must receive `400` and the connection must close.
5. With no transfer coding, a valid `Content-Length` gives the exact byte count. Invalid or conflicting lengths are framing errors; identical repeated values have a specified normalisation exception.
6. Otherwise, a **request** has no body and a **response** is close-delimited. Complete header validation and the RFC’s error rules are still required.'''
md(n,a,b,'Original simplified precedence wrongly used Content-Length after nonfinal chunked and omitted CONNECT/error cases.')
md(n,'Rule 4 for responses is the HTTP/1.0 way, and it is fragile: a connection that drops early looks identical to a complete response. You cannot tell a truncated download from a finished one.','Close-delimited responses are supported for compatibility and are fragile: an apparently clean connection close cannot distinguish a complete body from a prematurely ended one without additional information. HTTP/1.0 also supported Content-Length.','Avoid universal HTTP1.0 close framing and distinguish failure detection from message completeness.')
md(n,'A `HEAD` response has the same headers a `GET` would, including `Content-Length: 1256`, but zero body bytes follow. A client that ignored rule 1 would wait for 1256 bytes forever. Proxies and hand-rolled clients get this wrong surprisingly often.','A server should send the fields it would send for GET, but may omit fields calculated only while generating content. If it sends Content-Length on HEAD, that value must describe the content an equivalent GET would send. No body follows; waiting for those bytes can block until a timeout or close.','HEAD field parity is SHOULD with exceptions, not mandatory complete identity; remove unsupported prevalence.')
start=(r/(n+'.md')).read_text();a=start[start.index('A minimal decoder:'):start.index('Details worth knowing:')]
b='''A deliberately restricted decoder for an already-buffered, bounded message with **no extensions or trailers**. It rejects those unsupported forms and returns any following bytes separately. Production receivers must handle the full grammar and incremental input.

```python
import re

def read_chunked(buf):
    if len(buf) > 1_000_000:
        raise ValueError("demo limit")
    parts = []
    while True:
        line, sep, buf = buf.partition(
            b"\\r\\n")
        if not sep or not re.fullmatch(
                rb"[0-9A-Fa-f]+", line):
            raise ValueError("bad size")
        size = int(line, 16)
        if size == 0:
            if not buf.startswith(b"\\r\\n"):
                raise ValueError(
                    "trailers or truncation")
            return b"".join(parts), buf[2:]
        if (len(buf) < size + 2
                or buf[size:size + 2]
                != b"\\r\\n"):
            raise ValueError("bad chunk")
        parts.append(buf[:size])
        buf = buf[size + 2:]
```

'''
md(n,a,b,'Original decoder accepted truncated data, invalid CRLF/sizes and ended before trailer terminator without exposing leftovers.')
md(n,'**Chunk extensions** (`7;name=value`) exist but are almost never used. Parsers must skip them.','**Chunk extensions** (`7;name=value`) can carry per-chunk metadata. A conforming receiver ignores unrecognised extensions after parsing their syntax and imposing suitable limits.','Unknown extensions are ignored semantically; grammar and limits still matter; remove unsupported rarity.')
md(n,'HTTP/2 and HTTP/3 **forbid** `Transfer-Encoding: chunked`. Their DATA frames already carry lengths and an end-of-stream flag.','HTTP/2 and HTTP/3 **forbid** `Transfer-Encoding`. Both have length-delimited DATA frames. HTTP/2 signals message completion with END_STREAM; HTTP/3 uses the end of its underlying QUIC stream, not a DATA-frame END_STREAM flag.','HTTP3 frames have no END_STREAM flag.')
md(n,'RFC 9112 says `Transfer-Encoding` wins, and that such a message should be treated as suspicious.','RFC 9112 gives transfer coding precedence, recommends treating the combination as an error, and requires connection closure after responding if a server elects to process such a request.','Clarify security-critical server closure requirement.')
md(n,'The classic **CL.TE** variant: the front end trusts `Content-Length`, the back end trusts chunked.','The classic **CL.TE** variant below assumes vulnerable hops: the front end trusts Content-Length, the back end parses chunks and improperly keeps the connection reusable. Lines use CRLF, but the final `SMUGGLED` bytes have **no trailing CRLF**. This is a boundary illustration, not a complete valid second request.','Wire length13 requires no terminal newline; valid strict processing closesconnection, preventing assumed reuse.')
md(n,'Reject any request with both headers, or with malformed `Transfer-Encoding` values (`chunked , identity`, odd whitespace, duplicates).','Reject requests with both framing fields, invalid transfer-coding syntax, repeated chunked coding or a final coding other than chunked. Whitespace permitted by the grammar is not inherently malformed.','OWS before comma is valid; distinguish grammar from invalid coding order.')
md(n,'Speak HTTP/2 end to end, where lengths are part of binary framing (but beware proxies that *downgrade* HTTP/2 to HTTP/1.1 for the back end).','Using HTTP/2 end to end removes this HTTP/1.1 delimiter disagreement, but does not excuse validation of header fields and length consistency. Translation to HTTP/1.1 needs particular care.','Binary framing does not eliminate all request smuggling.')
md(n,'One slow response blocks every one queued behind it, and buggy intermediaries mangled pipelined traffic, so browsers never enabled it by default. Instead they open several parallel connections per origin (typically 6).','A slow earlier response can delay later responses. Clients can instead use parallel connections, subject to their own limits.\n\n> [!note] Content omitted after review\n> A universal browser connection count, historical default-pipelining claim and typical keep-alive timeout range are omitted because browser/server versions and configurations were not reliably established here.','Remove false all-browser historical default and unverified universal implementation figures.')
md(n,'it answers `413` or `401` straight away and saves the bandwidth.','it can send a final error such as `413` or `401` before the body. Clients may send after a bounded wait, so Expect does not guarantee that no body bytes are transmitted.','RFC allows client bounded wait; no guarantee completebandwidthsaving.')
md(n,'HTTP keeps no memory between requests.','HTTP semantics are stateless; applications and connections can still maintain state.','Stateless protocol does not prohibit server or connection state.')
