"""FastAPI backend for The Marginal Child calculator."""

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field
from typing import Literal, Optional
import sys
import os

# Add parent directory to path to import marginal_child package
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '../..'))

from marginal_child.pure_calculations import (
    calculate_uk_mtr_absolute,
    calculate_uk_net_income_absolute,
    calculate_us_mtr_absolute,
    calculate_us_net_income_absolute,
    derive_marginal_from_absolute,
)
from marginal_child.chart_utils import smooth_marginal_mtr
import pandas as pd

app = FastAPI(title="The Marginal Child API", version="2.0.0")

# CORS configuration
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # In production, specify actual origins
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# Request models
class USCalculationRequest(BaseModel):
    max_children: int = Field(default=3, ge=1, le=6)
    year: int = Field(default=2025, ge=2021, le=2035)
    marital_status: Literal["single", "married"] = "single"
    state_code: str = Field(default="TX", min_length=2, max_length=2)
    spouse_income: float = Field(default=0, ge=0)
    include_health_benefits: bool = True
    metric: Literal["net_income", "mtr"] = "net_income"
    view: Literal["absolute", "marginal"] = "marginal"


class UKCalculationRequest(BaseModel):
    max_children: int = Field(default=3, ge=1, le=6)
    year: int = Field(default=2025, ge=2021, le=2035)
    region: str = "LONDON"
    brma: Optional[str] = None
    rent: int = Field(default=12000, ge=0)  # Annual
    childcare_per_child: int = Field(default=8000, ge=0)  # Annual
    metric: Literal["net_income", "mtr"] = "net_income"
    view: Literal["absolute", "marginal"] = "marginal"


@app.get("/")
async def root():
    """API root endpoint."""
    return {
        "name": "The Marginal Child API",
        "version": "2.0.0",
        "endpoints": [
            "/calculate/us",
            "/calculate/uk",
            "/health"
        ]
    }


@app.get("/health")
async def health():
    """Health check endpoint."""
    return {"status": "healthy"}


@app.post("/calculate/us")
async def calculate_us(request: USCalculationRequest):
    """Calculate US marginal benefits or tax rates."""
    try:
        if request.metric == "net_income":
            df = calculate_us_net_income_absolute(
                request.max_children,
                request.year,
                request.marital_status,
                request.state_code,
                request.spouse_income,
                request.include_health_benefits,
            )
            if request.view == "marginal":
                df = derive_marginal_from_absolute(df, "net_income", "marginal_benefit")
        else:  # mtr
            df = calculate_us_mtr_absolute(
                request.max_children,
                request.year,
                request.marital_status,
                request.state_code,
                request.spouse_income,
                request.include_health_benefits,
            )
            if request.view == "marginal":
                df = derive_marginal_from_absolute(df, "mtr", "marginal_mtr")
                data_list = df.to_dict(orient="records")
                data_list = smooth_marginal_mtr(data_list, window_size=20)
                df = pd.DataFrame(data_list)

        return {"data": df.to_dict(orient="records")}

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/calculate/uk")
async def calculate_uk(request: UKCalculationRequest):
    """Calculate UK marginal benefits or tax rates."""
    try:
        if request.metric == "net_income":
            df = calculate_uk_net_income_absolute(
                request.max_children,
                request.year,
                request.region,
                request.rent,
                request.childcare_per_child,
                request.brma,
            )
            if request.view == "marginal":
                df = derive_marginal_from_absolute(df, "net_income", "marginal_benefit")
        else:  # mtr
            df = calculate_uk_mtr_absolute(
                request.max_children,
                request.year,
                request.region,
                request.rent,
                request.childcare_per_child,
                request.brma,
            )
            if request.view == "marginal":
                df = derive_marginal_from_absolute(df, "mtr", "marginal_mtr")
                data_list = df.to_dict(orient="records")
                data_list = smooth_marginal_mtr(data_list, window_size=20)
                df = pd.DataFrame(data_list)

        return {"data": df.to_dict(orient="records")}

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
