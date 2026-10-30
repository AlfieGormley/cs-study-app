---
id: nsec-krack-key-state
title: KRACK and key-installation state
level: advanced
minutes: 3
summary: A retransmitted handshake message must not reset an in-use key’s security state.
sourceLesson: nsec-wireless
---

Fresh key derivation is insufficient when a device later reinstalls the same key and resets its packet-number state. KRACK connects a reliability retransmission to that security failure.

## KRACK

In 2017 Mathy Vanhoef published **KRACK** (Key Reinstallation Attacks), a flaw in the WPA2 protocol itself rather than in any one product.

The handshake has a reliability feature: if the AP does not receive M4, it retransmits M3. The standard said the client should install the PTK on receiving M3, and vulnerable implementations reinstalled a key on a retransmitted M3.

```
 attacker (MITM on another channel)
 blocks M4, AP resends M3
 client re-installs the SAME PTK
 -> packet-number component resets
```

Reinstalling the key reset the **CCMP packet number**, which forms part of the CCMP nonce. Now the client encrypted new frames with a nonce, and therefore keystream, it had already used: the same mistake that killed WEP. Nonce reuse can expose relationships between plaintexts and enable decryption with additional known or predictable data; the exact capability depends on cipher and traffic. KRACK also enabled forgery in affected TKIP/GCMP cases. It does not reveal the Wi-Fi passphrase or the PMK, so changing the password does not fix it; patching does.

Worst hit were Linux and Android devices using affected `wpa_supplicant` versions 2.4 and later before fixes, which installed an **all-zero key** after the reinstall, making traffic trivially decryptable.

Fixes ensure keys are not reinstalled in a way that resets their security state. Patch every affected device: client patches do not fix vulnerable AP-side Fast BSS Transition behaviour, nor do ordinary AP patches automatically fix clients. Patched and unpatched devices interoperate, so no new protocol was needed. KRACK showed that even a protocol with a formal security proof can fail where the proof's model (a single key installation) does not match the key-installation logic engineers actually built.

## Key takeaways
- A retransmitted handshake message must not reset an in-use key’s security state.
- KRACK capabilities depended on the affected cipher and implementation.
- Patch affected client and AP roles; one side’s fix does not cover every attack variant.

## Further reading
- [Key Reinstallation Attacks (KRACK) — Mathy Vanhoef](https://www.krackattacks.com/)
- [Key Reinstallation Attacks: Forcing Nonce Reuse in WPA2 (CCS 2017 paper)](https://papers.mathyvanhoef.com/ccs2017.pdf)
- [Wi-Fi Protected Access — Wikipedia](https://en.wikipedia.org/wiki/Wi-Fi_Protected_Access)
