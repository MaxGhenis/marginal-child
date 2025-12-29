"""Calculation logic for the Marginal Child application."""

import logging
from typing import Dict

import pandas as pd
import streamlit as st
from policyengine_us import Simulation as USSimulation
from policyengine_uk import Simulation as UKSimulation

from marginal_child.constants import (
    DEFAULT_ADULT_AGE,
    DEFAULT_CHILD_AGE,
    INCOME_MAX,
    INCOME_MIN,
    INCOME_STEP,
    MAX_CHILDREN,
    UK_CHILD_AGES,
    UK_DEFAULT_CHILDCARE_PER_CHILD,
    UK_DEFAULT_RENT,
    UK_INCOME_MAX,
    UK_PARENT_AGE,
    US_STATES,
)

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def validate_inputs(
    year: int,
    marital_status: str,
    state_code: str,
    spouse_income: float,
    include_health_benefits: bool,
) -> None:
    """Validate input parameters.

    Args:
        year: Tax year for calculations (2021-2035)
        marital_status: Either 'single' or 'married'
        state_code: Two-letter US state code
        spouse_income: Annual income of spouse
        include_health_benefits: Whether to include health insurance value

    Raises:
        ValueError: If any input is invalid
    """
    if year < 2021 or year > 2035:
        raise ValueError(f"Year must be between 2021 and 2035: {year}")
    if marital_status not in ["single", "married"]:
        raise ValueError(f"Invalid marital status: {marital_status}")

    valid_states = [code for code, _ in US_STATES]
    if state_code not in valid_states:
        raise ValueError(f"Invalid state code: {state_code}")

    if spouse_income < 0:
        raise ValueError(f"Spouse income cannot be negative: {spouse_income}")

    if spouse_income > 0 and marital_status == "single":
        logger.warning(
            "Spouse income provided for single household, will be ignored"
        )

    if not isinstance(include_health_benefits, bool):
        raise ValueError(
            "include_health_benefits must be boolean: "
            f"{include_health_benefits}"
        )


def create_household_situation(
    num_children: int,
    year: int,
    marital_status: str,
    state_code: str,
    spouse_income: float,
) -> Dict:
    """Create a household situation dictionary for PolicyEngine.

    Args:
        num_children: Number of children in the household
        year: Tax year for calculations
        marital_status: Either 'single' or 'married'
        state_code: Two-letter US state code
        spouse_income: Income of spouse (0 if single)

    Returns:
        Dictionary representing the household situation

    Raises:
        ValueError: If num_children is negative or exceeds MAX_CHILDREN
    """
    if num_children < 0:
        raise ValueError(
            f"Number of children cannot be negative: {num_children}"
        )

    if num_children > MAX_CHILDREN:
        raise ValueError(
            f"Number of children cannot exceed {MAX_CHILDREN}: {num_children}"
        )
    situation = {
        "people": {
            "adult": {
                "age": {year: DEFAULT_ADULT_AGE},
            }
        }
    }

    # Add spouse if married
    if marital_status == "married":
        situation["people"]["spouse"] = {
            "age": {year: DEFAULT_ADULT_AGE},
            "employment_income": {year: spouse_income},
        }

    # Add children (all age 10)
    for i in range(num_children):
        situation["people"][f"child_{i+1}"] = {
            "age": {year: DEFAULT_CHILD_AGE}
        }

    # Create family and household structure
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


