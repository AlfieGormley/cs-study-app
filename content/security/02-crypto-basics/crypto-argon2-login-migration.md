---
id: crypto-argon2-login-migration
sourceLesson: crypto-passwords-kdfs
title: Verify Argon2 hashes and upgrade at login
level: advanced
minutes: 3
summary: Store the self-describing Argon2 record and rehash after successful login when settings change.
---

## Doing it in Python

The `argon2-cffi` library wraps the reference implementation. In argon2-cffi 25.1, defaults derive from RFC 9106's low-memory profile but can vary by platform. The example selects that profile explicitly (64 MiB, three passes, four lanes), generates a random salt and stores parameters with the result.

```python
from argon2 import PasswordHasher
from argon2.profiles import \
    RFC_9106_LOW_MEMORY
from argon2.exceptions import \
    VerifyMismatchError

ph = PasswordHasher.from_parameters(
    RFC_9106_LOW_MEMORY)

# The library generates a new random salt.
stored = ph.hash("correct horse")
# Show only metadata, omitting salt/hash.
header = "$".join(
    stored.split("$")[:4]) + "$"
print(header)

def login(stored, attempt):
    # Stored parameters govern verification.
    try:
        ph.verify(stored, attempt)
    except VerifyMismatchError:
        return False, stored
    # Upgrade only after a correct password.
    if ph.check_needs_rehash(stored):
        stored = ph.hash(attempt)
    return True, stored

# Correct password succeeds; wrong fails.
print(login(stored, "correct horse")[0])
print(login(stored, "battery")[0])
```

This prints:

```
$argon2id$v=19$m=65536,t=3,p=4$
True
False
```

In that header, `m=65536` is the memory in kibibytes (KiB, 1,024 bytes each), which is 64 MiB; `t=3` is three passes and `p=4` is four lanes.

The stored string is self-describing: algorithm, version, parameters, then the salt and hash (cut off here). That is what lets you raise parameters later. `check_needs_rehash` spots hashes made with old settings, and you upgrade them the next time that user logs in successfully, one point at which the submitted password is available. Treat hashes as trusted server-side records, persist upgrades atomically, and handle malformed stored records and operational errors separately; this minimal helper is not a full login endpoint.

> [!analogy] Real-world analogy: Renewing a membership card at the desk
> A gym introduces a more secure membership card. It cannot reissue cards by post, because making the new card needs the member's signature in person. So each time a member with an old card visits and is recognised, the desk swaps the old card for a new one.
>
> **How it maps:** The member's visit is a successful login, the one moment the server holds the plaintext password. Recognising the member is `verify` against the stored hash, the old card is a hash with outdated parameters (spotted by `check_needs_rehash`), and the swap is storing a new hash.
>
> **Where it stops:** Members who never visit keep old cards for ever, just as dormant accounts keep weak hashes; that is why the next paragraph wraps old hashes straight away. And the user never notices the swap: they type the same password, and only the stored record changes.

One temporary migration option is a salted outer Argon2id hash over the legacy SHA-1 representation, marked with its exact old encoding. Replace it with direct Argon2id after successful login. This cannot undo an earlier leak of the fast hash; forced resets may be necessary after compromise. Remove or separately protect retained legacy copies and backups.

## Key takeaways
- Store the self-describing Argon2 record and rehash after successful login when settings change.
- A temporary outer hash can strengthen a legacy table but cannot undo a prior leak.

## Further reading
- [argon2-cffi PasswordHasher API](https://argon2-cffi.readthedocs.io/en/stable/api.html)
- [RFC 9106: Argon2](https://www.rfc-editor.org/rfc/rfc9106)
- [OWASP: Password Storage Cheat Sheet](https://cheatsheetseries.owasp.org/cheatsheets/Password_Storage_Cheat_Sheet.html)
