"""UI components for the Marginal Child application."""

import pandas as pd
import plotly.graph_objects as go
import streamlit as st

from marginal_child.core import get_child_ordinal
from marginal_child.constants import (
    COLORS,
    DEFAULT_REGION_INDEX,
    DEFAULT_STATE_INDEX,
    FONT_FAMILY,
    LOGO_URL,
    UK_REGIONS,
    US_STATES,
)


def render_header():
    """Render the application header with branding."""
    st.markdown(
        f"""
        <style>
        @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&display=swap');
        .stApp {{
            font-family: {FONT_FAMILY};
        }}
        h1 {{
            color: {COLORS['primary']};
            font-weight: 600;
        }}
        .subtitle {{
            color: #666;
            font-size: 1.1rem;
            margin-bottom: 2rem;
        }}
        </style>
    """,
        unsafe_allow_html=True,
    )

    col1, col2 = st.columns([3, 1])
    with col1:
        st.title("The Marginal Child")
        st.markdown(
            '<p class="subtitle">Analyze marginal tax rates and benefits by number of children</p>',
            unsafe_allow_html=True,
        )
    with col2:
        st.markdown(
            '<div style="text-align: right; padding-top: 1rem;">'
            "Powered by PolicyEngine</div>",
            unsafe_allow_html=True,
        )


def render_sidebar() -> dict:
    """Render the sidebar configuration panel.

    Returns:
        Dictionary with all configuration parameters
    """
    with st.sidebar:
        st.header("Configuration")

        # Country selector
        country = st.selectbox(
            "Country",
            options=["US", "UK"],
            index=0,
            key="country",
        )

        # Max children selector
        max_children = st.number_input(
            "Maximum Number of Children",
            min_value=1,
            max_value=6,
            value=3,
            step=1,
            key="max_children",
            help="Number of children to include in analysis (0 to this number)",
        )

        st.markdown("---")

        # Metric selector
        metric = st.radio(
            "Metric",
            options=["Net Income", "Marginal Tax Rate"],
            key="metric",
        )

        # View selector
        view = st.radio(
            "View",
            options=["Absolute", "Marginal (per additional child)"],
            key="view",
        )

        st.markdown("---")

        year = st.selectbox(
            "Year", options=list(range(2021, 2036)), index=4, key="year"
        )

        # US-specific inputs
        if country == "US":
            marital_status = st.selectbox(
                "Marital Status",
                options=["single", "married"],
                format_func=lambda x: x.title(),
                key="marital_status",
            )

            state_code = st.selectbox(
                "State",
                options=[code for code, _ in US_STATES],
                format_func=lambda x: next(
                    name for code, name in US_STATES if code == x
                ),
                index=DEFAULT_STATE_INDEX,
                key="state",
            )

            spouse_income = 0
            if marital_status == "married":
                spouse_income = st.number_input(
                    "Spouse Income ($)",
                    min_value=0,
                    max_value=500000,
                    value=0,
                    step=1000,
                    key="spouse_income",
                    help="Annual employment income of spouse",
                )

            st.markdown("---")

            include_health_benefits = st.checkbox(
                "Include health insurance value",
                value=True,
                help="Includes Medicaid, CHIP, and ACA subsidies",
            )

            st.markdown("**Note:** All children assumed age 10")

        # UK-specific inputs
        else:  # UK
            region = st.selectbox(
                "Region",
                options=[code for code, _ in UK_REGIONS],
                format_func=lambda x: next(
                    name for code, name in UK_REGIONS if code == x
                ),
                index=DEFAULT_REGION_INDEX,
                key="region",
            )

            st.markdown("---")

            rent = st.number_input(
                "Monthly Rent (£)",
                min_value=0,
                max_value=5000,
                value=1000,
                step=100,
                key="rent",
                help="Monthly rent payment",
            )

            childcare = st.number_input(
                "Monthly Childcare per Child (£)",
                min_value=0,
                max_value=2000,
                value=667,
                step=50,
                key="childcare",
                help="Childcare costs per child under 12",
            )

            st.markdown(
                "**Note:** Parent age 35, children ages 4/7/10. "
                "BRMA not specified (uses regional default)."
            )

        calculate_button = st.button(
            "Calculate",
            type="primary",
            use_container_width=True,
        )

    # Return config dict
    config = {
        "country": country,
        "max_children": int(max_children),
        "metric": metric,
        "view": view,
        "year": year,
        "calculate_button": calculate_button,
    }

    if country == "US":
        config.update({
            "marital_status": marital_status,
            "state_code": state_code,
            "spouse_income": spouse_income,
            "include_health_benefits": include_health_benefits,
        })
    else:  # UK
        config.update({
            "region": region,
            "rent": rent * 12,  # Convert to annual
            "childcare_per_child": childcare * 12,  # Convert to annual
        })

    return config