@st.cache_data(show_spinner=False)
def calculate_marginal_child_benefits(max_children: int, 
    year: int,
    marital_status: str,
    state_code: str,
    spouse_income: float,
    include_health_benefits: bool,
) -> pd.DataFrame:
    """Calculate marginal benefits for children 1-4 across income range.

    This function uses PolicyEngine-US with axes to efficiently
    calculate net income across multiple income levels for
    households with 0-4 children.

    Args:
        year: Tax year for calculations (2021-2035)
        marital_status: Either 'single' or 'married'
        state_code: Two-letter US state code
        spouse_income: Annual income of spouse (0 if single)
        include_health_benefits: Whether to include health insurance value

    Returns:
        DataFrame with columns: income, num_children,
        marginal_benefit, net_income

    Raises:
        ValueError: If inputs are invalid
        Exception: If PolicyEngine calculation fails
    """
    # Validate inputs
    try:
        validate_inputs(
            year,
            marital_status,
            state_code,
            spouse_income,
            include_health_benefits,
        )
    except ValueError as e:
        logger.error(f"Input validation failed: {e}")
        raise
    results = []

    # Progress bar for calculation
    progress_bar = st.progress(0)
    status_text = st.empty()

    income_points = list(range(INCOME_MIN, INCOME_MAX + 1, INCOME_STEP))

    # Store net incomes for each number of children
    all_net_incomes = {}

    # Calculate for each number of children using axes for income
    for num_kids in range(max_children + 1):
        # Update progress
        progress = (num_kids + 1) / (max_children + 1)
        progress_bar.progress(progress)
        status_text.text(
            f"Calculating with {num_kids} children across all income levels..."
        )

        # Create base situation
        situation = create_household_situation(
            num_kids, year, marital_status, state_code, spouse_income
        )

        # Add axes for employment income variation
        situation["axes"] = [
            [
                {
                    "name": "employment_income",
                    "count": len(income_points),
                    "min": INCOME_MIN,
                    "max": INCOME_MAX,
                }
            ]
        ]

        # Run simulation with the situation containing axes
        try:
            sim = USSimulation(situation=situation)
        except Exception as e:
            logger.error(f"Failed to create simulation: {e}")
            status_text.error(f"Calculation error: {str(e)}")
            progress_bar.empty()
            raise

        # Get net income - either with or without health benefits value
        try:
            if include_health_benefits:
                # Calculate net income including health benefits value
                # This includes Medicaid, CHIP, and ACA premium tax credits
                net_incomes = sim.calculate(
                    "household_net_income_including_health_benefits", year
                )
            else:
                # Use regular net income (cash benefits only)
                net_incomes = sim.calculate("household_net_income", year)

        except Exception as e:
            logger.error(f"Failed to calculate net income: {e}")
            status_text.error(f"Calculation error: {str(e)}")
            progress_bar.empty()
            raise

        # Store results
        all_net_incomes[num_kids] = net_incomes

    # Calculate marginal benefits (difference between N and N-1 children)
    for num_kids in range(1, MAX_CHILDREN + 1):
        current_net_incomes = all_net_incomes[num_kids]
        previous_net_incomes = all_net_incomes[
            num_kids - 1
        ]  # Compare with N-1 children

        for i, income in enumerate(income_points):
            marginal_benefit = float(
                current_net_incomes[i] - previous_net_incomes[i]
            )

            results.append(
                {
                    "income": income,
                    "num_children": num_kids,
                    "marginal_benefit": marginal_benefit,
                    "net_income": float(current_net_incomes[i]),
                }
            )

    # Clear progress indicators
    progress_bar.empty()
    status_text.empty()

    return pd.DataFrame(results)


def get_child_ordinal(num: int) -> str:
    """Get ordinal string for a child number.

    Args:
        num: Child number (1-4)

    Returns:
        Ordinal string (1st, 2nd, 3rd, 4th)
    """
    ordinals = {1: "1st", 2: "2nd", 3: "3rd", 4: "4th"}
    return ordinals.get(num, f"{num}th")


# UK-specific functions

