"""The Marginal Child - PolicyEngine Tax and Benefit Analysis Package."""

# Export pure calculation functions (no UI dependencies)
from marginal_child.pure_calculations import (
    calculate_uk_mtr_absolute,
    calculate_uk_net_income_absolute,
    calculate_us_mtr_absolute,
    calculate_us_net_income_absolute,
    derive_marginal_from_absolute,
)

# Export constants
from marginal_child.constants import (
    COLORS,
    DEFAULT_REGION_INDEX,
    DEFAULT_STATE_INDEX,
    FONT_FAMILY,
    LOGO_URL,
    MAX_CHILDREN,
    UK_REGIONS,
    US_STATES,
)

__version__ = "2.0.0"

__all__ = [
    # Pure calculation functions
    "calculate_uk_mtr_absolute",
    "calculate_uk_net_income_absolute",
    "calculate_us_mtr_absolute",
    "calculate_us_net_income_absolute",
    "derive_marginal_from_absolute",
    # Constants
    "COLORS",
    "DEFAULT_REGION_INDEX",
    "DEFAULT_STATE_INDEX",
    "FONT_FAMILY",
    "LOGO_URL",
    "MAX_CHILDREN",
    "UK_REGIONS",
    "US_STATES",
]
