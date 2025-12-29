"""Pure calculation functions without any UI framework dependencies.

These functions can be used by FastAPI, Streamlit, or any other framework.
"""

import logging
from typing import Dict, Optional, Callable

import pandas as pd
from policyengine_us import Simulation as USSimulation
from policyengine_uk import Simulation as UKSimulation

from marginal_child.constants import (
    DEFAULT_ADULT_AGE,
    DEFAULT_CHILD_AGE,
    INCOME_MAX,
    INCOME_MIN,
    INCOME_STEP,
    UK_CHILD_AGES,
    UK_DEFAULT_CHILDCARE_PER_CHILD,
    UK_DEFAULT_RENT,
    UK_INCOME_MAX,
    UK_PARENT_AGE,
)

logger = logging.getLogger(__name__)


def create_us_household_situation(
    num_children: int,
    year: int,
    marital_status: str,
    state_code: str,
    spouse_income: float,
) -> Dict:
    """Create US household situation."""
    situation = {
        "people": {
            "adult": {
                "age": {year: DEFAULT_ADULT_AGE},
            }
        }
    }

    if marital_status == "married":
        situation["people"]["spouse"] = {
            "age": {year: DEFAULT_ADULT_AGE},
            "employment_income": {year: spouse_income},
        }

    for i in range(num_children):
        situation["people"][f"child_{i+1}"] = {
            "age": {year: DEFAULT_CHILD_AGE}
        }

    members = ["adult"]
    if marital_status == "married":
        members.append("spouse")
    members.extend([f"child_{i+1}" for i in range(num_children)])

    situation["families"] = {"family": {"members": members}}
    situation["households"] = {
        "household": {"members": members, "state_code": {year: state_code}}
    }
    situation["tax_units"] = {"tax_unit": {"members": members}}
    situation["spm_units"] = {"spm_unit": {"members": members}}

    return situation


def create_uk_household_situation(
    num_children: int,
    year: int,
    region: str,
    rent: int,
    childcare_per_child: int,
    brma: Optional[str] = None,
) -> Dict:
    """Create UK household situation."""
    # Use realistic ages for childcare (1, 3, 5)
    child_ages = [1, 3, 5]

    people = {
        "parent": {
            "age": {year: UK_PARENT_AGE},
            "employment_income": {year: 30000}
        }
    }

    all_members = ["parent"]
    for i in range(num_children):
        child_id = f"child_{i+1}"
        child_age = child_ages[i]
        people[child_id] = {"age": {year: child_age}}

        # Apply childcare for children under 5 (full-time nursery costs)
        if child_age < 5:
            people[child_id]["childcare_expenses"] = {year: childcare_per_child}

        all_members.append(child_id)

    household = {
        "members": all_members,
        "region": {year: region},
        "rent": {year: rent}
    }

    if brma:
        household["brma"] = {year: brma}

    situation = {
        "people": people,
        "benunits": {
            "benunit": {
                "members": all_members,
                "would_claim_uc": {year: True}
            }
        },
        "households": {"household": household}
    }

    return situation


def calculate_us_net_income_absolute(
    max_children: int,
    year: int,
    marital_status: str,
    state_code: str,
    spouse_income: float,
    include_health_benefits: bool,
    progress_callback: Optional[Callable] = None,
) -> pd.DataFrame:
    """Calculate absolute net income for US households.

    Args:
        progress_callback: Optional function(current, total, message) for progress updates
    """
    results = []
    income_points = list(range(INCOME_MIN, INCOME_MAX + 1, INCOME_STEP))

    for num_kids in range(max_children + 1):
        if progress_callback:
            progress_callback(num_kids + 1, max_children + 1, f"Calculating for {num_kids} children...")

        situation = create_us_household_situation(num_kids, year, marital_status, state_code, spouse_income)
        situation["axes"] = [[{"name": "employment_income", "count": len(income_points), "min": INCOME_MIN, "max": INCOME_MAX}]]

        sim = USSimulation(situation=situation)
        net_incomes = sim.calculate(
            "household_net_income_including_health_benefits" if include_health_benefits else "household_net_income", year
        )

        for i, income in enumerate(income_points):
            results.append({"income": income, "num_children": num_kids, "net_income": float(net_incomes[i])})

    return pd.DataFrame(results)


