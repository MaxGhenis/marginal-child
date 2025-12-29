# The Marginal Child

Analyze marginal tax rates and benefits by number of children across the US and UK.

## Architecture

### Modern Stack

**Frontend**: Next.js 14 + React + TypeScript + Tailwind CSS + Recharts
**Backend**: FastAPI + PolicyEngine-US + PolicyEngine-UK
**Design**: PolicyEngine app-v2 design tokens (Inter font, Teal primary color)

### Project Structure

```
marginal-child/
├── backend/                 # FastAPI server
│   ├── app/
│   │   └── main.py         # API endpoints
│   └── requirements.txt
├── frontend/                # Next.js app
│   ├── app/
│   │   ├── page.tsx        # Main page
│   │   ├── layout.tsx      # Root layout
│   │   └── globals.css     # Inter font + Tailwind
│   └── components/
│       ├── ConfigPanel.tsx  # Configuration UI
│       └── ChartDisplay.tsx # Recharts visualization
├── marginal_child/          # Pure Python package
│   ├── pure_calculations.py # Core logic (no UI dependencies)
│   ├── constants.py         # App-v2 colors, regions, defaults
│   └── streamlit_ui.py      # Legacy Streamlit UI
├── app.py                  # Legacy Streamlit app
└── tests/                  # Pytest test suite
```

## Features

### 4 Visualization Modes

**Metrics:**
1. **Net Income**: Income after taxes and benefits
2. **Marginal Tax Rate**: % of additional earnings kept

**Views:**
1. **Absolute**: Show curves for 0-N children
2. **Marginal**: Show change per additional child

**All combinations available for both US and UK.**

### Countries

**United States:**
- All 50 states + DC
- Federal and state taxes
- SNAP, WIC, EITC, CTC, Medicaid, CHIP, ACA subsidies
- Marital status and spouse income options

**United Kingdom:**
- 12 ITL1 regions
- Universal Credit, Child Benefit, Income Tax, National Insurance
- Configurable rent and childcare costs
- Single parents with children ages 1, 3, 5

## Quick Start

### Development

```bash
# Terminal 1: Start backend
cd backend
python3.13 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
uvicorn app.main:app --reload --port 8000

# Terminal 2: Start frontend
cd frontend
npm install
npm run dev
```

**URLs:**
- Frontend: http://localhost:3000
- Backend API: http://localhost:8000
- API Docs: http://localhost:8000/docs

### Legacy Streamlit (Deprecated)

```bash
# Use .venv (has both policyengine-us and policyengine-uk)
source .venv/bin/activate
streamlit run app.py
```

## API Endpoints

### POST /calculate/us

Calculate US metrics.

**Request:**
```json
{
  "max_children": 3,
  "year": 2025,
  "marital_status": "single",
  "state_code": "CA",
  "spouse_income": 0,
  "include_health_benefits": true,
  "metric": "mtr",
  "view": "absolute"
}
```

**Response:**
```json
{
  "data": [
    {"income": 0, "num_children": 0, "mtr": 0.0},
    {"income": 1000, "num_children": 0, "mtr": 0.15},
    ...
  ]
}
```

### POST /calculate/uk

Calculate UK metrics.

**Request:**
```json
{
  "max_children": 3,
  "year": 2025,
  "region": "LONDON",
  "rent": 12000,
  "childcare_per_child": 12000,
  "brma": null,
  "metric": "mtr",
  "view": "absolute"
}
```

## Key Findings

### UK Marginal Tax Rate Spikes

**Universal Credit Taper (£10-50k):**
- 67.6% MTR due to UC withdrawal
- Extended by housing and childcare support
- "Benefit trap" where earning more provides minimal net income gain

**Child Benefit Withdrawal (£50-70k):**
- Higher MTRs for more children (48.8% to 57.7%)
- High Income Child Benefit Charge (1% per £100 over £60k)

**Personal Allowance Taper (£100-125k):**
- 62% MTR - the "60% tax trap"
- £1 allowance reduction per £2 earned

### Childcare Cost Assumptions

**UK**: £1,000/month per child (full-time nursery for ages 1, 3, 5)
**Reality**: Average full-time nursery costs £1,035-£1,247/month (£1,800+/month in London)

Our assumptions are **conservative** - real childcare costs are higher.

## Technology

- **PolicyEngine-US v1.428.0**: US federal and state tax-benefit model
- **PolicyEngine-UK v2.55.3**: UK tax-benefit model
- **Next.js 14**: React framework
- **FastAPI**: Python async web framework
- **Recharts**: React charting library
- **Tailwind CSS**: Utility-first CSS framework
- **Inter Font**: PolicyEngine company font

## Deployment

**Frontend**: Deploy to Vercel
**Backend**: Deploy to container platform (Google Cloud Run, Railway, etc.)

### Environment Variables

**Backend:**
- `CORS_ORIGINS`: Comma-separated allowed origins (production)

**Frontend:**
- `NEXT_PUBLIC_API_URL`: Backend API URL (default: http://localhost:8000)

## Design System

Uses PolicyEngine app-v2 design tokens:
- Primary color: Teal (#319795)
- Font: Inter
- Color gradients: Gray-400 → Teal-300
- Logo: Teal version

## Contributing

Contributions welcome! The codebase is structured for TDD:

```bash
# Run tests
pytest tests/ -v

# Test coverage
pytest tests/ --cov=marginal_child
```

## License

MIT

## Acknowledgments

Powered by [PolicyEngine](https://policyengine.org), the open-source tax-benefit microsimulation platform.
