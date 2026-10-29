---
id: secf-mandatory-labels
title: Mandatory confidentiality and integrity labels
level: intermediate
minutes: 3
sourceLesson: secf-access-control
summary: Mandatory access control limits ordinary owners through a central policy.
---

DAC lets an object owner choose permissions. Mandatory access control adds centrally enforced restrictions that ordinary owners cannot waive. The following directional rules are simplified level-only models; real policies can include compartments and trusted exceptions.


## Mandatory access control

In **mandatory access control**, a central policy, not the owner, decides. Users can't override it even for their own files. Mandatory access control came from military systems with classification levels (Unclassified < Confidential < Secret < Top Secret).

### Bell–LaPadula: confidentiality

The Bell–LaPadula model constrains confidentiality-related information flows. In this simplified level-only explanation, assume subjects operate at the named level and have no trusted declassification exception:

- **Simple security property: no read up.** A Secret-cleared subject can't read Top Secret.
- **Star property: no write down.** A Secret subject can't write to a Confidential object.

The second rule is the clever one. Without it, a Trojan horse running with Secret clearance could copy Secret data into an Unclassified file.

### Biba: integrity

The **strict integrity** form associated with Biba reverses these directional rules to protect integrity:

- **No read down**: a high-integrity process mustn't consume low-integrity data, which could corrupt it.
- **No write up**: a low-integrity subject mustn't modify high-integrity objects.

```
          Bell-LaPadula    Biba
          (secrecy)        (integrity)
read      no read UP       no read DOWN
write     no write DOWN    no write UP
```

Windows Mandatory Integrity Control normally enforces **no write up** through integrity labels and policy; it is not an implementation of all strict Biba rules. SELinux and AppArmor can confine processes, including root processes, under enforced policies. Actual access also depends on policy configuration and trusted administrative powers.

## Key takeaways
- Mandatory access control limits ordinary owners through a central policy.
- The simplified Bell–LaPadula rules prevent reading up and writing down.
- Strict Biba reverses those directions; Windows MIC is a narrower mechanism.

## Further reading
- [RFC 4949: security terms and models](https://www.rfc-editor.org/rfc/rfc4949)
- [Windows Mandatory Integrity Control](https://learn.microsoft.com/en-us/windows/win32/secauthz/mandatory-integrity-control)
