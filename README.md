# Brent Oil Price Change Point Analysis

Analyzing the impact of major political and economic events on Brent crude oil prices using Bayesian change point detection.

**Author:** Beth Abraham
**Program:** Birhan Energies Data Science Challenge

---

## Project Overview

Brent crude oil prices are highly volatile and sensitive to geopolitical conflicts, OPEC policy decisions, economic shocks, and sanctions. This project analyzes over three decades of daily Brent oil price data (May 1987–September 2022) to:

- Identify major events that significantly impacted oil prices
- Apply Bayesian change point detection (PyMC) to statistically quantify structural breaks in the price series
- Associate detected change points with real-world events to generate actionable insights for investors, policymakers, and energy companies
- Present findings through an interactive dashboard

---

## Repository Structure
brent-oil-changepoint-analysis/
├── .github/
│   └── workflows/
│       └── unittests.yml       # CI pipeline for automated testing
├── .vscode/
│   └── settings.json           # Editor/test runner configuration
├── data/
│   ├── BrentOilPrices.csv      # Raw daily price data (not tracked in git)
│   └── events.csv              # Curated dataset of major oil-market events
├── notebooks/
│   ├── 01_eda.ipynb            # Exploratory data analysis & stationarity testing
│   └── README.md
├── scripts/
│   └── README.md               # Reusable data loading/cleaning scripts (in progress)
├── src/
│   ├── init.py
│   └── data_utils.py           # Reusable data loading/cleaning/feature functions
├── tests/
│   └── init.py             # Unit tests
├── .gitignore
├── requirements.txt
└── README.md
---

## Data

**Source:** Daily Brent crude oil prices, May 20, 1987 – September 30, 2022.

| Field | Description |
|---|---|
| `Date` | Date of recorded price (`day-month-year` format) |
| `Price` | Brent oil price in USD per barrel |

The raw price CSV is excluded from version control via `.gitignore`; only the curated `events.csv` is tracked.

---

## Setup & Installation

1. **Clone the repository**
```bash
   git clone https://github.com/Bethabrh/brent-oil-changepoint-analysis.git
   cd brent-oil-changepoint-analysis
```

2. **Install dependencies**
```bash
   pip install -r requirements.txt
```

3. **Add the data file**
   Place `BrentOilPrices.csv` inside the `data/` folder.

4. **Run the EDA notebook**
   Open `notebooks/01_eda.ipynb` in VS Code, select a Python kernel with the installed dependencies, and run all cells.

---

## Task 1: Analysis Workflow

### 1. Analysis Steps

1. **Data Loading & Cleaning** — Load the Brent oil price dataset, parse the `Date` column to datetime, sort chronologically, and check for missing values or duplicate dates. (Implemented as reusable, error-handled functions in `src/data_utils.py`.)
2. **Exploratory Data Analysis (EDA)** — Visualize the raw price trend to identify major shocks and regime shifts. Compute log returns (`log(price_t) - log(price_{t-1})`) to obtain a series better suited to statistical modeling.
3. **Stationarity Testing** — Run Augmented Dickey-Fuller (ADF) tests on both raw prices and log returns to formally confirm which series is stationary and should be used for downstream modeling.
4. **Volatility Analysis** — Compute rolling standard deviation of log returns to visualize volatility clustering and identify high-volatility periods.
5. **Event Research & Compilation** — Compile a structured dataset of major geopolitical, economic, and OPEC-policy events (1990–2022) likely to have influenced oil prices.
6. **Change Point Modeling (Task 2)** — Apply a Bayesian change point model (PyMC) to detect structural breaks in the price/return series, estimate the most probable break date(s), and quantify the shift in parameters (e.g., mean level) before vs. after.
7. **Event Association** — Compare detected change point dates against the researched events dataset to form hypotheses about likely causes.
8. **Insight Generation & Reporting** — Summarize quantified impacts and communicate findings to stakeholders via a written report and an interactive dashboard.

### 2. Event Research Methodology

Events were compiled from major, verifiable oil-market shocks spanning the dataset's range, categorized into: geopolitical conflicts (e.g., Gulf War, Russia-Ukraine war), OPEC policy decisions (e.g., 2014 non-cut, 2016 OPEC+ agreement), economic shocks (e.g., 1997 Asian Financial Crisis, 2008 Global Financial Crisis), and sanctions/geopolitical events (e.g., 2018 Iran sanctions). Sixteen events were documented with date, category, description, and expected price direction, stored in `data/events.csv`.