def create_uk_household_situation(
    num_children: int,
    year: int,
    region: str,
    rent: int = UK_DEFAULT_RENT,
    childcare_per_child: int = UK_DEFAULT_CHILDCARE_PER_CHILD,
) -> Dict:
    """Create a UK household situation dictionary.

    Args:
        num_children: Number of children (0-3)
        year: Tax year
        region: UK region code (e.g., "LONDON")
        rent: Annual rent in pounds
        childcare_per_child: Annual childcare expenses per child

    Returns:
        Dictionary representing the household situation
    """
    people = {
        "parent": {
            "age": {year: UK_PARENT_AGE},
            "employment_income": {year: 30000}  # Will be varied by axes
        }
    }

    all_members = ["parent"]
    for i in range(num_children):
        child_id = f"child_{i+1}"
        child_age = UK_CHILD_AGES[i]
        people[child_id] = {"age": {year: child_age}}

        # Add childcare expenses for children under 12
        if child_age < 12:
            people[child_id]["childcare_expenses"] = {year: childcare_per_child}

        all_members.append(child_id)

    situation = {
        "people": people,
        "benunits": {
            "benunit": {
                "members": all_members,
                "would_claim_uc": {year: True}  # Enable UC claiming
            }
        },
        "households": {
            "household": {
                "members": all_members,
                "region": {year: region},
                "rent": {year: rent}
            }
        }
    }

    return situation


@st.cache_data(show_spinner=False)
def calculate_uk_marginal_tax_rates(max_children: int, 
    year: int,
    region: str,
    rent: int = UK_DEFAULT_RENT,
    childcare_per_child: int = UK_DEFAULT_CHILDCARE_PER_CHILD,
) -> pd.DataFrame:
    """Calculate UK marginal tax rates for single parents with 0-3 children.

    Args:
        year: Tax year for calculations
        region: UK region code
        rent: Annual rent in pounds
        childcare_per_child: Annual childcare expenses per child

    Returns:
        DataFrame with columns: income, num_children, mtr
    """
    results = []

    # Progress bar
    progress_bar = st.progress(0)
    status_text = st.empty()

    # Calculate for each number of children (0-3)
    for num_children in range(max_children + 1):
        progress = (num_children + 1) / 4
        progress_bar.progress(progress)
        status_text.text(
            f"Calculating MTR for {num_children} {'child' if num_children == 1 else 'children'}..."
        )

        # Create situation with axes
        situation = create_uk_household_situation(
            num_children, year, region, rent, childcare_per_child
        )

        # Add axes for income variation
        situation["axes"] = [
            [
                {
                    "name": "employment_income",
                    "count": 1001,
                    "min": 0,
                    "max": UK_INCOME_MAX,
                    "period": year,
                }
            ]
        ]

        # Run simulation
        try:
            sim = UKSimulation(situation=situation)
        except Exception as e:
            logger.error(f"Failed to create UK simulation: {e}")
            progress_bar.empty()
            status_text.empty()
            raise

        # Calculate MTR
        try:
            all_incomes = sim.calculate("employment_income", year)
            all_mtr = sim.calculate("marginal_tax_rate", year)

            # Handle interleaved person-level data
            num_people = 1 + num_children
            if num_people == 1:
                incomes = all_incomes
                mtr = all_mtr
            else:
                incomes = all_incomes[::num_people]
                mtr = all_mtr[::num_people]

            # Store results
            for i, income in enumerate(incomes):
                results.append(
                    {
                        "income": float(income),
                        "num_children": num_children,
                        "mtr": float(mtr[i]),
                    }
                )

        except Exception as e:
            logger.error(f"Failed to calculate UK MTR: {e}")
            progress_bar.empty()
            status_text.empty()
            raise

    # Clear progress indicators
    progress_bar.empty()
    status_text.empty()

    return pd.DataFrame(results)


# Additional calculation functions for all 4 visualization modes

