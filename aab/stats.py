"""Trend statistics: Mann-Kendall test and Sen's slope with a confidence interval.

Formulas follow Mann (1945), Sen (1968) and Gilbert (1987). The Mann-Kendall variance
ignores ties, which suits continuous annual values. Tests can be compared with
scipy.stats.theilslopes in tests/test_stats.py.
"""
import math
from dataclasses import dataclass

import numpy as np


@dataclass(frozen=True)
class MannKendall:
    s: float
    z: float
    p_value: float


@dataclass(frozen=True)
class SenSlope:
    slope: float          # units of y per unit of t (for years: per year)
    lower: float          # lower bound of the 95% interval
    upper: float          # upper bound of the 95% interval
    intercept: float


def mann_kendall(x) -> MannKendall:
    x = np.asarray(x, dtype=float)
    n = len(x)
    s = sum(float(np.sign(x[i + 1:] - x[i]).sum()) for i in range(n - 1))
    var_s = n * (n - 1) * (2 * n + 5) / 18
    z = 0.0 if s == 0 else ((s - 1) if s > 0 else (s + 1)) / math.sqrt(var_s)
    p_value = math.erfc(abs(z) / math.sqrt(2))
    return MannKendall(s=s, z=z, p_value=p_value)


def sen_slope(t, x) -> SenSlope:
    t = np.asarray(t, dtype=float)
    x = np.asarray(x, dtype=float)
    n = len(x)
    if n < 3:
        raise ValueError("Sen's slope needs at least 3 values")
    var_s = n * (n - 1) * (2 * n + 5) / 18
    slopes = np.sort(np.concatenate([(x[i + 1:] - x[i]) / (t[i + 1:] - t[i]) for i in range(n - 1)]))
    big_n = len(slopes)
    c = 1.96 * math.sqrt(var_s)
    m1 = round((big_n - c) / 2)
    m2 = round((big_n + c) / 2) + 1
    slope = float(np.median(slopes))
    lower = float(slopes[max(m1 - 1, 0)])
    upper = float(slopes[min(m2 - 1, big_n - 1)])
    intercept = float(np.median(x - slope * t))
    return SenSlope(slope=slope, lower=lower, upper=upper, intercept=intercept)
