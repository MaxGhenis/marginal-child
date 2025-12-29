"""Test that marginal MTR calculations produce sensible results."""

import pytest
from marginal_child.chart_utils import derive_marginal_from_absolute


def test_marginal_mtr_basic():
    """Test basic marginal MTR calculation."""
    # Simulate MTR data that increases with more children
    data = [
        {"income": 10000, "num_children": 0, "mtr": 0.20},
        {"income": 10000, "num_children": 1, "mtr": 0.25},
        {"income": 10000, "num_children": 2, "mtr": 0.30},
        {"income": 20000, "num_children": 0, "mtr": 0.30},
        {"income": 20000, "num_children": 1, "mtr": 0.35},
        {"income": 20000, "num_children": 2, "mtr": 0.40},
    ]

    result = derive_marginal_from_absolute(data, "mtr", "marginal_mtr")

    # Should have marginal values for children 1 and 2 only
    assert len(result) == 4  # 2 incomes × 2 marginal children

    # Check marginal MTR values
    income_10k = [r for r in result if r["income"] == 10000]
    assert len(income_10k) == 2
    assert income_10k[0]["marginal_mtr"] == 0.05  # 0.25 - 0.20
    assert income_10k[1]["marginal_mtr"] == 0.05  # 0.30 - 0.25


def test_marginal_mtr_with_noise():
    """Test that small numerical noise doesn't create huge spikes."""
    # Simulate slightly noisy MTR data (common with numerical gradients)
    data = [
        {"income": 10000, "num_children": 0, "mtr": 0.2001},
        {"income": 10000, "num_children": 1, "mtr": 0.2003},
        {"income": 10100, "num_children": 0, "mtr": 0.1999},
        {"income": 10100, "num_children": 1, "mtr": 0.2002},
    ]

    result = derive_marginal_from_absolute(data, "mtr", "marginal_mtr")

    # Marginal values should be small (noise level)
    for r in result:
        assert abs(r["marginal_mtr"]) < 0.01, f"Marginal MTR too large: {r['marginal_mtr']}"


def test_detect_problematic_discontinuities():
    """Test detection of discontinuities that cause spikes."""
    # Simulate discontinuous MTR (e.g., from cliff effects)
    data = [
        {"income": 99900, "num_children": 0, "mtr": 0.40},
        {"income": 99900, "num_children": 1, "mtr": 0.45},
        {"income": 100000, "num_children": 0, "mtr": 0.62},  # Personal allowance taper
        {"income": 100000, "num_children": 1, "mtr": 0.62},
        {"income": 100100, "num_children": 0, "mtr": 0.62},
        {"income": 100100, "num_children": 1, "mtr": 0.62},
    ]

    result = derive_marginal_from_absolute(data, "mtr", "marginal_mtr")

    # At £100k, the discontinuity is the same for both, so marginal change is small
    income_100k = next(r for r in result if r["income"] == 100000)
    # Should be close to 0 because both jump by same amount
    assert abs(income_100k["marginal_mtr"]) < 0.05


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
