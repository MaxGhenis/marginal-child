import modal

app = modal.App("marginal-child")

image = modal.Image.debian_slim(python_version="3.12").pip_install(
    "fastapi",
    "policyengine-us",
)

STATES = [
    "AL", "AK", "AZ", "AR", "CA", "CO", "CT", "DE", "DC", "FL",
    "GA", "HI", "ID", "IL", "IN", "IA", "KS", "KY", "LA", "ME",
    "MD", "MA", "MI", "MN", "MS", "MO", "MT", "NE", "NV", "NH",
    "NJ", "NM", "NY", "NC", "ND", "OH", "OK", "OR", "PA", "RI",
    "SC", "SD", "TN", "TX", "UT", "VT", "VA", "WA", "WV", "WI", "WY",
]


def create_situation(params: dict) -> dict:
    year = 2024
    people = {
        "parent1": {
            "age": {year: params.get("parent1_age", 30)},
            "employment_income": {year: params.get("employment_income", 0)},
        }
    }

    families = {"family": {"members": ["parent1"]}}
    marital_units = {"marital_unit": {"members": ["parent1"]}}
    tax_units = {"tax_unit": {"members": ["parent1"]}}
    spm_units = {"spm_unit": {"members": ["parent1"]}}
    households = {
        "household": {
            "members": ["parent1"],
            "state_name": {year: params.get("state", "TX")},
        }
    }

    if params.get("marital_status") == "married":
        people["parent2"] = {
            "age": {year: params.get("parent2_age", 30)},
            "employment_income": {year: params.get("spouse_income", 0)},
        }
        for unit in [families, marital_units, tax_units, spm_units, households]:
            list(unit.values())[0]["members"].append("parent2")

    num_children = params.get("num_children", 0)
    for i in range(num_children):
        child_key = f"child{i + 1}"
        child_age = params.get(f"child{i + 1}_age", 5)
        people[child_key] = {"age": {year: child_age}}
        families["family"]["members"].append(child_key)
        tax_units["tax_unit"]["members"].append(child_key)
        spm_units["spm_unit"]["members"].append(child_key)
        households["household"]["members"].append(child_key)
        marital_units[f"{child_key}_marital_unit"] = {
            "members": [child_key],
            "marital_unit_id": {year: i + 2},
        }

    return {
        "people": people,
        "families": families,
        "marital_units": marital_units,
        "tax_units": tax_units,
        "spm_units": spm_units,
        "households": households,
    }


@app.function(image=image, timeout=120)
@modal.fastapi_endpoint(method="GET")
def states() -> list[str]:
    return STATES


@app.function(image=image, timeout=300)
@modal.fastapi_endpoint(method="POST")
def marginal_child(data: dict) -> list[dict]:
    from policyengine_us import Simulation

    max_children = data.get("max_children", 5)
    income_min = data.get("income_min", 0)
    income_max = data.get("income_max", 200000)
    income_step = data.get("income_step", 5000)
    year = 2024

    results = []

    for income in range(income_min, income_max + 1, income_step):
        prev_net_income = None

        for num_children in range(max_children + 1):
            params = {**data, "employment_income": income, "num_children": num_children}
            situation = create_situation(params)
            sim = Simulation(situation=situation)
            net_income = float(sim.calculate("household_net_income", year))

            if prev_net_income is not None and num_children > 0:
                results.append({
                    "income": income,
                    "num_children": num_children,
                    "marginal_benefit": net_income - prev_net_income,
                    "net_income": net_income,
                })

            prev_net_income = net_income

    return results


@app.function(image=image, timeout=120)
@modal.fastapi_endpoint(method="POST")
def calculate(data: dict) -> dict:
    from policyengine_us import Simulation

    situation = create_situation(data)
    sim = Simulation(situation=situation)
    year = 2024

    snap = float(sim.calculate("snap", year))
    wic = float(sim.calculate("wic", year))
    medicaid = float(sim.calculate("medicaid", year))
    chip = float(sim.calculate("chip", year))
    premium_tax_credit = float(sim.calculate("premium_tax_credit", year))
    eitc = float(sim.calculate("eitc", year))
    ctc = float(sim.calculate("ctc", year))
    cdcc = float(sim.calculate("cdcc", year))
    housing_subsidy = float(sim.calculate("housing_subsidy", year))
    net_income = float(sim.calculate("household_net_income", year))
    market_income = float(sim.calculate("household_market_income", year))

    return {
        "snap": snap,
        "wic": wic,
        "medicaid": medicaid,
        "chip": chip,
        "premium_tax_credit": premium_tax_credit,
        "eitc": eitc,
        "ctc": ctc,
        "cdcc": cdcc,
        "housing_subsidy": housing_subsidy,
        "total_benefits": snap + wic + medicaid + chip + premium_tax_credit + eitc + ctc + cdcc + housing_subsidy,
        "net_income": net_income,
        "market_income": market_income,
    }