def create_benefits_plot(df: pd.DataFrame) -> go.Figure:
    """Create the marginal benefits plot.

    Args:
        df: DataFrame with calculation results

    Returns:
        Plotly figure object
    """
    fig = go.Figure()

    # Add traces for each child
    for i, child_num in enumerate(sorted(df["num_children"].unique())):
        child_data = df[df["num_children"] == child_num]
        fig.add_trace(
            go.Scatter(
                x=child_data["income"],
                y=child_data["marginal_benefit"],
                mode="lines",
                name=f"{get_child_ordinal(child_num)} child",
                line=dict(
                    color=COLORS["gradient"][i % len(COLORS["gradient"])],
                    width=3,
                ),
                hovertemplate="Income: $%{x:,.0f}<br>"
                "Marginal Benefit: $%{y:,.0f}<extra></extra>",
            )
        )

    # Update layout
    fig.update_layout(
        title={
            "text": "Net Income Change from Taxes and Benefits "
            "per Additional Child",
            "font": {"size": 20, "color": COLORS["primary"]},
        },
        xaxis=dict(
            title="Earnings",
            tickformat="$,.0f",
            gridcolor="rgba(0,0,0,0.1)",
        ),
        yaxis=dict(
            title="Net Income Change for Additional Child",
            tickformat="$,.0f",
            rangemode="tozero",
            gridcolor="rgba(0,0,0,0.1)",
        ),
        hovermode="x unified",
        plot_bgcolor="white",
        paper_bgcolor="white",
        font=dict(family=FONT_FAMILY),
        legend=dict(
            title="Child Number",
            orientation="v",
            yanchor="top",
            y=1,
            xanchor="left",
            x=1.02,
        ),
        height=600,
    )

    return fig


def create_mtr_plot(df: pd.DataFrame, country: str, region_name: str = "") -> go.Figure:
    """Create the marginal tax rate plot for UK.

    Args:
        df: DataFrame with MTR results
        country: Country code
        region_name: Region name for subtitle

    Returns:
        Plotly figure object
    """
    import plotly.express as px

    fig = go.Figure()

    # Create gray-to-teal gradient
    colors = px.colors.sample_colorscale(
        [[0, COLORS['gray_400']], [1, COLORS['teal_300']]],
        [i/3 for i in range(4)]
    )

    # Add traces for each number of children
    for i, num_children in enumerate(sorted(df["num_children"].unique())):
        child_data = df[df["num_children"] == num_children]
        fig.add_trace(
            go.Scatter(
                x=child_data["income"],
                y=child_data["mtr"],
                mode="lines",
                name=f'{num_children} {"child" if num_children == 1 else "children"}',
                line=dict(color=colors[i], width=2.5),
                hovertemplate="Income: £%{x:,.0f}<br>MTR: %{y:.1%}<extra></extra>",
            )
        )

    # Add 0% reference line
    fig.add_hline(y=0, line_dash="dash", line_color="gray", opacity=0.5)

    # Update layout
    subtitle = f"{region_name}, " if region_name else ""
    subtitle += "parent age 35, children ages 4/7/10, £1k/mo rent, £667/mo childcare/child"

    fig.update_layout(
        title={
            "text": f"Marginal Tax Rate Schedule<br><sub>{subtitle}</sub>",
            "font": {"size": 20, "color": COLORS["primary"]},
        },
        xaxis=dict(
            title="Employment Income (£)",
            tickformat=",.0f",
            tickprefix="£",
            gridcolor="rgba(200, 200, 200, 0.3)",
            showgrid=True,
        ),
        yaxis=dict(
            title="Marginal Tax Rate",
            tickformat=".0%",
            range=[0, 1],
            gridcolor="rgba(200, 200, 200, 0.3)",
            showgrid=True,
        ),
        hovermode="x unified",
        plot_bgcolor="white",
        paper_bgcolor="white",
        font=dict(family=FONT_FAMILY),
        legend=dict(
            x=0.98,
            y=0.02,
            xanchor="right",
            yanchor="bottom",
            bgcolor="rgba(255, 255, 255, 0.8)",
            bordercolor="rgba(0, 0, 0, 0.2)",
            borderwidth=1,
        ),
        height=600,
    )

    return fig


