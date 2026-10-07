import pytest
import re

UNITS = {"h": 3600, "m": 60, "s": 1}
TOKEN = re.compile(r"(\d+)([hms])")

def parse_duration(text):
    pos, total = 0, 0
    for m in TOKEN.finditer(text):
        if m.start() != pos:
            raise ValueError(text)
        total += int(m[1]) * UNITS[m[2]]
        pos = m.end()
    if pos != len(text) or not text:
        raise ValueError(text)
    return total

def test_hours():
    assert parse_duration("1h") == 3600

def test_minutes():
    assert parse_duration("90m") == 5400

def test_combined():
    assert parse_duration("1h30m") == 5400

@pytest.mark.parametrize("bad",
    ["", "h", "1x", "1h junk"])
def test_rejects_garbage(bad):
    with pytest.raises(ValueError):
        parse_duration(bad)
