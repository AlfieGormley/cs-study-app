---
id: nsec-wpa2-derived-keys
title: WPA2 passphrase and session key derivation
level: advanced
minutes: 4
summary: WPA2-Personal derives a PMK with the SSID as salt and 4,096 PBKDF2 iterations.
sourceLesson: nsec-wireless
---

Replacing WEP requires authenticated encryption and a sound key hierarchy. This unit separates the passphrase-derived pairwise key-derivation secret from the keys used for one client’s protected traffic.

## WPA2

**WPA** (2003) was a stop-gap (TKIP) that ran on WEP hardware. **WPA2** (IEEE 802.11i, 2004) is the real fix, using AES in CCMP mode for authenticated encryption. It comes in two flavours:

| Mode | Authentication | Used in |
|---|---|---|
| Personal (PSK) | Shared passphrase | Homes, small offices |
| Enterprise | 802.1X / EAP per user | Companies, eduroam |

In Personal mode the passphrase is stretched into a 256-bit **Pairwise Master Key** (PMK) using PBKDF2 with HMAC-SHA1, 4,096 iterations, and the network name (SSID) as the salt. Stretching means deliberately repeating a hash thousands of times, so that each guess an attacker tries costs thousands of hash computations too. Salting with the SSID means the same passphrase gives different PMKs on differently named networks:

```formula reference
PMK = PBKDF2(HMAC-SHA1, P, SSID,
             4096, 256)
where
PMK: Pairwise Master Key, the 256-bit pairwise key-derivation secret used to derive WPA2-Personal pairwise keys; the AP supplies group key material separately
PBKDF2: Password-Based Key Derivation Function 2: applies a keyed hash many times to turn a password into a key; its inputs are, in order, the hash function, the password, the salt, the iteration count and the output length in bits
HMAC-SHA1: the keyed hash PBKDF2 repeats here: HMAC built on the SHA-1 hash function
P: the passphrase, 8 to 63 printable ASCII characters
SSID: the network name, used as the salt so that the same passphrase gives different keys on differently named networks
In words: the PMK is the passphrase hashed 4,096 times with the network name mixed in, giving a 256-bit key.
```

Because the salt is the SSID, a table of precomputed PMKs built for one exact SSID can be reused on every other network with that same name (common defaults such as `linksys` are popular targets), but not across arbitrary different names.

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

Both sides then derive the session key from the PMK, the two random nonces and both MAC addresses, all of which except the PMK are exchanged in the clear:

```formula reference
PTK = PRF(PMK, N_A, N_S, MAC_AP, MAC_C)
where
PTK: Pairwise Transient Key, the session's set of keys for protecting unicast traffic between this client and AP
PRF: pseudo-random function: a keyed function (built on HMAC in WPA2) that expands a key and inputs into as many key bits as needed; 802.11i also feeds it a fixed label and puts the addresses and nonces in sorted order
PMK: Pairwise Master Key, from the passphrase (Personal) or from 802.1X (Enterprise)
N_A: ANonce, the random number the AP sends in M1
N_S: SNonce, the random number the client sends in M2
MAC_AP: the AP's MAC address
MAC_C: the client's MAC address
In words: the session key mixes the long-term PMK with two fresh random numbers and both addresses, so every handshake gives a new PTK.
```

- Fresh nonces separate PTK derivations for distinct handshakes under the same PMK; secure nonce generation and correct key-installation state are required.
- The **MIC** on M2 proves the client knows the PMK; the MIC on M3 proves the AP does. That mutual proof is what resists a stranger's AP completing this authenticated handshake as yours, as long as the stranger does not know the passphrase.
- M3 also delivers the **Group Temporal Key** (GTK) used for broadcast and multicast frames.

In WPA2-Personal every device derives the same PMK from the shared passphrase. Fresh nonces keep each session's PTK different, but anyone who knows the passphrase and captures a client's handshake can derive that client's PTK; the next units show how the same captured data enables offline guessing.

## Key takeaways
- WPA2-Personal derives a PMK with the SSID as salt and 4,096 PBKDF2 iterations.
- The four-way handshake derives per-session key material from nonces and addresses.
- MICs confirm key possession; correct nonce generation and installation still matter.

## Further reading
- [Wi-Fi Protected Access — Wikipedia](https://en.wikipedia.org/wiki/Wi-Fi_Protected_Access)
- [IEEE 802.11i-2004 — Wikipedia](https://en.wikipedia.org/wiki/IEEE_802.11i-2004)
- [RFC 8018: PKCS #5 (PBKDF2)](https://www.rfc-editor.org/rfc/rfc8018)
