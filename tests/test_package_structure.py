"""Test that the package structure is properly set up."""

import pytest


def test_imports():
    """Test that all main functions can be imported."""
    from marginal_child import (
        COLORS,
        MAX_CHILDREN,
        UK_REGIONS,
        US_STATES,
        calculate_marginal_child_benefits,
        calculate_uk_marginal_tax_rates,
        calculate_us_marginal_tax_rates,
        get_child_ordinal,
    )

    assert COLORS is not None
    assert MAX_CHILDREN == 4
    assert len(UK_REGIONS) > 0
    assert len(US_STATES) > 0
    assert callable(calculate_marginal_child_benefits)
    assert callable(calculate_uk_marginal_tax_rates)
    assert callable(calculate_us_marginal_tax_rates)
    assert callable(get_child_ordinal)


def test_get_child_ordinal():
    """Test ordinal number generation."""
    from marginal_child import get_child_ordinal

    assert get_child_ordinal(1) == "1st"
    assert get_child_ordinal(2) == "2nd"
    assert get_child_ordinal(3) == "3rd"
    assert get_child_ordinal(4) == "4th"


def test_constants():
    """Test that constants are properly defined."""
    from marginal_child.constants import (
        COLORS,
        FONT_FAMILY,
        LOGO_URL,
        UK_DEFAULT_CHILDCARE_PER_CHILD,
        UK_DEFAULT_RENT,
        UK_INCOME_MAX,
    )

    # Check app-v2 colors
    assert COLORS["primary"] == "#319795"  # Teal-500
    assert COLORS["gray_400"] == "#9CA3AF"
    assert COLORS["teal_300"] == "#4FD1C5"

    # Check font
    assert "Inter" in FONT_FAMILY

    # Check logo
    assert "teal.png" in LOGO_URL

    # Check UK defaults
    assert UK_DEFAULT_RENT == 12000  # £1k/month * 12
    assert UK_DEFAULT_CHILDCARE_PER_CHILD == 8000
    assert UK_INCOME_MAX == 200000


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
