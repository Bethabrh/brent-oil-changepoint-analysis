# Brent Oil Price Change Point Analysis

Bayesian structural break detection on three decades of Brent crude oil prices, paired with a full-stack interactive dashboard for exploring detected change points, their associated real-world events, and model reliability diagnostics.

**Author:** Beth Abraham
**Program:** 10 Academy AI Mastery — Birhan Energies Data Science Challenge

![CI](https://github.com/Bethabrh/brent-oil-changepoint-analysis/actions/workflows/unittests.yml/badge.svg)

## Business Problem

Brent crude oil prices are highly volatile and sensitive to geopolitical conflicts, OPEC policy decisions, economic shocks, and sanctions. Investors, policymakers, and energy companies need a statistically rigorous way to identify exactly when the market's underlying behavior shifted — not just eyeball a price chart — and to trust that those shifts are real rather than noise.

## Solution Overview

This project applies Bayesian change point detection (PyMC) to over three decades of daily Brent oil prices (May 1987–September 2022) to statistically identify structural breaks in the price series, then matches each detected break to a real-world event (conflict, OPEC decision, sanction, etc.) within a defined time window. Results are served through a Flask API and displayed in a React dashboard, including MCMC convergence diagnostics (r-hat, ESS) so a non-technical audience can see at a glance how trustworthy each detected break is.

## Key Results

- 5 statistically significant change points detected across the full 1987–2022 price series
- 93% combined test coverage (34 automated tests: 17 unit + 17 integration), all passing
- Convergence diagnostics computed and exposed per change point, giving a plain-language reliability status (good / acceptable / poor) for every detected break
- CI pipeline runs the full test suite with coverage on every push

## Quick Start

**Backend:**
```bash
git clone https://github.com/Bethabrh/brent-oil-changepoint-analysis
cd brent-oil-changepoint-analysis
pip install -r requirements.txt
python backend/app.py
```

**Frontend** (in a separate terminal):
```bash
cd frontend
npm install
npm run dev
```

The dashboard expects the Flask API on `http://127.0.0.1:5001`.

## Project Structure
brent-oil-changepoint-analysis/
├── .github/workflows/ # CI pipeline (GitHub Actions)
├── backend/ # Flask API (app.py)
├── frontend/ # React dashboard
├── notebooks/ # Change point detection & EDA notebooks
├── scripts/
├── src/ # Core logic: data_utils.py, config.py
├── tests/ # Unit + integration tests
└── requirements.txt
## Demo

Run the Quick Start above, then visit `http://localhost:5173` to view the live dashboard.

## Technical Details

- **Data:** Daily Brent crude oil prices, May 1987–September 2022, paired with a curated dataset of major geopolitical and economic events
- **Model:** Bayesian change point detection via PyMC (MCMC sampling), detecting shifts in the underlying price/log-return distribution
- **Evaluation:** Model correctness verified via bit-for-bit identical outputs across a full refactor (ADF p-values, change point dates/impacts). Convergence assessed via r-hat and effective sample size (ESS), reported per change point in the dashboard's Model Reliability section

## Future Improvements

- Extend explainability with SHAP-style attribution for what drove each detected break
- Add confidence intervals around detected change point dates in the chart
- Automate event-matching with a lightweight NLP pipeline instead of manual date windows

## Author

Beth Abraham
10 Academy AI Mastery, KAIM9