def calculate_us_mtr_absolute(
    max_children: int,
    year: int,
    marital_status: str,
    state_code: str,
    spouse_income: float,
    include_health_benefits: bool = True,
    progress_callback: Optional[Callable] = None,
) -> pd.DataFrame:
    """Calculate absolute MTR for US households.

    Args:
        include_health_benefits: If True, calculate MTR from net income including health benefits
    """
    import numpy as np

    results = []
    income_points = list(range(INCOME_MIN, INCOME_MAX + 1, INCOME_STEP))

    if include_health_benefits:
        # Calculate MTR from gradient of net income including health benefits
        for num_kids in range(max_children + 1):
            if progress_callback:
                progress_callback(num_kids + 1, max_children + 1, f"Calculating MTR for {num_kids} children...")

            situation = create_us_household_situation(num_kids, year, marital_status, state_code, spouse_income)
            situation["axes"] = [[{"name": "employment_income", "count": len(income_points), "min": INCOME_MIN, "max": INCOME_MAX}]]

            sim = USSimulation(situation=situation)
            net_incomes = sim.calculate("household_net_income_including_health_benefits", year)

            # Calculate MTR as 1 - d(net_income)/d(income)
            mtr_values = np.zeros(len(income_points))
            for i in range(len(income_points) - 1):
                d_income = income_points[i+1] - income_points[i]
                d_net = net_incomes[i+1] - net_incomes[i]
                mtr_values[i] = 1 - (d_net / d_income)
            # Last point same as second-to-last
            mtr_values[-1] = mtr_values[-2] if len(income_points) > 1 else 0

            for i, income in enumerate(income_points):
                results.append({"income": income, "num_children": num_kids, "mtr": float(mtr_values[i])})
    else:
        # Use built-in marginal_tax_rate (excludes health benefits)
        for num_kids in range(max_children + 1):
            if progress_callback:
                progress_callback(num_kids + 1, max_children + 1, f"Calculating MTR for {num_kids} children...")

            situation = create_us_household_situation(num_kids, year, marital_status, state_code, spouse_income)
            situation["axes"] = [[{"name": "employment_income", "count": len(income_points), "min": INCOME_MIN, "max": INCOME_MAX}]]

            sim = USSimulation(situation=situation)
            mtr_values = sim.calculate("marginal_tax_rate", year)

            for i, income in enumerate(income_points):
                results.append({"income": income, "num_children": num_kids, "mtr": float(mtr_values[i])})

    return pd.DataFrame(results)


def calculate_uk_net_income_absolute(
    max_children: int,
    year: int,
    region: str,
    rent: int,
    childcare_per_child: int,
    brma: Optional[str] = None,
    progress_callback: Optional[Callable] = None,
) -> pd.DataFrame:
    """Calculate absolute net income for UK single parents."""
    results = []

    for num_children in range(max_children + 1):
        if progress_callback:
            progress_callback(num_children + 1, max_children + 1, f"Calculating for {num_children} children...")

        situation = create_uk_household_situation(num_children, year, region, rent, childcare_per_child, brma)
        situation["axes"] = [[{"name": "employment_income", "count": 1001, "min": 0, "max": UK_INCOME_MAX, "period": year}]]

        sim = UKSimulation(situation=situation)
        all_incomes = sim.calculate("employment_income", year)
        all_net_income = sim.calculate("household_net_income", year)

        num_people = 1 + num_children
        incomes = all_incomes if num_people == 1 else all_incomes[::num_people]

        for i, income in enumerate(incomes):
            results.append({"income": float(income), "num_children": num_children, "net_income": float(all_net_income[i])})

    return pd.DataFrame(results)


