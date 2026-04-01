# Budget Allocation Analysis

A Python project that models budget allocation as a decision-making problem
under constraints, analyzing how different allocation strategies perform
across varying scenarios and tradeoffs.

---

## What This Project Does

A company has a fixed $1,000,000 annual marketing budget to allocate across
five channels. This project asks: does the allocation strategy matter, and
by how much?

To answer that, the project simulates 18,000 possible budget outcomes across three strategies
and three market scenarios, stores all data in SQLite, runs analytical SQL
queries, and surfaces the tradeoffs through four charts and a decision summary.

---

## Channels & Assumptions

| Channel               | Baseline ROI | Volatility | Max Allocation |
|-----------------------|-------------|------------|----------------|
| Paid Search           | 3.2×        | 0.30       | 40%            |
| Social Media          | 2.5×        | 0.45       | 35%            |
| Content / SEO         | 4.1×        | 0.20       | 30%            |
| Email Marketing       | 5.8×        | 0.15       | 20%            |
| Events & Partnerships | 2.1×        | 0.60       | 25%            |

ROI draws use a log-normal distribution to prevent negative returns.
A diminishing returns penalty applies when any channel exceeds its cap.

---

## Strategies

| Strategy     | Philosophy                                                             |
|--------------|------------------------------------------------------------------------|
| Conservative | Load into Email + Content (high ROI, low volatility). Minimize Social and Events. |
| Balanced     | Spread proportionally. No channel dominates.                           |
| Aggressive   | Concentrate in Content/SEO and Events. Accept volatility for upside.   |

---

## Scenarios

| Scenario | ROI Multiplier | Interpretation               |
|----------|---------------|------------------------------|
| Low      | 0.65×         | Market headwinds, ad fatigue |
| Base     | 1.00×         | Normal operating conditions  |
| High     | 1.35×         | Tailwinds, strong conversion |

---

## How SQL Fits In

All raw data lives in a local SQLite database. Aggregations and summaries
are computed via SQL queries before results are passed into pandas for
analysis and charting. Four queries are used:

| Query   | Business Question                                                      |
|---------|------------------------------------------------------------------------|
| Query 1 | What is the average, min, and max return per strategy and scenario?    |
| Query 2 | What percentage of simulations fall below budget or exceed 2× return?  |
| Query 3 | Which strategy wins on expected return in each scenario?               |
| Query 4 | How does channel spend, ROI, and expected return break down per strategy? |

---

## Key Results

- Conservative wins on expected return in every scenario — $3.69M (Base),
  $5.00M (High), $2.41M (Low)
- Conservative has the best risk-adjusted efficiency ratio — 8.01 in Base,
  vs 7.21 for Balanced and 7.05 for Aggressive
- In the Low scenario, Conservative keeps 93.0% of simulations above 2×
  budget, compared to 83.6% for Aggressive and 74.4% for Balanced
- Aggressive captures the highest single ceiling — $8.56M in the High scenario
- Diversification does not automatically mean safety — Balanced performs worst
  on downside protection despite spreading budget across all five channels

See RESULTS.md for the full analysis and interpretation.

---

## How to Run

Open `budget_analysis.py` in Google Colab or run locally with Python 3.
The script generates a `results/` folder containing the SQLite database,
four charts, and three exported CSV tables.

Dependencies: `pandas`, `numpy`, `matplotlib` — all available by default
in Google Colab. `sqlite3` is part of Python's standard library.

---

## Tech Stack

| Tool               | Role                                              |
|--------------------|---------------------------------------------------|
| Python 3           | Core language                                     |
| pandas 2.2.2       | Data wrangling and metric computation             |
| numpy 2.0.2        | Monte Carlo simulation with log-normal draws      |
| matplotlib 3.10.0  | Four output charts                                |
| sqlite3            | Embedded database and SQL aggregation layer       |
| Google Colab       | Development and execution environment             |
| Claude Sonnet 4.6  | AI assistant used to design and build the project |