def render_summary_statistics(df: pd.DataFrame):
    """Render summary statistics cards.

    Args:
        df: DataFrame with calculation results
    """
    st.header("Summary Statistics")

    col1, col2, col3, col4 = st.columns(4)

    with col1:
        avg_benefit_1st = df[df["num_children"] == 1][
            "marginal_benefit"
        ].mean()
        st.metric("Average - 1st Child", f"${avg_benefit_1st:,.0f}")

    with col2:
        avg_benefit_2nd = df[df["num_children"] == 2][
            "marginal_benefit"
        ].mean()
        st.metric("Average - 2nd Child", f"${avg_benefit_2nd:,.0f}")

    with col3:
        avg_benefit_3rd = df[df["num_children"] == 3][
            "marginal_benefit"
        ].mean()
        st.metric("Average - 3rd Child", f"${avg_benefit_3rd:,.0f}")

    with col4:
        avg_benefit_4th = df[df["num_children"] == 4][
            "marginal_benefit"
        ].mean()
        st.metric("Average - 4th Child", f"${avg_benefit_4th:,.0f}")


def create_absolute_net_income_plot(df: pd.DataFrame, country: str) -> go.Figure:
    """Create absolute net income plot (lines for 0-N children)."""
    import plotly.express as px

    fig = go.Figure()
    colors = px.colors.sample_colorscale(
        [[0, COLORS['gray_400']], [1, COLORS['teal_300']]],
        [i/4 for i in range(5)]
    )

    for i, num_children in enumerate(sorted(df["num_children"].unique())):
        child_data = df[df["num_children"] == num_children]
        currency = "£" if country == "UK" else "$"
        
        fig.add_trace(go.Scatter(
            x=child_data["income"],
            y=child_data["net_income"],
            mode="lines",
            name=f'{num_children} {"child" if num_children == 1 else "children"}',
            line=dict(color=colors[i], width=2.5),
            hovertemplate=f"Income: {currency}%{{x:,.0f}}<br>Net Income: {currency}%{{y:,.0f}}<extra></extra>",
        ))

    fig.update_layout(
        title=dict(text="Net Income by Number of Children", font=dict(size=20, color=COLORS["primary"])),
        xaxis=dict(title=f"Employment Income ({currency})", tickformat=",.0f", tickprefix=currency,
                   gridcolor="rgba(200,200,200,0.3)", showgrid=True),
        yaxis=dict(title=f"Household Net Income ({currency})", tickformat=",.0f", tickprefix=currency,
                   gridcolor="rgba(200,200,200,0.3)", showgrid=True),
        hovermode="x unified",
        plot_bgcolor="white",
        paper_bgcolor="white",
        font=dict(family=FONT_FAMILY),
        legend=dict(x=0.02, y=0.98, xanchor="left", yanchor="top",
                    bgcolor="rgba(255,255,255,0.8)", bordercolor="rgba(0,0,0,0.2)", borderwidth=1),
        height=600,
    )

    return fig