@st.cache_data(show_spinner=False)
def calculate_us_marginal_tax_rates(max_children: int, 
    year: int,
    marital_status: str,
    state_code: str,
    spouse_income: float,
) -> pd.DataFrame:
    """Calculate US marginal tax rates for households with 0-4 children."""
    results = []
    progress_bar = st.progress(0)
    status_text = st.empty()
    income_points = list(range(INCOME_MIN, INCOME_MAX + 1, INCOME_STEP))

    for num_kids in range(max_children + 1):
        progress_bar.progress((num_kids + 1) / (max_children + 1))
        status_text.text(f"Calculating MTR for {num_kids} children...")

        situation = create_household_situation(num_kids, year, marital_status, state_code, spouse_income)
        situation["axes"] = [[{"name": "employment_income", "count": len(income_points), "min": INCOME_MIN, "max": INCOME_MAX}]]

        try:
            sim = USSimulation(situation=situation)
            mtr_values = sim.calculate("marginal_tax_rate", year)

            for i, income in enumerate(income_points):
                results.append({"income": income, "num_children": num_kids, "mtr": float(mtr_values[i])})
        except Exception as e:
            logger.error(f"Failed to calculate US MTR: {e}")
            progress_bar.empty()
            status_text.empty()
            raise

    progress_bar.empty()
    status_text.empty()
    return pd.DataFrame(results)


@st.cache_data(show_spinner=False)
def calculate_absolute_net_income(max_children: int, 
    year: int, marital_status: str, state_code: str, spouse_income: float, include_health_benefits: bool
) -> pd.DataFrame:
    """Calculate absolute net income for US households with 0-4 children."""
    results = []
    progress_bar = st.progress(0)
    status_text = st.empty()
    income_points = list(range(INCOME_MIN, INCOME_MAX + 1, INCOME_STEP))

    for num_kids in range(max_children + 1):
        progress_bar.progress((num_kids + 1) / (max_children + 1))
        status_text.text(f"Calculating net income for {num_kids} children...")

        situation = create_household_situation(num_kids, year, marital_status, state_code, spouse_income)
        situation["axes"] = [[{"name": "employment_income", "count": len(income_points), "min": INCOME_MIN, "max": INCOME_MAX}]]

        try:
            sim = USSimulation(situation=situation)
            net_incomes = sim.calculate(
                "household_net_income_including_health_benefits" if include_health_benefits else "household_net_income", year
            )

            for i, income in enumerate(income_points):
                results.append({"income": income, "num_children": num_kids, "net_income": float(net_incomes[i])})
        except Exception as e:
            logger.error(f"Failed to calculate absolute net income: {e}")
            progress_bar.empty()
            status_text.empty()
            raise

    progress_bar.empty()
    status_text.empty()
    return pd.DataFrame(results)


@st.cache_data(show_spinner=False)
def calculate_uk_absolute_net_income(max_children: int, 
    year: int, region: str, rent: int, childcare_per_child: int
) -> pd.DataFrame:
    """Calculate absolute net income for UK single parents with 0-3 children."""
    results = []
    progress_bar = st.progress(0)
    status_text = st.empty()

    for num_children in range(max_children + 1):
        progress_bar.progress((num_children + 1) / 4)
        status_text.text(f"Calculating net income for {num_children} {'child' if num_children == 1 else 'children'}...")

        situation = create_uk_household_situation(num_children, year, region, rent, childcare_per_child)
        situation["axes"] = [[{"name": "employment_income", "count": 1001, "min": 0, "max": UK_INCOME_MAX, "period": year}]]

        try:
            sim = UKSimulation(situation=situation)
            all_incomes = sim.calculate("employment_income", year)
            all_net_income = sim.calculate("household_net_income", year)

            num_people = 1 + num_children
            incomes = all_incomes if num_people == 1 else all_incomes[::num_people]
            # For household_net_income, it should be household-level already
            net_incomes = all_net_income

            for i, income in enumerate(incomes):
                results.append({"income": float(income), "num_children": num_children, "net_income": float(net_incomes[i])})
        except Exception as e:
            logger.error(f"Failed to calculate UK absolute net income: {e}")
            progress_bar.empty()
            status_text.empty()
            raise

    progress_bar.empty()
    status_text.empty()
    return pd.DataFrame(results)
