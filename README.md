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
│   └── init.py             # Core analysis modules (in progress)
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

1. **Data Loading & Cleaning** — Load the Brent oil price dataset, parse the `Date` column to datetime, sort chronologically, and check for missing values or duplicate dates.
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

### 4. Change Point Models: Purpose & Expected Outputs

Change point models identify points in time where the statistical properties of a series (e.g., mean, variance) shift abruptly, signaling a structural break rather than gradual drift. In this project, a Bayesian change point model (via PyMC) will treat the switch point (tau) as a random variable with a discrete uniform prior over the time index, define separate "before" and "after" parameters (e.g., two means, μ₁ and μ₂), and use MCMC sampling to estimate the posterior distribution of tau and the before/after parameters jointly.

**Expected outputs:**
- A posterior distribution over the most probable change point date(s) — a sharp, narrow peak indicates high confidence in a specific date.
- Posterior distributions for the "before" and "after" parameters, enabling probabilistic statements (e.g., "there is a 95% probability the mean price increased by at least $X after the change point").
- Convergence diagnostics (r_hat, trace plots) to validate the sampling process.

**Limitations:** the model identifies *when* a structural break occurred and *how large* it was, but does not itself prove *why* it occurred — causal attribution to a specific event requires separately comparing detected dates against the researched events timeline, and even a close temporal match does not constitute proof of causation.

### 5. Assumptions & Limitations

**Assumptions:**
- Daily closing prices are representative of true market conditions (no missing-data bias in the source dataset).
- A single/few discrete change points is a reasonable simplification of what is, in reality, continuous and multi-causal price formation.
- Events researched are treated as candidate explanations for detected change points, not confirmed causes.

**Limitations:**
- **Correlation vs. causation**: A change point occurring near the date of a known event is a temporal correlation, not proof that the event *caused* the shift. Oil prices are influenced by many simultaneous factors (macroeconomic conditions, currency fluctuations, speculative trading, inventory levels), and multiple candidate events often cluster near any given date, making single-cause attribution inherently uncertain.
- The model assumes a fixed number of change points (often just one in a simple implementation); real markets may have many overlapping regime shifts.
- Historical events data was manually curated and may not be exhaustive — smaller or regional events that nonetheless moved prices may be omitted.
- Bayesian change point detection identifies statistical breaks in the modeled series (e.g., log returns) — interpretation in terms of raw price levels requires care.

### 6. Communication Channels

Findings will be communicated via:
- A written analytical report (blog-post format suitable for Medium, or PDF) summarizing methodology, visualizations, and quantified impact statements — targeted at investors, policymakers, and energy company stakeholders.
- An interactive dashboard (Flask backend + React frontend) allowing stakeholders to explore historical trends, filter by date range, and see event-price correlations directly.
- Regular GitHub commits and issue tracking for technical transparency and reproducibility.

---

## Roadmap

- [x] **Task 1** — Project foundation: repo structure, events dataset, EDA, workflow documentation
- [ ] **Task 2** — Bayesian change point modeling (PyMC) and event association
- [ ] **Task 3** — Interactive Flask/React dashboard

---

## Tech Stack

Python · pandas · NumPy · statsmodels · PyMC · Matplotlib/Seaborn · Flask · React