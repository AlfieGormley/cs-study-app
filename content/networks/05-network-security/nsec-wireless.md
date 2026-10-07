---
id: nsec-wireless
title: Wi-Fi security: WEP, WPA2, KRACK, WPA3 and 802.1X
level: advanced
minutes: 15
summary: Why WEP fell apart, how the WPA2 four-way handshake derives keys and how KRACK broke it, how WPA2-Personal permits offline guessing, what correctly implemented SAE changes, and how enterprise authentication separates unicast keys.
---

Wired networks have a physical boundary: to sniff a cable you need to reach it. Wi-Fi signals may extend beyond the intended premises. Capture depends on channel, signal, interference and receiver capabilities; being nearby does not guarantee reception of every frame.

So Wi-Fi security has to provide in protocol what walls provide for Ethernet:

- **Access control**: only authorised devices may join.
- **Confidentiality and integrity** for protected data, with separate protection rules for management traffic; many headers and control frames remain exposed.
- **Authentication of the network**, so clients do not join an impostor.

The history of Wi-Fi security is a tour of how to get these wrong, and it is worth studying because the same mistakes recur in other protocols.

## WEP: what not to do

**WEP**, introduced with the original 802.11 standard, encrypted protected data-frame payloads with the RC4 stream cipher, using a key built from a shared 40- or 104-bit secret plus a 24-bit **initialisation vector** (IV) sent in clear. Integrity came from a CRC-32 checksum.

Its flaws compound:

1. **IV reuse.** Stream ciphers must never reuse a keystream. With only 2^24 (about 16.8 million) IVs, collisions come fast: under independent uniform random IV selection with replacement, the birthday approximation gives a 50% collision chance after about 4,800 frames. Counter-based choices have different collision behavior until wraparound. For equal IVs under the same WEP key, XORing the encrypted payloads cancels their keystream and reveals the XOR of the plaintexts; recovering either plaintext needs further information.
2. **Weak RC4 key scheduling.** The Fluhrer–Mantin–Shamir attack (2001), and the much faster PTW attack (2007), recover the key from captured traffic. The 2007 PTW paper reports recovery of a 104-bit WEP key with fewer than 40,000 frames in half its cases, using an active attack. Its sub-minute collection result involved reinjection on an 802.11g network; this is an experiment-specific result, not a guarantee for any busy network.
3. **CRC-32 is not a MAC.** Its algebraic structure permits predictable checksum adjustments when bits are flipped; CRC-32 conventions include fixed initial/final terms, so the general relation is affine rather than simply CRC(a XOR b) = CRC(a) XOR CRC(b). It is not a keyed authenticator.
4. **Shared-key management** makes individual revocation and safe rotation difficult; WEP does not require that operators literally never change keys.

WEP is obsolete and should not be used. The lessons: never reuse a nonce, use a real MAC, and derive fresh per-session keys.

## WPA2

**WPA** (2003) was a stop-gap (TKIP) that ran on WEP hardware. **WPA2** (IEEE 802.11i, 2004) is the real fix, using AES in CCMP mode for authenticated encryption. It comes in two flavours:

| Mode | Authentication | Used in |
|---|---|---|
| Personal (PSK) | Shared passphrase | Homes, small offices |
| Enterprise | 802.1X / EAP per user | Companies, eduroam |

In Personal mode the passphrase is stretched into a 256-bit **Pairwise Master Key** (PMK):

```
PMK = PBKDF2(HMAC-SHA1, passphrase,
             salt = SSID,
             4096 iterations, 256 bits)
```

```python
import hashlib

def pmk(passphrase, ssid):
    password = passphrase.encode("ascii")
    name = ssid.encode("ascii")
    if not 8 <= len(password) <= 63:
        raise ValueError("password length")
    if not 1 <= len(name) <= 32:
        raise ValueError("SSID length")
    return hashlib.pbkdf2_hmac(
        "sha1", password, name, 4096, 32)

print(pmk("password", "IEEE").hex()[:16])
```

This ASCII-only passphrase example (not raw hexadecimal PSK provisioning) prints `f42c6fc52df0ebef`, the beginning of the derived 256-bit key for those inputs. Note that the SSID is the salt, so a table for one exact SSID can be reused on other networks with that same SSID, not across arbitrary different names.

### The four-way handshake

The PMK is never used to encrypt traffic directly. Instead, after association, the access point (authenticator) and client (supplicant) run the **four-way handshake** to derive a fresh **Pairwise Transient Key** (PTK) for this session:

```
 AP                              Client
 M1: ANonce  ------------------>
                  client picks SNonce,
                  derives PTK
             <------------------ M2:
                       SNonce + MIC
 AP derives PTK,
 checks MIC
 M3: GTK (encrypted) + MIC ----->
                  client INSTALLS PTK
             <------------------ M4: ack
 AP installs PTK
```

```
PTK = PRF(PMK, ANonce, SNonce,
          AP MAC, client MAC)
```

- Fresh nonces separate PTK derivations for distinct handshakes under the same PMK; secure nonce generation and correct key-installation state are required.
- The **MIC** on M2 proves the client knows the PMK; the MIC on M3 proves the AP does. That mutual proof is what stops a stranger's AP pretending to be yours, as long as the stranger does not know the passphrase.
- M3 also delivers the **Group Temporal Key** (GTK) used for broadcast and multicast frames.

### The offline cracking problem

