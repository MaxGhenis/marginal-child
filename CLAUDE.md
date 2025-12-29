# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

The Marginal Child analyzes how government benefits and marginal tax rates change with each additional child using PolicyEngine microsimulation for both US and UK. It displays:
- **Marginal benefit**: Net income change from having an additional child
- **Marginal tax rate**: Change in MTR (in pp) from having an additional child

Both can be viewed in "By # Children" (absolute) or "Per Additional Child" (incremental) modes.

## Quick Start

```bash
# Frontend (Next.js)
cd frontend && npm install && npm run dev

# Backend runs on Modal - no local setup needed
# Production API: https://maxghenis--marginal-child-api-fastapi-app.modal.run
```

Frontend: http://localhost:3001 (uses local backend via .env.local, or Modal in production)

## Commands

### Development
```bash
# Frontend
cd frontend && npm run dev

# Local backend (optional - for testing changes)
cd backend && pip install -r requirements.txt && uvicorn app.main:app --reload --port 8000

# Deploy backend to Modal
cd backend && modal deploy modal_app.py
```

### Testing & Linting
```bash
make test          # pytest with 80% coverage requirement
make format        # black + isort (79 char)
make lint          # black --check, isort --check, flake8, mypy
```

## Architecture

```
frontend/                    # Next.js 14 + TypeScript + Tailwind + Recharts
├── app/page.tsx            # Main page, fetches all 4 data combinations
└── components/
    ├── ConfigPanel.tsx     # Household config (country, state, marital status, etc.)
    └── ChartDisplay.tsx    # Two tab rows: [Net Income | MTR] x [By # | Per Child]

backend/
├── app/main.py             # FastAPI endpoints
└── modal_app.py            # Modal deployment config (Python 3.13)

marginal_child/             # Pure Python package (no UI dependencies)
├── pure_calculations.py    # PolicyEngine calculation functions
├── chart_utils.py          # Data transformation, smoothing
└── constants.py            # Design tokens, states, regions
```

## API

**Production**: https://maxghenis--marginal-child-api-fastapi-app.modal.run

### POST /calculate/us
```json
{
  "max_children": 3, "year": 2025,
  "marital_status": "single", "state_code": "CA",
  "spouse_income": 0, "include_health_benefits": true,
  "metric": "net_income|mtr", "view": "absolute|marginal"
}
```

### POST /calculate/uk
```json
{
  "max_children": 3, "year": 2025,
  "region": "LONDON", "rent": 12000, "childcare_per_child": 12000,
  "metric": "net_income|mtr", "view": "absolute|marginal"
}
```

## Key Implementation Details

### PolicyEngine Axes
The `axes` feature must be embedded INSIDE the situation dict:
```python
situation["axes"] = [[{"name": "employment_income", "count": 500, "min": 0, "max": 500000}]]
sim = Simulation(situation=situation)
```

### MTR with Health Benefits (US)
Computed from numerical gradient since `marginal_tax_rate` doesn't include health:
```python
mtr = 1 - (net_income[i+1] - net_income[i]) / (income[i+1] - income[i])
```

### Entity Structure
- **US**: `people`, `families`, `households`, `tax_units`, `spm_units`
- **UK**: `people`, `benunits`, `households`

## Deployment

- **Frontend**: Deploy to Vercel (auto-uses Modal API via next.config.js default)
- **Backend**: `cd backend && modal deploy modal_app.py`

### Environment Variables
- `NEXT_PUBLIC_API_URL`: Override API URL (default: Modal production URL)
- `.env.local`: Local dev uses `http://localhost:8000`
