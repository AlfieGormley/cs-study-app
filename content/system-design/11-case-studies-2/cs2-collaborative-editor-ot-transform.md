---
id: cs2-collaborative-editor-ot-transform
title: Operational transformation on both clients
level: advanced
minutes: 3
summary: Transform index-based edits against committed and pending operations.
sourceLesson: cs2-collaborative-editor
---

## Deep dive 1: Operational Transformation

Google described its use of OT in a 2010 engineering post; this is a historical implementation account. OT represents edits as operations such as `insert(pos, text)` and `delete(pos, len)`. When two operations are concurrent, one is **transformed** against the other so it still makes sense.

### Example
The document is `abc` at revision 10.

- Alice: `insert(1, "X")`, giving `aXbc`.
- Bob, at the same time: `delete(2)` (removing `c`), giving `ab`.

The server receives Alice's op first and commits it as rev 11. Bob’s operation names revision ten as its base, so the server transforms it against everything committed since rev 10:

```python
# Apply Alice, then shift Bob's target.
text = "abc"
insert_pos, delete_pos = 1, 2
inserted = "X"
text = (text[:insert_pos] + inserted
        + text[insert_pos:])
# An earlier insertion shifts the target.
if insert_pos <= delete_pos:
    delete_pos += len(inserted)
text = (text[:delete_pos]
        + text[delete_pos+1:])
# aXb: Bob's c is gone; Alice's X remains.
print(text)
```

Applying `delete(3)` to `aXbc` gives `aXb`. That's correct: Bob's `c` is gone and Alice's `X` is kept. Alice receives Bob's transformed op, Bob receives Alice's op (transformed against his pending op on his client), and both converge to `aXb`.

### Client-server OT in practice
- The client keeps three things: the last acknowledged server revision, **one in-flight op** awaiting ack, and a **buffer** of ops typed since.
- Incoming server ops are transformed against the in-flight and buffered ops before being applied locally.
- Certain central-server OT protocols avoid the need for TP2 by constraining causal delivery and transformation paths; centralisation alone is insufficient. TP1 requires two concurrent ops to converge when transformed and applied in either order. More general transformation paths also require TP2, which is notoriously hard to get right, and several published algorithms were later shown to be incorrect.

**Pros**: compact ops, no per-character metadata, a mature approach, and a natural fit for a server-authoritative product.

**Cons**: transform functions multiply with op types (insert, delete, format, table operations...), so correctness is subtle. The client-server OT design here uses a central sequencer per document; decentralized OT protocols also exist. Offline edits that diverge a long way take a lot of transforms to rebase.

## Check both histories

An optimistic client has applied its own edits before the server confirms them. An incoming remote operation therefore cannot be copied directly onto the screen: it was expressed against a server revision that predates those local edits. The client transforms the remote operation through the outstanding local operation and then through the buffer. It also rebases its pending local operations through the incoming remote change so that their later submission matches the server history.

Keep the example's scope narrow. The single insertion and deletion demonstrate one positional case. Equal-position inserts, overlapping deletions and rich-text formatting introduce additional transformation rules. Convergence and preserving an intended target are separate checks; the worked example does not prove a complete OT library correct.

## Key takeaways
- Transform positions to preserve the selected characters under concurrent edits.
- Client-server protocols track acknowledged revision, in-flight operation and local buffer.
- A server alone does not prove TP1 or TP2; protocol and transformation laws need joint verification.

## Further reading

- [Google Docs conflict resolution (2010)](https://drive.googleblog.com/2010/09/whats-different-about-new-google-docs_22.html) — the historical engineering explanation of OT.
