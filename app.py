"""The Marginal Child - PolicyEngine Tax and Benefit Calculator.

Entry point for the Streamlit application.
"""

import streamlit as st

from marginal_child.core import (
    calculate_absolute_net_income,
    calculate_marginal_child_benefits,
    calculate_uk_absolute_net_income,
    calculate_uk_marginal_tax_rates,
    calculate_us_marginal_tax_rates,
    get_child_ordinal,
)
from marginal_child.streamlit_ui import (
    create_absolute_mtr_plot,
    create_absolute_net_income_plot,
    create_benefits_plot,
    create_marginal_mtr_plot,
    create_mtr_plot,
    render_header,
    render_sidebar,
    render_summary_statistics,
)
from marginal_child.constants import UK_REGIONS

# Page configuration
st.set_page_config(
    page_title="The Marginal Child", page_icon="👶", layout="wide"
)


def main():
    """Main application entry point."""
    render_header()

    config = render_sidebar()

    country = config["country"]
    max_children = config["max_children"]
    metric = config["metric"]
    view = config["view"]
    year = config["year"]
    calculate_button = config["calculate_button"]

    # Create cache key
    cache_key = f"{country}_{max_children}_{metric}_{view}"

    # Calculate if button pressed or not cached
    if calculate_button or cache_key not in st.session_state:
        try:
            with st.spinner("Calculating..."):
                # US calculations
                if country == "US":
                    if metric == "Net Income":
                        if view == "Absolute":
                            df = calculate_absolute_net_income(
                                max_children,
                                year,
                                config["marital_status"],
                                config["state_code"],
                                config["spouse_income"],
                                config["include_health_benefits"],
                            )
                        else:  # Marginal
                            df = calculate_marginal_child_benefits(
                                max_children,
                                year,
                                config["marital_status"],
                                config["state_code"],
                                config["spouse_income"],
                                config["include_health_benefits"],
                            )
                    else:  # MTR
                        df = calculate_us_marginal_tax_rates(
                            max_children,
                            year,
                            config["marital_status"],
                            config["state_code"],
                            config["spouse_income"],
                        )

                # UK calculations
                else:  # UK
                    if metric == "Net Income":
                        if view == "Absolute":
                            df = calculate_uk_absolute_net_income(
                                max_children,
                                year,
                                config["region"],
                                config["rent"],
                                config["childcare_per_child"],
                            )
                        else:  # Marginal
                            # Calculate absolute first, then derive marginal
                            df_abs = calculate_uk_absolute_net_income(
                                max_children,
                                year,
                                config["region"],
                                config["rent"],
                                config["childcare_per_child"],
                            )
                            # Convert to marginal
                            marginal_data = []
                            for income in df_abs["income"].unique():
                                income_df = df_abs[df_abs["income"] == income].sort_values("num_children")
                                for i in range(1, len(income_df)):
                                    current = income_df.iloc[i]
                                    previous = income_df.iloc[i-1]
                                    marginal_data.append({
                                        "income": income,
                                        "num_children": current["num_children"],
                                        "marginal_benefit": current["net_income"] - previous["net_income"],
                                        "net_income": current["net_income"]
                                    })
                            df = pd.DataFrame(marginal_data)
                    else:  # MTR
                        df = calculate_uk_marginal_tax_rates(
                            max_children,
                            year,
                            config["region"],
                            config["rent"],
                            config["childcare_per_child"],
                        )

                st.session_state[cache_key] = df

        except ValueError as e:
            st.error(f"Invalid input: {str(e)}")
            st.stop()
        except Exception as e:
            st.error(f"Calculation error: {str(e)}")
            st.stop()
    else:
        df = st.session_state[cache_key]

    # Display appropriate plot
    if metric == "Net Income":
        if view == "Absolute":
            fig = create_absolute_net_income_plot(df, country)
        else:  # Marginal
            fig = create_benefits_plot(df)
    else:  # MTR
        if view == "Absolute":
            if country == "UK":
                region_name = next(name for code, name in UK_REGIONS if code == config["region"])
                fig = create_mtr_plot(df, country, region_name)
            else:
                fig = create_absolute_mtr_plot(df, country)
        else:  # Marginal MTR
            fig = create_marginal_mtr_plot(df, country)

    st.plotly_chart(fig, use_container_width=True)

    # Display statistics
    if metric == "Net Income" and view == "Marginal (per additional child)":
        render_summary_statistics(df)
    elif metric == "Marginal Tax Rate":
        st.header("MTR Statistics")
        cols = st.columns(min(4, len(df["num_children"].unique())))

        for i, num_children in enumerate(sorted(df["num_children"].unique())):
            if i < len(cols):
                with cols[i]:
                    child_data = df[df["num_children"] == num_children]
                    avg_mtr = child_data["mtr"].mean()
                    max_mtr = child_data["mtr"].max()
                    label = f"{num_children} {'child' if num_children == 1 else 'children'}" if view == "Absolute" else get_child_ordinal(num_children)
                    st.metric(label, f"{avg_mtr:.1%} avg", f"{max_mtr:.1%} max")


if __name__ == "__main__":
    import pandas as pd
    main()