def calculate_uk_mtr_absolute(
    max_children: int,
    year: int,
    region: str,
    rent: int,
    childcare_per_child: int,
    brma: Optional[str] = None,
    progress_callback: Optional[Callable] = None,
) -> pd.DataFrame:
    """Calculate absolute MTR for UK single parents."""
    results = []

    for num_children in range(max_children + 1):
        if progress_callback:
            progress_callback(num_children + 1, max_children + 1, f"Calculating MTR for {num_children} children...")

        situation = create_uk_household_situation(num_children, year, region, rent, childcare_per_child, brma)
        situation["axes"] = [[{"name": "employment_income", "count": 1001, "min": 0, "max": UK_INCOME_MAX, "period": year}]]

        sim = UKSimulation(situation=situation)
        all_incomes = sim.calculate("employment_income", year)
        all_mtr = sim.calculate("marginal_tax_rate", year)

        num_people = 1 + num_children
        incomes = all_incomes if num_people == 1 else all_incomes[::num_people]
        mtr = all_mtr if num_people == 1 else all_mtr[::num_people]

        for i, income in enumerate(incomes):
            results.append({"income": float(income), "num_children": num_children, "mtr": float(mtr[i])})

    return pd.DataFrame(results)


def derive_marginal_from_absolute(df_absolute: pd.DataFrame, value_column: str, new_column: str) -> pd.DataFrame:
    """Convert absolute values to marginal (change per additional child).

    Args:
        df_absolute: DataFrame with absolute values
        value_column: Column name containing absolute values
        new_column: Column name for marginal values

    Returns:
        DataFrame with marginal values
    """
    marginal_data = []

    for income in df_absolute["income"].unique():
        income_df = df_absolute[df_absolute["income"] == income].sort_values("num_children")
        for i in range(1, len(income_df)):
            current = income_df.iloc[i]
            previous = income_df.iloc[i-1]
            marginal_data.append({
                "income": income,
                "num_children": current["num_children"],
                new_column: current[value_column] - previous[value_column],
            })

    return pd.DataFrame(marginal_data)


def calculate_us_all(
    max_children: int,
    year: int,
    marital_status: str,
    state_code: str,
    spouse_income: float,
    include_health_benefits: bool = True,
) -> pd.DataFrame:
    """Calculate both net_income and mtr in a single pass per child count.

    Returns DataFrame with: income, num_children, net_income, mtr
    """
    import numpy as np

    results = []
    income_points = list(range(INCOME_MIN, INCOME_MAX + 1, INCOME_STEP))

    for num_kids in range(max_children + 1):
        situation = create_us_household_situation(num_kids, year, marital_status, state_code, spouse_income)
        situation["axes"] = [[{"name": "employment_income", "count": len(income_points), "min": INCOME_MIN, "max": INCOME_MAX}]]

        sim = USSimulation(situation=situation)

        # Get net income
        net_income_var = "household_net_income_including_health_benefits" if include_health_benefits else "household_net_income"
        net_incomes = sim.calculate(net_income_var, year)

        # Calculate MTR from gradient of net income (works for both with/without health)
        mtr_values = np.zeros(len(income_points))
        for i in range(len(income_points) - 1):
            d_income = income_points[i+1] - income_points[i]
            d_net = net_incomes[i+1] - net_incomes[i]
            mtr_values[i] = 1 - (d_net / d_income)
        mtr_values[-1] = mtr_values[-2] if len(income_points) > 1 else 0

        for i, income in enumerate(income_points):
            results.append({
                "income": income,
                "num_children": num_kids,
                "net_income": float(net_incomes[i]),
                "mtr": float(mtr_values[i]),
            })

    return pd.DataFrame(results)


def calculate_uk_all(
    max_children: int,
    year: int,
    region: str,
    rent: int,
    childcare_per_child: int,
    brma: Optional[str] = None,
) -> pd.DataFrame:
    """Calculate both net_income and mtr in a single pass per child count.

    Returns DataFrame with: income, num_children, net_income, mtr
    """
    results = []

    for num_children in range(max_children + 1):
        situation = create_uk_household_situation(num_children, year, region, rent, childcare_per_child, brma)
        situation["axes"] = [[{"name": "employment_income", "count": 1001, "min": 0, "max": UK_INCOME_MAX, "period": year}]]

        sim = UKSimulation(situation=situation)
        all_incomes = sim.calculate("employment_income", year)
        all_net_income = sim.calculate("household_net_income", year)
        all_mtr = sim.calculate("marginal_tax_rate", year)

        num_people = 1 + num_children
        incomes = all_incomes if num_people == 1 else all_incomes[::num_people]

        for i, income in enumerate(incomes):
            results.append({
                "income": float(income),
                "num_children": num_children,
                "net_income": float(all_net_income[i]),
                "mtr": float(all_mtr[i]),
            })

    return pd.DataFrame(results)
