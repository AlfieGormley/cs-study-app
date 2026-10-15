---
id: app-email-imap-identities
title: "Mailbox synchronisation with IMAP identities"
level: intermediate
minutes: 3
sourceLesson: app-email
summary: "IMAP sequence numbers can move; a durable cached identity needs mailbox context, UIDVALIDITY and UID."
---

## Retrieval: IMAP and POP3

**POP3** (port 110, or 995 with implicit TLS) retrieves messages and supports deletion; clients can also leave messages on the server. It lacks IMAP's richer server-side mailbox and flag model.

**IMAP** (port 143, or **993** with TLS; current version IMAP4rev2, [RFC 9051](https://www.rfc-editor.org/rfc/rfc9051)) keeps mail **on the server** and lets many clients view and modify it. Folders, read and flagged states, and moves all sync between devices.

Each IMAP command starts with a client-chosen label, an **IMAP tag**, used to match responses. Some commands can be outstanding concurrently, subject to protocol ordering rules. This abbreviated exchange assumes TLS is already established; the FETCH response body and other required SELECT responses are omitted:

```
C: a1 LOGIN bob secret
S: a1 OK LOGIN completed
C: a2 SELECT INBOX
S: * 172 EXISTS
S: * OK [UIDVALIDITY 3857529045]
S: a2 OK [READ-WRITE] SELECT done
C: a3 UID FETCH 4827 (FLAGS BODY[])
S: * 172 FETCH (UID 4827 FLAGS ...
S: a3 OK FETCH completed
```

Lines starting with `*` are **untagged responses**: data or notifications. Key ideas:

- **Message sequence numbers** (1 to 172 here) are positions in the mailbox and shift when earlier messages are **expunged**, not merely marked `\Deleted`.
- **UIDs** increase with message assignment and remain stable within a mailbox's UIDVALIDITY generation. A cache identity includes the server/account, mailbox, UIDVALIDITY and UID; mutable flags still need synchronisation.
- **UIDVALIDITY** says whether cached UIDs are still meaningful. If it changes (the mailbox was rebuilt), the client must invalidate the old UID mappings and resynchronise, rather than assume a reused number identifies the same message.
- **Flags** such as `\Seen`, `\Flagged`, `\Deleted` record state. Deleting is two steps: set `\Deleted`, then `EXPUNGE`.
- **IDLE** lets the server send mailbox updates while the client waits. Connections can time out; the client terminates and reissues IDLE periodically and reconnects when needed.

Applications can also use provider APIs or JMAP (RFC 8620), a JSON-based synchronisation framework over HTTP; JMAP Mail is specified separately in RFC 8621. Deployment prevalence is omitted because this review did not establish a reliable measurement.

## Key takeaways
- IMAP sequence numbers can move; a durable cached identity needs mailbox context, UIDVALIDITY and UID.
- Deletion flags, expunging and live updates are distinct operations.

## Further reading
- [RFC 9051](https://www.rfc-editor.org/rfc/rfc9051)
- [RFC 1939](https://www.rfc-editor.org/rfc/rfc1939)
- [RFC 8620](https://www.rfc-editor.org/rfc/rfc8620)
