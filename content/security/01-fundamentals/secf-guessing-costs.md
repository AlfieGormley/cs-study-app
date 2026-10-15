---
id: secf-guessing-costs
title: Calculate offline guessing costs
level: intermediate
minutes: 3
sourceLesson: secf-authentication
summary: Divide the stated search space by the assumed guessing rate.
---

Offline guessing begins after an attacker obtains password-verification data. Login throttling does not limit these local calculations. The rates below are invented assumptions for comparing search costs, not measurements of an attacker or device.


### Why slowness matters: a calculation

Suppose an attacker steals a database of 8-character random passwords drawn from the 94 non-space printable ASCII characters: about 6.1 thousand million million possibilities. Assume **unsalted fast SHA-256** and an illustrative ten billion guesses a second. The worst-case time to try every possibility is the size of the search divided by the guess rate:

```formula
T = S / G
T = 6.1 × 10^15 / (10^10 per s)
T = 6.1 × 10^5 s
T = (6.1 × 10^5 / 86400) days
T ≈ 7.1 days
where
T: the worst-case time to try every possible password once
S: the size of the search space: 94^8 ≈ 6.1 × 10^15 possible passwords
G: the guess rate: candidates the attacker hashes and checks per second; 10^10 is an assumed illustrative figure, not a hardware benchmark
s: seconds
86400: the number of seconds in a day (24 × 60 × 60)
days: the unit of the final answer, one day being 86,400 s
≈: approximately equal to (rounded)
In words: ten billion guesses a second exhausts every 8-character random password in about a week; on average the right one turns up halfway, after about 3.5 days.
```

Because there is no salt, each candidate digest can be compared against all unsalted hashes using the same scheme, so exhausting this space can find all accounts whose passwords belong to it. This simplified comparison assumes digest lookup across the database adds no limiting cost; it is not a complete hardware or multi-target benchmark. Exhausting this space covers only passwords in the assumed eight-character alphabet.

With a **salted** hash, the work is repeated **per user**: a candidate hashed with Alice's salt is useless against Bob's.

With a **memory-hard** hash tuned so each guess costs, say, ten thousand times more, the same search for one user takes:

```formula
T_slow = S × k / G
T_slow = (6.1 × 10^15 × 10^4 / 10^10) s
T_slow = 6.1 × 10^9 s
T_slow = (6.1 × 10^9 / 31557600) years
T_slow ≈ 193 years
where
T_slow: the worst-case time to exhaust the search space for one user with the slow hash
S: the size of the search space: about 6.1 × 10^15 possible passwords
k: the slowdown factor: how many times more each guess costs than with fast SHA-256; 10^4 is an assumed example
G: the fast-hash guess rate, 10^10 guesses per second (assumed)
s: seconds
31557600: the number of seconds in an average year of 365.25 days
years: the unit of the final answer
≈: approximately equal to (rounded)
In words: making each guess ten thousand times more expensive turns a one-week search into one of around 190 years, for every user separately.
```

The numbers are illustrative, but the shape is real: distinct salts prevent sharing the same candidate-hash computation across accounts. Total attack cost also depends on targeting, password distribution and stopping rules; it is not universally an exact user-count multiplier. No hardware benchmark is supplied for these illustrative rates.

## Key takeaways
- Divide the stated search space by the assumed guessing rate.
- Distinct salts prevent reuse of the same candidate hash across accounts.
- Slowdown factors are assumptions, not hardware benchmarks.

## Further reading
- [OWASP Password Storage Cheat Sheet](https://cheatsheetseries.owasp.org/cheatsheets/Password_Storage_Cheat_Sheet.html)
- [NIST SP 800-63B-4: authentication](https://pages.nist.gov/800-63-4/sp800-63b.html)
