import pytest

from utils_funcs import one_rep_max


def test_one_rep_max():
    assert one_rep_max(100,1)==100
    assert one_rep_max(100, 5) == pytest.approx(100 * 36 / (37 - 5))  # Brzycki formula
    assert one_rep_max(80, 10) == pytest.approx(80 * 36 / (37 - 10))


def test_invalid():
    with pytest.raises(ValueError):
        one_rep_max(100,37) 
        