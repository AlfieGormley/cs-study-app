---
id: secf-guessing-costs
title: Why offline guessing cost matters
level: intermediate
minutes: 3
sourceLesson: secf-authentication
summary: Search time grows with the possibilities and the cost of each guess.
---

Offline guessing begins after an attacker obtains password-verification data. Login throttling does not limit these local calculations: the attacker tests guesses on their own hardware, as fast as it allows. The rates below are invented assumptions for comparing search costs, not measurements of an attacker or device.


### What sets the attacker's time

Three things decide how long an exhaustive search takes: how many candidates there are, how fast the attacker can test them, and how much work each test costs. The defender controls the last one through the choice of password hash:

```formula essential
T = kS / G
where
T: the worst-case time to try every candidate once, in seconds
S: the search space: how many candidate passwords the attacker must consider
k: the slowdown factor: how many times more work each guess costs than a fast hash; 1 for a fast hash such as SHA-256
G: the attacker's rate with the fast hash, in guesses per second
In words: the search takes longer when there are more candidates or when each guess costs more, and shorter only when the attacker can guess faster.
```

For a password chosen at random from that space, the attacker finds it about halfway through on average, so the average time is about half of the worst case.

### An illustrative comparison

Suppose an attacker steals a database of 8-character random passwords drawn from the 94 non-space printable ASCII characters: about 6.1 thousand million million possibilities. Assume **unsalted fast SHA-256** and an illustrative ten billion guesses a second. Every possibility is tried in about a week.

Because there is no salt, each candidate digest can be compared against all unsalted hashes using the same scheme, so that one week of work can find every account whose password lies in this space. This simplified comparison assumes digest lookup across the database adds no limiting cost; it is not a complete hardware or multi-target benchmark.

With a **salted** hash, the work is repeated **per user**: a candidate hashed with Alice's salt is useless against Bob's.

With a **memory-hard** hash tuned so each guess costs, say, ten thousand times more, the same exhaustive search for one user takes around two centuries instead of a week.

> [!analogy] Real-world analogy: a wall of combination lockers
> Imagine a thief alone overnight with a wall of combination lockers. In one version, each code the thief tries is tested on every locker at once, so all owners who chose that code are exposed by one try. In another, each locker must be tried separately, and each try takes a minute.
>
> **How it maps:** Overnight access is the stolen database: no attendant (rate limit) is watching. Testing one code on every locker at once is an unsalted hash; trying each locker separately is a unique salt per user. The minute per try is a slow, memory-hard password hash.
>
> **Where it stops:** A real attacker can buy more hardware to raise the guessing rate, which is why memory-hard functions also make each parallel guess expensive in memory. Owners who chose common codes are still found early whichever lock is used, just as weak passwords fall first.

The numbers are illustrative, but the shape is real: distinct salts prevent sharing the same candidate-hash computation across accounts, and a costly hash multiplies the time of every guess. Total attack cost also depends on targeting, password distribution and stopping rules; it is not universally an exact user-count multiplier.

## Key takeaways
- Search time grows with the number of candidates and the cost per guess.
- Distinct salts prevent reuse of the same candidate hash across accounts.
- Slowdown factors are assumptions, not hardware benchmarks.

## Further reading
- [OWASP Password Storage Cheat Sheet](https://cheatsheetseries.owasp.org/cheatsheets/Password_Storage_Cheat_Sheet.html)
- [NIST SP 800-63B-4: authentication](https://pages.nist.gov/800-63-4/sp800-63b.html)
