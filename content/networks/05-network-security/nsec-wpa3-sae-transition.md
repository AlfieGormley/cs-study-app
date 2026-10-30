---
id: nsec-wpa3-sae-transition
title: SAE, management frames and WPA3 transition risks
level: advanced
minutes: 3
summary: Correctly implemented fresh SAE resists passive offline password verification and provides forward secrecy under its assumptions.
sourceLesson: nsec-wireless
---

WPA3-Personal changes password authentication, while protected management frames address another attack surface. Open networks use the separate OWE design. Keep those roles distinct when evaluating an access point’s advertised mode.

## WPA3

**WPA3** (2018) addresses WPA2's structural weaknesses:

| WPA2 problem | WPA3 answer |
|---|---|
| Offline guessing | SAE handshake |
| No forward secrecy | SAE derives fresh keys |
| Spoofed deauth frames | PMF mandatory |
| Open Wi-Fi in clear | Separate Enhanced Open programme: OWE |

**SAE** (Simultaneous Authentication of Equals, based on the Dragonfly key exchange) replaces the PSK step. Both sides prove knowledge of the password through a Diffie-Hellman-style exchange that is designed to resist passive offline dictionary verification when correctly implemented. Each guess requires a live exchange with the AP, which can rate-limit. A fresh SAE exchange derives new key material and provides forward secrecy against later password disclosure under its security assumptions. Caching and roaming can reuse key material across associations.

**Protected Management Frames** (802.11w) protect robust management frames such as deauthentication/disassociation once the relevant security association is established. They do not prevent radio jamming or protect every pre-association/control frame. Under WPA2 without PMF, anyone can forge a "deauth" from the AP, kicking clients off to capture their handshake or push them towards an evil twin.

WPA3 is not flawless. The 2019 **Dragonblood** attacks (Vanhoef and Ronen) found timing and cache side channels in SAE implementations, and **downgrade attacks** against *transition mode*, where an AP accepts both WPA2 and WPA3 so old devices can connect: an attacker advertises a WPA2-only copy and captures a crackable WPA2 handshake. Fixes followed (including the hash-to-element method), but transition mode remains a weak spot. Wi-Fi certification requirements for 6 GHz call for WPA3 or Enhanced Open (OWE) with PMF, without WPA2 on that band. This does not prohibit a multi-band SSID from separately serving legacy clients on 2.4 or 5 GHz.

> [!analogy] Real-world analogy: a new front door with the old back door still open
> A building fits a new front door that cannot be picked, but keeps the old back door working for staff who have not yet been issued new fobs. Both doors open with the same staff code. A burglar ignores the new door and watches someone use the old one.
>
> **How it maps:** The new front door is SAE, which resists offline guessing; the old back door is WPA2-Personal kept by transition mode, and the shared code is the single passphrase used by both. An attacker who lures a client into a WPA2 handshake (for example with a WPA2-only fake access point) can crack the passphrase offline and then use it for the WPA3 side too.
>
> **Where it stops:** Clients can be told to remember that a network supports WPA3 and refuse the old door (transition disable), which has no exact building equivalent. And SAE still allows slow online guessing at the "front door", so a weak passphrase remains weak.

**OWE** encrypts open networks (cafés, airports) with an unauthenticated key exchange. It stops passive sniffing, but not an evil twin, because nobody's identity is checked.

## Key takeaways
- Correctly implemented fresh SAE resists passive offline password verification and provides forward secrecy under its assumptions.
- PMF protects selected management frames after keys exist, not all radio traffic.
- WPA2 transition support and implementation side channels can weaken the intended protections.

## Further reading
- [Dragonblood: analysing WPA3's Dragonfly handshake](https://wpa3.mathyvanhoef.com/)
- [RFC 7664: Dragonfly Key Exchange](https://www.rfc-editor.org/rfc/rfc7664)
- [Wi-Fi Protected Access — Wikipedia](https://en.wikipedia.org/wiki/Wi-Fi_Protected_Access)
