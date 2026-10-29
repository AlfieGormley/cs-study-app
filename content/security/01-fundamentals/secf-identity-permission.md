---
id: secf-identity-permission
title: Identity and permission are different
level: basic
minutes: 3
sourceLesson: secf-cia-aaa
summary: Identification claims an identity; authentication checks evidence.
---

## AAA: authentication, authorisation, accounting

The CIA properties are goals. AAA is the plumbing most systems use to reach them.

```
 request
   |
   v
+-----------------+  who are you?
| Authentication  |---- reject
+-----------------+
   | identity
   v
+-----------------+  may you do this?
| Authorisation   |---- deny
+-----------------+
   | allowed
   v
 resource
   |
   v
+-----------------+  what happened?
| Accounting      |--> audit log
+-----------------+
```

### Authentication: who are you?

The system verifies a claimed identity, using something you know (password), have (security key, phone) or are (fingerprint). The lesson on authentication covers this in depth.

Note the distinction between **identification** (claiming to be `alice`) and **authentication** (checking evidence for that claim). Typing a username is identification; the password is authentication.

> [!analogy] Real-world analogy: checking into a hotel
> At reception you give your name, show your passport and receive a key card. The card opens your room and no other, and the door lock records each time it is used.
>
> **How it maps:** Giving your name is identification. Checking the passport is authentication. The card opening only room 214 is authorisation for one specific object. The lock's entry record is accounting.
>
> **Where it stops:** The key card works for whoever holds it, and reception never sees who uses it later. A web session token behaves the same way after login, so a stolen token bypasses the passport check.

### Authorisation: what may you do?

Once the system knows who you are, it decides whether *this* identity may perform *this* action on *this* resource. Alice may read her own payslip but not Bob's. This is **access control**, covered in its own lesson.

HTTP `401 Unauthorized` means the request lacks valid authentication credentials for the target resource; the response must include a `WWW-Authenticate` challenge. `403 Forbidden` means the server understood the request but refuses it. A 403 can reflect insufficient permissions, but does not itself prove the requester was authenticated.

> [!tip] Authentication is not authorisation
> Many breaches involve a perfectly authenticated user doing something they were never authorised to do, such as changing `/invoices/1001` to `/invoices/1002` in the URL. Checking that a user is logged in is not the same as checking that they may access that object.

## Key takeaways
- Identification claims an identity; authentication checks evidence.
- Authorisation checks the action and specific object.
- 401 requires a challenge; 403 alone does not prove successful login.

## Further reading
- [RFC 9110: HTTP semantics](https://www.rfc-editor.org/rfc/rfc9110.html)
- [OWASP Authorization Cheat Sheet](https://cheatsheetseries.owasp.org/cheatsheets/Authorization_Cheat_Sheet.html)