Look at what an eavesdropper captures: ANonce, SNonce, both MAC addresses, and a MIC computed from a PTK that depends only on those values and the PMK. So they can test passphrase guesses **offline**:

```
for guess in wordlist:
    p = pmk(guess, ssid)
    if mic(ptk(p, nonces), M2) == seen:
        found!
```

No further contact with the network is needed, so there is no lockout. The 4,096 PBKDF2 iterations add work per guess. The rate depends on hardware and implementation; the next example uses a hypothetical rate. In some configurations, a captured **PMKID**, derived using the PMK, a fixed label and both MAC addresses, supplies another offline verifier without a victim client handshake.

> [!example] How long does a password last?
> An 8-character all-lowercase passphrase has 26^8 ≈ 2.1 × 10^11 possibilities. At an assumed constant 10^6 distinct guesses a second, exhausting them takes about 2.1 × 10^5 seconds, roughly 58 hours, and on average half that. Human choices can be nonuniform and vulnerable to dictionary order. Uniformly choosing five words from a specified large list gives a much larger finite search space (calculated in the quiz); security still depends on the list, selection process and attacker resources.

WPA2-Personal's resistance to this offline guessing attack depends on passphrase strength. An observer who knows the shared passphrase and captures the needed handshake can derive another client's link-layer keys; application TLS can still protect the application payload. Implementation and management-frame security also matter.

## KRACK

In 2017 Mathy Vanhoef published **KRACK** (Key Reinstallation Attacks), a flaw in the WPA2 protocol itself rather than in any one product.

The handshake has a reliability feature: if the AP does not receive M4, it retransmits M3. The standard said the client should install the PTK on receiving M3, and vulnerable implementations reinstalled a key on a retransmitted M3.

```
 attacker (MITM on another channel)
 blocks M4, AP resends M3
 client re-installs the SAME PTK
 -> packet-number component resets
```

Reinstalling the key reset the **packet number**, which forms part of the CCMP nonce. Now the client encrypted new frames with a nonce, and therefore keystream, it had already used: the same mistake that killed WEP. Nonce reuse can expose relationships between plaintexts and enable decryption with additional known or predictable data; the exact capability depends on cipher and traffic. KRACK also enabled forgery in affected TKIP/GCMP cases.

Worst hit were Linux and Android devices using affected `wpa_supplicant` versions 2.4 and later before fixes, which installed an **all-zero key** after the reinstall, making traffic trivially decryptable.

Fixes ensure keys are not reinstalled in a way that resets their security state. Patch every affected device: client patches do not fix vulnerable AP-side Fast BSS Transition behavior, nor do ordinary AP patches automatically fix clients. Patched and unpatched devices interoperate, so no new protocol was needed. KRACK showed that even a protocol with a formal security proof can fail where the proof's model (a single key installation) does not match the state machine engineers actually built.

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

**OWE** encrypts open networks (cafés, airports) with an unauthenticated key exchange. It stops passive sniffing, but not an evil twin, because nobody's identity is checked.

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

Independent authentication credentials and pairwise key derivation prevent one ordinary user's credentials from deriving another's unicast keys. Group traffic can still use a shared GTK, and caching/roaming can reuse PMKs; isolation is not a claim that every frame has a unique per-user key. Access can be revoked per user and logged per user, and the RADIUS server can assign VLANs by role, which ties Wi-Fi into the segmentation of lesson 2. The same 802.1X runs on wired switch ports.

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

> [!note] Content omitted after review
> Universal GPU guessing rates, claims that dictionary attacks usually finish in minutes, and an absolute guarantee that a five-word passphrase is uncrackable are omitted. No hardware benchmark, password distribution or attacker budget was specified; the numerical exercise uses explicit hypothetical assumptions. An exact WEP introduction/deprecation chronology and attribution of the PBKDF2 output to a particular IEEE test-vector publication are also omitted because those original records were not retrieved; the key output itself was executed.

## Key takeaways
- WEP failed through IV reuse, weak RC4 keying, an unkeyed CRC checksum and shared keys; the lessons recur throughout security.
- WPA2's four-way handshake derives a PTK from the PMK, nonces and addresses; freshness depends on correct nonce generation and key installation, and MICs confirm possession of derived keying material.
- WPA2-Personal handshakes (and PMKIDs) allow offline passphrase guessing, so passphrase entropy limits resistance to that guessing attack; other security properties still depend on configuration and implementation.
- KRACK forced key reinstallation, resetting nonces and reusing keystream; affected clients and APs require the relevant patches.
- Correctly implemented pure SAE is designed to resist passive offline password verification and provide forward secrecy under its assumptions. Implementation flaws and WPA2 transition modes can weaken these properties.
- 802.1X gives per-user keys via RADIUS; with PEAP, clients must validate the server certificate or credentials leak to evil twins.

## Further reading
- [Key Reinstallation Attacks (KRACK) — Mathy Vanhoef](https://www.krackattacks.com/)
- [Dragonblood: analysing WPA3's Dragonfly handshake](https://wpa3.mathyvanhoef.com/)
- [Wi-Fi Protected Access — Wikipedia](https://en.wikipedia.org/wiki/Wi-Fi_Protected_Access)
- [Wired Equivalent Privacy — Wikipedia](https://en.wikipedia.org/wiki/Wired_Equivalent_Privacy)
- [IEEE 802.1X — Wikipedia](https://en.wikipedia.org/wiki/IEEE_802.1X)
- [RFC 7664: Dragonfly Key Exchange](https://www.rfc-editor.org/rfc/rfc7664)
