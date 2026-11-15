"""Checks the trend statistics against independent implementations and known cases."""
import numpy as np
import pytest
from scipy import stats as sstats

from aab.stats import mann_kendall, sen_slope


def test_sen_slope_matches_scipy_on_random_series():
    rng = np.random.default_rng(1)
    t = np.arange(1975, 2024, dtype=float)
    x = 330 - 0.1 * (t - 1975) + rng.normal(0, 15, len(t))
    ours = sen_slope(t, x)
    ref = sstats.theilslopes(x, t)
    assert ours.slope == pytest.approx(ref[0], rel=1e-9)
    # scipy uses median(y) - slope * median(t); this module uses median(y - slope * t), the classical Theil form.
    assert ours.intercept == pytest.approx(float(np.median(x - ref[0] * t)), rel=1e-9)


def test_sen_slope_interval_brackets_the_slope():
    t = np.arange(10, dtype=float)
    x = 2 * t + np.array([0, 1, -1, 0.5, -0.5, 0, 1, -1, 0, 0.2])
    res = sen_slope(t, x)
    assert res.lower <= res.slope <= res.upper
    assert res.slope == pytest.approx(2, abs=0.2)


def test_mann_kendall_monotonic_series_is_strongly_significant():
    res = mann_kendall(np.arange(20, dtype=float))
    assert res.s == 20 * 19 / 2
    assert res.p_value < 0.001


def test_mann_kendall_flat_series_has_no_trend():
    res = mann_kendall(np.array([5.0] * 10))
    assert res.s == 0
    assert res.z == 0
    assert res.p_value == pytest.approx(1.0)


def test_sen_slope_needs_three_values():
    with pytest.raises(ValueError):
        sen_slope([1, 2], [1, 2])
