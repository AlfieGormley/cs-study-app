# test_pricing.py
import pytest
from pricing import apply_discount

def test_ten_percent_off():
    assert apply_discount(50.0, 10) == 45.0

def test_full_discount_is_free():
    assert apply_discount(50.0, 100) == 0.0

def test_rejects_negative_percent():
    with pytest.raises(ValueError):
        apply_discount(50.0, -5)
