---
id: emb-platform-comparison-score-sensitivity
sourceLesson: emb-platform-comparison
title: "Test the decision against its weights"
level: advanced
minutes: 2
summary: "A weighted total makes priorities explicit but inherits the quality of its inputs."
---

## Step 5: score, then test the scoring

Apply must-haves as pass/fail first. Then score the survivors on each weighted criterion, with a sentence of evidence per score. Each option's total is its scores multiplied by the weights and added up:

```formula
T = Σ (w_c s_c)
T_X = 3 × 4 + 2 × 4 + 1 × 3 = 23
where
T: an option's weighted total; higher is better
Σ: sigma, "add up over every criterion"
w_c: the weight you gave criterion c before scoring, for example 1 to 3
s_c: the option's score on criterion c, for example 1 to 5
c: one criterion, such as audio, debugging or documentation
T_X: the total for placeholder option X below, with weights audio 3, debug 2, docs 1 and scores 4, 4, 3
In words: multiply each score by how much that criterion matters, then add the products; the biggest total wins on paper.
```

Then check whether the result depends on your weights:

```python
# Placeholder scores (1-5), NOT real data.
scores = {
    "X": {"audio": 4, "debug": 4,
          "docs": 3},
    "Y": {"audio": 3, "debug": 2,
          "docs": 5},
}

# Scores are placeholders, not hardware
# data.
def rank(weights):
    total = {
        name: sum(weights[c] * s[c]
                  for c in weights)
        for name, s in scores.items()
    }
    return sorted(total.items(),
                  key=lambda kv: -kv[1])

# Change priorities while keeping scores
# fixed.
print(rank({"audio": 3, "debug": 2,
            "docs": 1}))
# Change priorities while keeping scores
# fixed.
print(rank({"audio": 1, "debug": 1,
            "docs": 3}))
```

```output
[('X', 23), ('Y', 18)]
[('Y', 20), ('X', 17)]
```

Same scores, different weights, opposite winner. That is the point of the exercise: a weighted matrix makes your priorities explicit. If a small, defensible change of weights flips the result, the options are close, and the deciding factor should be a test, not arithmetic.

## Key takeaways
- A weighted total makes priorities explicit but inherits the quality of its inputs.
- If defensible weights reverse the result, gather decisive evidence.

## Further reading
- [Daisy Seed hardware page — Electro-Smith](https://docs.daisy.audio/hardware/Seed/)
- [Daisy Seed datasheet v1.2.0 — Electro-Smith](https://daisy.nyc3.cdn.digitaloceanspaces.com/products/seed/Daisy_Seed_datasheet.pdf)
- [Teensy 4.1 — PJRC](https://www.pjrc.com/store/teensy41.html)
- [Audio adaptor boards for Teensy — PJRC](https://www.pjrc.com/store/teensy3_audio.html)
- [Teensy Audio Library — PJRC](https://www.pjrc.com/teensy/td_libs_Audio.html)
- [Raspberry Pi 5 product brief — Raspberry Pi](https://datasheets.raspberrypi.com/rpi5/raspberry-pi-5-product-brief.pdf)
- [Raspberry Pi audio boards overview — Raspberry Pi documentation source](https://github.com/raspberrypi/documentation/blob/master/documentation/asciidoc/accessories/audio/introduction.adoc)
- [Raspberry Pi audio boards configuration — Raspberry Pi documentation source](https://github.com/raspberrypi/documentation/blob/master/documentation/asciidoc/accessories/audio/configuration.adoc)
- [GPIO on Raspberry Pi — Raspberry Pi documentation source](https://github.com/raspberrypi/documentation/blob/master/documentation/asciidoc/computers/raspberry-pi/gpio-on-raspberry-pi.adoc)
- [Raspberry Pi models and their ports (Pi 5 lists no 3.5 mm jack) — Raspberry Pi documentation source](https://github.com/raspberrypi/documentation/blob/master/documentation/asciidoc/computers/raspberry-pi/introduction.adoc)
