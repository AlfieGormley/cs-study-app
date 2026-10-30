---
id: nsec-enterprise-wifi-identities
title: 802.1X identities and server certificate checks
level: advanced
minutes: 4
summary: 802.1X separates the supplicant, authenticator and authentication server roles.
sourceLesson: nsec-wireless
---

A shared Wi-Fi passphrase makes individual user revocation awkward. Enterprise authentication supplies separate credentials, but its protection still depends on the EAP method and the client’s server validation policy.

## 802.1X and WPA-Enterprise

In Enterprise mode there is no shared passphrase. **802.1X** splits authentication across three roles:

```
 Supplicant    Authenticator  Auth server
 (laptop)      (AP/switch)    (RADIUS)
   | EAP/802.11  | EAP/RADIUS   |
   |<----------->|<------------>|
   | AP relays until success    |
   |             |<-- PMK ------|
   |<- 4-way --->|              |
```

1. The controlled data port remains unauthorised while authentication proceeds; EAPOL and necessary link-management traffic are separate.
2. The client and the RADIUS server run an **EAP method** through the AP.
3. With a key-generating EAP method and the illustrated RADIUS deployment, exported keying material reaches the authenticator over the AAA channel; the link layer derives/selects its PMK. RADIUS is a common backend, not a requirement of every 802.1X deployment.
4. The normal four-way handshake follows.

Independent authentication credentials and pairwise key derivation prevent one ordinary user's credentials from deriving another's unicast keys. Group traffic can still use a shared GTK, and caching/roaming can reuse PMKs; isolation is not a claim that every frame has a unique per-user key. Access can be revoked per user and logged per user, and the RADIUS server can assign VLANs by role, which ties Wi-Fi into the segmentation of the earlier firewall and segmentation units. The same 802.1X runs on wired switch ports.

> [!analogy] Real-world analogy: personal staff passes instead of one door code
> An office that gives everyone the same door code must change it for all 500 staff when one person leaves. Issuing personal passes, checked by a central security desk, lets one pass be cancelled and logs who entered when. But a staff member who hands their password to anyone wearing a security-guard uniform, without checking the guard is real, can still be fooled.
>
> **How it maps:** The shared door code is WPA2-Personal's passphrase; the personal passes and central desk are 802.1X credentials checked by the RADIUS authentication server, with the access point relaying. The fake guard is an evil-twin access point running its own RADIUS server, and checking the guard's credentials is validating the server certificate's CA and name.
>
> **Where it stops:** The "uniform" here is a TLS certificate, which can be checked mathematically if the client is configured with the right CA and server name; with EAP-TLS the client proves itself with a certificate rather than a reusable password. Group traffic still shares one group key, unlike fully individual passes.

The EAP method matters:

| Method | Client proves with | Risk |
|---|---|---|
| EAP-TLS | Certificate | Needs a client PKI |
| PEAP / EAP-TTLS | Password in a TLS tunnel | Weak if server cert not checked |

> [!warning] The PEAP evil twin
> PEAP wraps a password exchange (usually MSCHAPv2) inside TLS from the RADIUS server. If clients do not check that server certificate against the right CA and name, an attacker runs an evil twin AP with their own RADIUS server, clients happily complete the tunnel, and the attacker captures MSCHAPv2 exchanges. Captured MSCHAPv2 challenge responses permit offline attacks on its DES-based construction, which can recover an NT password hash without necessarily recovering the plaintext password. Deploy a profile validating the intended CA and server name. EAP-TLS avoids password-based inner authentication but still requires server validation.

## Defending a wireless network

- Use **WPA3**, or WPA2 with long random passphrases where you must, and enable PMF.
- Prefer **802.1X with EAP-TLS** for organisations; validate server certificates on every client.
- Put guest and IoT devices on separate SSIDs and VLANs, isolated from internal networks.
- Run **wireless intrusion detection** to spot rogue APs, evil twins and floods of deauth frames.
- Treat Wi-Fi, even WPA3, as one layer: TLS and VPNs on top mean a Wi-Fi compromise does not expose application data.

## Key takeaways
- 802.1X separates the supplicant, authenticator and authentication server roles.
- Individual credentials enable individual access decisions and pairwise key separation; group keys remain shared.
- Validate the intended server CA and name for PEAP and EAP-TLS deployments.

## Further reading
- [IEEE 802.1X — Wikipedia](https://en.wikipedia.org/wiki/IEEE_802.1X)
- [RFC 5216: The EAP-TLS Authentication Protocol](https://www.rfc-editor.org/rfc/rfc5216)
- [Wi-Fi Protected Access — Wikipedia](https://en.wikipedia.org/wiki/Wi-Fi_Protected_Access)