### 3. Time Series Properties & Modeling Implications

- **Trend**: The price series shows long relatively stable stretches punctuated by sharp shocks — the Gulf War spike (1990-91), a steady 2000s rise to a peak near $147/barrel (mid-2008), a Global Financial Crisis crash, a 2014-2016 decline, and an extreme COVID-19 volatility spike in 2020.
- **Stationarity**: An ADF test on raw prices returned a p-value of 0.2785 — we fail to reject the null hypothesis of a unit root, so raw prices are **non-stationary**. The same test on log returns returned a p-value of ~0.0000 — strongly rejecting non-stationarity, confirming log returns are **stationary**.
- **Volatility**: A 30-day rolling standard deviation of log returns shows clear volatility clustering, with the most extreme spike occurring in 2020 (COVID-19 demand collapse and Saudi-Russia price war), exceeding even the 2008 Financial Crisis and 1990-91 Gulf War volatility.
- **Modeling implication**: Because raw prices are non-stationary, change point modeling in Task 2 will primarily be applied to log returns (or with a model structure appropriate for a trending series), since standard Bayesian change point detection assumes a reasonably well-behaved data-generating process for pre/post-change parameters to be meaningfully estimated.

### 4. Communication Channels

Findings will be communicated via:
- A written analytical report (blog-post format suitable for Medium, or PDF) summarizing methodology, visualizations, and quantified impact statements — targeted at investors, policymakers, and energy company stakeholders.
- An interactive dashboard (Flask backend + React frontend) allowing stakeholders to explore historical trends, filter by date range, and see event-price correlations directly.
- Regular GitHub commits and issue tracking for technical transparency and reproducibility.

---

## Bayesian Change Point Models: Concepts, Outputs, and Limitations

### Why Use a Change Point Model?

Oil prices don't drift randomly and smoothly — they tend to hold a relatively stable behavior for a period, then shift abruptly in response to a shock (a war breaking out, an OPEC decision, a financial crisis). A change point model is built specifically to detect **when** that shift happened and **how large** it was, rather than just describing an overall trend line. This makes it well suited to a market like oil, where the interesting signal is the structural break itself, not the average behavior across the whole history.

### How the Model Works (Conceptually)

1. **Switch point (τ)**: treated as an unknown parameter with a prior distribution over all possible time indices in the dataset — the model doesn't assume where the break is in advance, it learns it from the data.
2. **Before/after parameters**: two sets of parameters (e.g., mean μ₁ before τ, mean μ₂ after τ) describe the data's behavior in each regime.
3. **Switch function**: at each time step, the model selects μ₁ or μ₂ depending on whether that time point falls before or after τ.
4. **Likelihood**: observed prices (or log returns) are modeled as noisy draws around whichever mean is currently active.
5. **MCMC sampling**: rather than returning a single "best guess," Bayesian inference (via MCMC) returns full posterior *distributions* over τ, μ₁, and μ₂ — capturing our uncertainty, not just a point estimate.

### Expected Outputs

- **Posterior distribution of τ**: shows which date(s) are most probable as the true change point. A narrow, sharp peak means high confidence in a specific date; a wide, flat posterior means the data doesn't clearly support one location over another.
- **Posterior distributions of regime parameters (μ₁, μ₂, or variances)**: allow probabilistic statements like "there is a 95% probability the mean log-return shifted by at least X after the change point," rather than a single deterministic number.
- **Convergence diagnostics** (r_hat ≈ 1.0, healthy trace plots): confirm the MCMC sampler actually explored the posterior properly and the results can be trusted.

### Limitations of the Approach

- The model tells us **when** and **how large** a shift was — it does **not** by itself tell us **why**. Attributing a detected change point to a specific real-world event is a separate, interpretive step done by comparing dates, not something the statistical model proves.
- Simple change point models assume a small, fixed number of breaks (often just one). Real oil markets likely have many overlapping regime shifts, so this is a simplification.
- Results are sensitive which series is modeled (raw price vs. log returns) and the choice of prior for τ.

---

## Assumptions and Limitations

### Assumptions

- Daily closing prices in the source dataset are treated as representative and accurate; no adjustment is made for potential data-collection anomalies.
- Modeling a small number of discrete change points is treated as a reasonable simplification of what is, in reality, a continuous and multi-causal price-formation process.
- Events in `data/events.csv` are treated only as **candidate explanations** for detected change points — their presence near a date is not treated as proof of impact.