def create_absolute_mtr_plot(df: pd.DataFrame, country: str) -> go.Figure:
    """Create absolute MTR plot (lines for 0-N children)."""
    import plotly.express as px

    fig = go.Figure()
    num_lines = len(df["num_children"].unique())
    colors = px.colors.sample_colorscale(
        [[0, COLORS['gray_400']], [1, COLORS['teal_300']]],
        [i/(num_lines-1) for i in range(num_lines)]
    )

    for i, num_children in enumerate(sorted(df["num_children"].unique())):
        child_data = df[df["num_children"] == num_children]
        currency = "£" if country == "UK" else "$"
        
        fig.add_trace(go.Scatter(
            x=child_data["income"],
            y=child_data["mtr"],
            mode="lines",
            name=f'{num_children} {"child" if num_children == 1 else "children"}',
            line=dict(color=colors[i], width=2.5),
            hovertemplate=f"Income: {currency}%{{x:,.0f}}<br>MTR: %{{y:.1%}}<extra></extra>",
        ))

    fig.add_hline(y=0, line_dash="dash", line_color="gray", opacity=0.5)

    fig.update_layout(
        title=dict(text="Marginal Tax Rate by Number of Children", font=dict(size=20, color=COLORS["primary"])),
        xaxis=dict(title=f"Employment Income ({currency})", tickformat=",.0f", tickprefix=currency,
                   gridcolor="rgba(200,200,200,0.3)", showgrid=True),
        yaxis=dict(title="Marginal Tax Rate", tickformat=".0%", range=[0, 1],
                   gridcolor="rgba(200,200,200,0.3)", showgrid=True),
        hovermode="x unified",
        plot_bgcolor="white",
        paper_bgcolor="white",
        font=dict(family=FONT_FAMILY),
        legend=dict(x=0.98, y=0.02, xanchor="right", yanchor="bottom",
                    bgcolor="rgba(255,255,255,0.8)", bordercolor="rgba(0,0,0,0.2)", borderwidth=1),
        height=600,
    )

    return fig


def create_marginal_mtr_plot(df: pd.DataFrame, country: str) -> go.Figure:
    """Create marginal MTR plot (change in MTR per additional child)."""
    import plotly.express as px

    # Calculate marginal MTR (change from N-1 to N children)
    marginal_data = []
    for income in df["income"].unique():
        income_df = df[df["income"] == income].sort_values("num_children")
        for i in range(1, len(income_df)):
            current = income_df.iloc[i]
            previous = income_df.iloc[i-1]
            marginal_data.append({
                "income": income,
                "num_children": current["num_children"],
                "marginal_mtr": current["mtr"] - previous["mtr"]
            })

    df_marginal = pd.DataFrame(marginal_data)

    fig = go.Figure()
    colors = COLORS["gradient"][:len(df_marginal["num_children"].unique())]

    for i, num_children in enumerate(sorted(df_marginal["num_children"].unique())):
        child_data = df_marginal[df_marginal["num_children"] == num_children]
        currency = "£" if country == "UK" else "$"
        
        fig.add_trace(go.Scatter(
            x=child_data["income"],
            y=child_data["marginal_mtr"],
            mode="lines",
            name=get_child_ordinal(int(num_children)),
            line=dict(color=colors[i], width=2.5),
            hovertemplate=f"Income: {currency}%{{x:,.0f}}<br>MTR Change: %{{y:.1%}}<extra></extra>",
        ))

    fig.add_hline(y=0, line_dash="dash", line_color="gray", opacity=0.5)

    fig.update_layout(
        title=dict(text="Change in Marginal Tax Rate per Additional Child", font=dict(size=20, color=COLORS["primary"])),
        xaxis=dict(title=f"Employment Income ({currency})", tickformat=",.0f", tickprefix=currency,
                   gridcolor="rgba(200,200,200,0.3)", showgrid=True),
        yaxis=dict(title="MTR Change (percentage points)", tickformat=".1%",
                   gridcolor="rgba(200,200,200,0.3)", showgrid=True),
        hovermode="x unified",
        plot_bgcolor="white",
        paper_bgcolor="white",
        font=dict(family=FONT_FAMILY),
        legend=dict(x=0.98, y=0.02, xanchor="right", yanchor="bottom",
                    bgcolor="rgba(255,255,255,0.8)", bordercolor="rgba(0,0,0,0.2)", borderwidth=1),
        height=600,
    )

    return fig
