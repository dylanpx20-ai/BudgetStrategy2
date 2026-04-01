# Results & Analysis

Full output from `budget_analysis.py` with interpretation.

---

## Simulation Parameters

| Parameter         | Value                                      |
|-------------------|--------------------------------------------|
| Total budget      | $1,000,000                                 |
| Channels          | 5                                          |
| Strategies        | 3 (Conservative, Balanced, Aggressive)     |
| Scenarios         | 3 (Low, Base, High)                        |
| Total simulations | 18,000 (2,000 per strategy × scenario)     |

---

## Query 1 — Average & Range of Returns by Strategy × Scenario

| Strategy     | Scenario | Avg Return | Min Return | Max Return |
|--------------|----------|------------|------------|------------|
| Conservative | Base     | $3,687,429 | $2,512,067 | $6,244,403 |
| Aggressive   | Base     | $3,544,701 | $2,191,115 | $7,173,848 |
| Balanced     | Base     | $3,394,199 | $2,171,884 | $5,793,974 |
| Conservative | High     | $4,997,156 | $3,353,787 | $8,221,364 |
| Aggressive   | High     | $4,764,891 | $3,140,021 | $8,560,858 |
| Balanced     | High     | $4,605,618 | $2,949,628 | $7,470,828 |
| Conservative | Low      | $2,407,750 | $1,482,897 | $5,796,836 |
| Aggressive   | Low      | $2,304,158 | $1,490,938 | $4,633,542 |
| Balanced     | Low      | $2,212,787 | $1,483,004 | $3,924,515 |

Conservative leads on average return in every scenario. The gap is most
pronounced in the High scenario — $4,997,156 vs $4,605,618 for Balanced,
an 8.5% difference. Aggressive has the highest individual ceiling in both
Base ($7,173,848) and High ($8,560,858), meaning it offers the best upside
at the cost of a consistently lower average and floor.

---

## Query 2 — Risk Profile

| Strategy     | Scenario | % Below Budget | % Above 2× Return |
|--------------|----------|----------------|-------------------|
| Conservative | Low      | 0.0%           | 93.0%             |
| Aggressive   | Low      | 0.0%           | 83.6%             |
| Balanced     | Low      | 0.0%           | 74.4%             |
| All          | Base     | 0.0%           | 100.0%            |
| All          | High     | 0.0%           | 100.0%            |

No strategy returned less than the original $1M budget across all 18,000
simulations. The real differentiation appears in the Low scenario, where
Conservative keeps 93.0% of outcomes above 2× budget vs 74.4% for Balanced
— an 18.6 percentage point gap.

Balanced's poor Low-scenario performance is a key finding. Spreading budget
evenly across channels of varying volatility does not minimize risk. Balanced
carries full exposure to Social Media (vol 0.45) and Events & Partnerships
(vol 0.60) without the ROI quality that Conservative draws from Email and
Content/SEO.

---

## Query 3 — Winning Strategy per Scenario

| Scenario | Winning Strategy | Avg Return |
|----------|-----------------|------------|
| Base     | Conservative    | $3,687,429 |
| High     | Conservative    | $4,997,156 |
| Low      | Conservative    | $2,407,750 |

Conservative wins on expected return in all three scenarios. This challenges
the common assumption that conservative allocations sacrifice return for
safety. The advantage comes from concentrating budget in Email Marketing
(5.8× ROI, 0.15 volatility) and Content/SEO (4.1× ROI, 0.20 volatility) —
the two channels with the strongest risk-adjusted fundamentals.

---

## Query 4 — Channel Spend by Strategy

### Conservative
| Channel               | Allocation | Spend    | ROI  | Expected Return |
|-----------------------|------------|----------|------|-----------------|
| Content / SEO         | 35%        | $350,000 | 4.1× | $1,435,000      |
| Email Marketing       | 20%        | $200,000 | 5.8× | $1,160,000      |
| Paid Search           | 20%        | $200,000 | 3.2× | $640,000        |
| Events & Partnerships | 20%        | $200,000 | 2.1× | $420,000        |
| Social Media          | 5%         | $50,000  | 2.5× | $125,000        |

### Balanced
| Channel               | Allocation | Spend    | ROI  | Expected Return |
|-----------------------|------------|----------|------|-----------------|
| Paid Search           | 25%        | $250,000 | 3.2× | $800,000        |
| Social Media          | 20%        | $200,000 | 2.5× | $500,000        |
| Content / SEO         | 20%        | $200,000 | 4.1× | $820,000        |
| Events & Partnerships | 20%        | $200,000 | 2.1× | $420,000        |
| Email Marketing       | 15%        | $150,000 | 5.8× | $870,000        |

### Aggressive
| Channel               | Allocation | Spend    | ROI  | Expected Return |
|-----------------------|------------|----------|------|-----------------|
| Content / SEO         | 30%        | $300,000 | 4.1× | $1,230,000      |
| Events & Partnerships | 30%        | $300,000 | 2.1× | $630,000        |
| Email Marketing       | 20%        | $200,000 | 5.8× | $1,160,000      |
| Paid Search           | 10%        | $100,000 | 3.2× | $320,000        |
| Social Media          | 10%        | $100,000 | 2.5× | $250,000        |

Conservative's edge comes from its 35% allocation to Content/SEO — the
highest single-channel spend in the project at $350,000 — paired with a
full 20% in Email Marketing. Aggressive's $300,000 bet on Events &
Partnerships (2.1× ROI, 0.60 volatility) is the key risk factor that
limits its average while enabling its high ceiling.

---

## Efficiency Ratio (Risk-Adjusted Return)

| Strategy     | Low  | Base | High |
|--------------|------|------|------|
| Conservative | 7.79 | 8.01 | 7.98 |
| Balanced     | 7.14 | 7.21 | 7.37 |
| Aggressive   | 7.01 | 7.05 | 7.34 |

The efficiency ratio measures average return per unit of standard deviation,
analogous to a Sharpe ratio. Conservative leads in all three scenarios and
is most dominant under stress — a ratio of 7.79 in Low vs 7.01 for
Aggressive, an 11% efficiency advantage when it matters most.

Balanced and Aggressive both improve in efficiency as conditions improve,
narrowing the gap slightly in the High scenario. Conservative never loses
its lead.

---

## Decision Summary

| Question                            | Answer                                      |
|-------------------------------------|---------------------------------------------|
| Highest expected return (Base)      | Conservative — $3,687,429                   |
| Best downside protection (Low)      | Conservative — 93.0% of outcomes above 2×  |
| Best risk-adjusted return           | Conservative — efficiency ratio of 8.01     |
| Highest upside ceiling (High)       | Aggressive — max return of $8,560,858       |

---

## Key Takeaways

**1. Conservative outperforms on expected return, not just safety.**
By concentrating in the two highest-ROI, lowest-volatility channels,
Conservative generates more average return than either alternative in
every scenario tested.

**2. Aggressive's edge is purely in the ceiling, not the average.**
The Aggressive strategy only wins if the goal is specifically to maximize
the chance of an exceptional outcome. Its average and floor are consistently
lower than Conservative's across all scenarios.

**3. Diversification does not automatically reduce risk.**
Balanced performs worst on downside protection in the Low scenario. Spreading
budget across high-volatility channels without weighting for ROI quality
dilutes returns without providing meaningful safety.

**4. Strategy choice depends on what you are optimizing for.**
Under uncertainty, Conservative is the dominant choice across every metric
except maximum upside. If an organization has a specific high-return target
that requires tail-end outcomes, Aggressive is the rational bet — but only then.