### Limitations

- **Correlation vs. causal impact (critical distinction)**: If a detected change point falls close in time to a known event (e.g., an OPEC announcement), that is a **temporal correlation** — evidence *consistent with* a causal link, but not proof of one. Oil prices are driven by many simultaneous factors — macroeconomic conditions, currency movements, speculative trading positions, inventory data, weather, and multiple overlapping geopolitical events — so a single nearby event is rarely the sole or fully verified cause of a price shift. Establishing actual causation would require a counterfactual analysis (what would have happened without the event) that is outside the scope of this project; this analysis instead reports **statistically detected structural breaks** and **plausible associated events**, explicitly stopping short of causal claims.
- The events dataset was manually curated from major, well-documented events and is not exhaustive — smaller or more localized events that nonetheless moved prices may be omitted.
- A basic change point model assumes only one (or a small fixed number of) breaks; it may miss more gradual regime changes or fail to separate multiple closely-spaced shocks.
- Findings are based on historical data only and are not intended as a predictive trading signal.

---
## Task 2: Bayesian Change Point Modeling — Results

A single change-point model applied across the full 1987–2022 series proved statistically underdetermined (multiple comparably large shocks caused a multimodal posterior over tau, with elevated r-hat and divergences). To resolve this, the same model was applied to focused time windows around five major candidate events, each converging cleanly:

| Event Window | Detected Change Point | Matched Event (events.csv) | Price Impact |
|---|---|---|---|
| Gulf War | 1990-11-27 | Gulf War / Operation Desert Storm Begins (51d offset) | $31.85 → $31.21 (−2.0%) |
| Global Financial Crisis | 2008-07-08 | Oil Price Peaks at Record High (3d offset) | $138.16 → $135.21 (−2.1%) |
| 2014 OPEC Non-Cut | 2014-11-19 | OPEC Declines to Cut Production (8d offset) | $80.18 → $75.27 (−6.1%) |
| COVID / Price War | 2020-04-01 | WTI Futures Turn Negative / OPEC+ Record Cut (19d offset) | $22.62 → $20.99 (−7.2%) |
| Russia-Ukraine War | 2022-03-21 | Russian Invasion of Ukraine (25d offset) | $115.94 → $117.43 (+1.3%) |

All windowed models achieved acceptable convergence (r_hat ≤ 1.10, no unresolved divergences after tuning adjustments). Full methodology, trace plots, and posterior visualizations are in `notebooks/02_change_point_model.ipynb`.

**Key limitation discovered:** a single-change-point Bayesian model is well-suited to a *single, dominant* shock in a bounded window, but becomes statistically unstable across a 35-year span containing multiple comparably large shocks. Windowed detection is an effective mitigation and produces cleanly converged, event-aligned results, though it requires the analyst to pre-select candidate windows rather than fully automated discovery. A production version would extend to a proper multi-change-point or regime-switching model (see Advanced Extensions).

## Task 3: Interactive Dashboard

A full-stack dashboard visualizes the analysis results.

### Backend (Flask)

Located in `backend/app.py`. Endpoints:

| Endpoint | Description |
|---|---|
| `GET /api/health` | Health check |
| `GET /api/prices` | Historical price data (optional `start_date`/`end_date` query params) |
| `GET /api/changepoints` | Detected change points with quantified impact and matched events |
| `GET /api/events` | Full curated events dataset |
| `GET /api/summary` | Combined summary for dashboard overview |

**Run it:**
```bash
cd backend
pip install flask flask-cors
python app.py
```
Runs on `http://127.0.0.1:5001`.

### Frontend (React + Vite)

Located in `frontend/`. Built with React, Recharts for visualization, and a custom dark energy-industry themed UI.

**Run it:**
```bash
cd frontend
npm install
npm run dev
```
Runs on `http://localhost:5173`.

**Features:**
- Interactive price chart with change point markers
- Clickable change point cards showing quantified before/after impact
- Full sortable events timeline
- Responsive layout

### Screenshots

See `screenshots/` folder for dashboard views.

## Roadmap

- [x] **Task 1** — Project foundation: repo structure, events dataset, EDA, workflow documentation
- [ ] **Task 2** — Bayesian change point modeling (PyMC) and event association
- [ ] **Task 3** — Interactive Flask/React dashboard

---

## Tech Stack

Python · pandas · NumPy · statsmodels · PyMC · Matplotlib/Seaborn · Flask · React
