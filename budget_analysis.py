# =============================================================================
# PROJECT 3: Budget Allocation Analysis
# Author: [Your Name]
# Description: Models budget allocation as a decision problem under constraints,
#              comparing strategies across scenarios using Python + SQL.
# =============================================================================

# ── 0. DEPENDENCIES ──────────────────────────────────────────────────────────
import sqlite3
import os
import numpy as np
import pandas as pd
import matplotlib
import matplotlib.pyplot as plt
import matplotlib.ticker as mticker
from matplotlib.gridspec import GridSpec
from itertools import product

# Create output folder (works in Colab and locally)
os.makedirs("results", exist_ok=True)

print("✓ Libraries loaded")
print(f"  pandas {pd.__version__} | numpy {np.__version__} | matplotlib {matplotlib.__version__}")


# =============================================================================
# SECTION 1 — DEFINE MODEL INPUTS
# Core assumptions about each channel's behavior and constraints.
# These are grounded in typical B2B/B2C digital marketing benchmarks.
# =============================================================================

TOTAL_BUDGET = 1_000_000   # $1M fixed annual budget

# Channel definitions
# baseline_roi: expected $ return per $ spent under base conditions
# volatility:   std dev of roi multiplier across simulations (risk proxy)
# min_pct:      floor allocation (can't go below this share of budget)
# max_pct:      ceiling allocation (diminishing returns above this share)

CHANNELS = pd.DataFrame([
    {"channel": "Paid Search",         "baseline_roi": 3.2, "volatility": 0.30, "min_pct": 0.10, "max_pct": 0.40},
    {"channel": "Social Media",        "baseline_roi": 2.5, "volatility": 0.45, "min_pct": 0.05, "max_pct": 0.35},
    {"channel": "Content / SEO",       "baseline_roi": 4.1, "volatility": 0.20, "min_pct": 0.05, "max_pct": 0.30},
    {"channel": "Email Marketing",     "baseline_roi": 5.8, "volatility": 0.15, "min_pct": 0.05, "max_pct": 0.20},
    {"channel": "Events & Partnerships","baseline_roi": 2.1, "volatility": 0.60, "min_pct": 0.05, "max_pct": 0.25},
])

# Strategy definitions: percentage of budget allocated to each channel
# Each row must sum to 1.0 (100% of budget)
#
# Conservative  → heavy Email + Content (high ROI, low volatility)
# Balanced      → proportional to ROI, respects constraints
# Aggressive    → concentrates in Email + Content, accepts risk elsewhere

STRATEGIES = pd.DataFrame([
    # Conservative: maximize Email + Content (high ROI, low vol). Minimize Events + Social.
    {"strategy": "Conservative",  "Paid Search": 0.20, "Social Media": 0.05,
     "Content / SEO": 0.35, "Email Marketing": 0.20, "Events & Partnerships": 0.20},
    # 0.20 + 0.05 + 0.35 + 0.20 + 0.20 = 1.00 ✓

    # Balanced: no channel dominates, moderate spread
    {"strategy": "Balanced",      "Paid Search": 0.25, "Social Media": 0.20,
     "Content / SEO": 0.20, "Email Marketing": 0.15, "Events & Partnerships": 0.20},
    # 0.25 + 0.20 + 0.20 + 0.15 + 0.20 = 1.00 ✓

    # Aggressive: concentrate in high-ROI channels, accept Events volatility for upside
    {"strategy": "Aggressive",    "Paid Search": 0.10, "Social Media": 0.10,
     "Content / SEO": 0.30, "Email Marketing": 0.20, "Events & Partnerships": 0.30},
    # 0.10 + 0.10 + 0.30 + 0.20 + 0.30 = 1.00 ✓
]).set_index("strategy")

# Verify allocations sum to 1.0
for strat in STRATEGIES.index:
    total = STRATEGIES.loc[strat].sum()
    assert abs(total - 1.0) < 1e-9, f"Strategy '{strat}' allocations sum to {total:.4f}, not 1.0"

print("\n✓ Model inputs defined")
print(f"  Budget: ${TOTAL_BUDGET:,.0f} | Channels: {len(CHANNELS)} | Strategies: {len(STRATEGIES)}")


# =============================================================================
# SECTION 2 — SIMULATION ENGINE
# For each strategy × scenario combination, simulate N Monte Carlo draws.
# Scenario modifiers shift the ROI distribution up or down.
# Diminishing returns penalize over-concentration in any single channel.
# =============================================================================

N_SIMULATIONS = 2_000   # Monte Carlo draws per strategy × scenario
RANDOM_SEED    = 42

# Scenario multipliers applied to each channel's baseline ROI
# Low = headwinds (e.g., recession, ad fatigue), High = tailwinds
SCENARIOS = {
    "Low":  0.65,   # 35% below baseline
    "Base": 1.00,   # exactly baseline
    "High": 1.35,   # 35% above baseline
}

def diminishing_returns(alloc_pct: float, cap: float) -> float:
    """
    Penalizes over-allocation beyond a channel's effective cap.
    Returns a multiplier in (0, 1] applied to that channel's raw return.
    Channels at or below cap are unaffected (multiplier = 1.0).
    Channels above cap experience log-scaled efficiency loss.
    """
    if alloc_pct <= cap:
        return 1.0
    # Penalty: smoothly decreasing as allocation exceeds cap
    excess = (alloc_pct - cap) / cap     # relative overshoot
    return max(0.5, 1.0 - 0.4 * np.log1p(excess))

def simulate_strategy(strategy_name: str, scenario_name: str,
                      n_sims: int = N_SIMULATIONS,
                      seed: int = RANDOM_SEED) -> pd.DataFrame:
    """
    Runs a Monte Carlo simulation for one strategy under one scenario.

    Returns a DataFrame with one row per simulation, containing:
    - total_return ($): sum of returns across all channels
    - per-channel return columns
    """
    combo_seed = seed + hash((strategy_name, scenario_name)) % 100_000
    rng = np.random.default_rng(combo_seed)

    alloc = STRATEGIES.loc[strategy_name]           # channel allocation %s
    scenario_mult = SCENARIOS[scenario_name]        # scenario shift

    results = []
    for _ in range(n_sims):
        row = {"strategy": strategy_name, "scenario": scenario_name}
        total_return = 0.0

        for _, ch in CHANNELS.iterrows():
            channel       = ch["channel"]
            spend         = alloc[channel] * TOTAL_BUDGET
            base_roi      = ch["baseline_roi"] * scenario_mult
            vol           = ch["volatility"]

            # Draw ROI from a log-normal distribution to prevent negative returns
            # log-normal parameters derived from mean and std of underlying normal
            mu_ln  = np.log(base_roi**2 / np.sqrt(base_roi**2 + (base_roi * vol)**2))
            sig_ln = np.sqrt(np.log(1 + vol**2))
            roi    = rng.lognormal(mean=mu_ln, sigma=sig_ln)

            # Apply diminishing returns penalty
            dr_mult = diminishing_returns(alloc[channel], ch["max_pct"])
            channel_return = spend * roi * dr_mult

            row[f"return_{channel.replace(' ', '_').replace('/', '_')}"] = round(channel_return, 2)
            total_return += channel_return

        row["total_return"] = round(total_return, 2)
        results.append(row)

    return pd.DataFrame(results)


# Run all 9 combinations (3 strategies × 3 scenarios)
print("\n⏳ Running Monte Carlo simulations...")
sim_frames = []
for strat, scen in product(STRATEGIES.index, SCENARIOS.keys()):
    df = simulate_strategy(strat, scen)
    sim_frames.append(df)

sim_df = pd.concat(sim_frames, ignore_index=True)
print(f"✓ Simulation complete: {len(sim_df):,} total draws across 9 combinations")


# =============================================================================
# SECTION 3 — SQLITE DATABASE
# Store channel metadata, allocation decisions, and simulation results
# in a local SQLite database. All downstream aggregations use SQL.
# =============================================================================

DB_PATH = "results/budget_analysis.db"
conn    = sqlite3.connect(DB_PATH)
cur     = conn.cursor()

print(f"\n✓ SQLite database created at: {DB_PATH}")

# ── Create tables ─────────────────────────────────────────────────────────────

cur.executescript("""
    DROP TABLE IF EXISTS channels;
    DROP TABLE IF EXISTS allocations;
    DROP TABLE IF EXISTS simulation_results;

    CREATE TABLE channels (
        channel_id   INTEGER PRIMARY KEY AUTOINCREMENT,
        channel_name TEXT    NOT NULL,
        baseline_roi REAL    NOT NULL,
        volatility   REAL    NOT NULL,
        min_pct      REAL    NOT NULL,
        max_pct      REAL    NOT NULL
    );

    CREATE TABLE allocations (
        allocation_id INTEGER PRIMARY KEY AUTOINCREMENT,
        strategy      TEXT NOT NULL,
        channel_name  TEXT NOT NULL,
        alloc_pct     REAL NOT NULL,
        spend_dollars REAL NOT NULL
    );

    CREATE TABLE simulation_results (
        sim_id        INTEGER PRIMARY KEY AUTOINCREMENT,
        strategy      TEXT NOT NULL,
        scenario      TEXT NOT NULL,
        total_return  REAL NOT NULL
    );
"""
)

# ── Insert channel data ────────────────────────────────────────────────────────
CHANNELS.rename(columns={"channel": "channel_name"}).to_sql(
    "channels", conn, if_exists="append", index=False
)

# ── Insert allocation data ─────────────────────────────────────────────────────
alloc_rows = []
for strat in STRATEGIES.index:
    for ch in CHANNELS["channel"]:
        pct = STRATEGIES.loc[strat, ch]
        alloc_rows.append({
            "strategy":      strat,
            "channel_name":  ch,
            "alloc_pct":     pct,
            "spend_dollars": pct * TOTAL_BUDGET,
        })
pd.DataFrame(alloc_rows).to_sql("allocations", conn, if_exists="append", index=False)

# ── Insert simulation results ──────────────────────────────────────────────────
sim_df[["strategy", "scenario", "total_return"]].to_sql(
    "simulation_results", conn, if_exists="append", index=False
)

conn.commit()
print("✓ Tables populated: channels, allocations, simulation_results")


# =============================================================================
# SECTION 4 — SQL QUERIES
# These queries do the heavy analytical lifting BEFORE pandas.
# Each query answers a specific business question.
# =============================================================================

print("\n" + "="*65)
print("SQL QUERY RESULTS")
print("="*65)

# ── SQL Query 1: Expected return and risk by strategy × scenario ──────────────
QUERY_1 = """
    SELECT
        strategy,
        scenario,
        ROUND(AVG(total_return), 0)                          AS avg_return,
        ROUND(MIN(total_return), 0)                          AS min_return,
        ROUND(MAX(total_return), 0)                          AS max_return,
        ROUND(AVG(total_return) - MIN(total_return), 0)      AS upside_vs_min,
        COUNT(*)                                             AS n_simulations
    FROM simulation_results
    GROUP BY strategy, scenario
    ORDER BY scenario, avg_return DESC;
"""
q1 = pd.read_sql_query(QUERY_1, conn)
print("\n📊 Query 1 — Average & Range of Returns by Strategy × Scenario")
print(q1.to_string(index=False))

# ── SQL Query 2: Downside risk — % of simulations below budget ────────────────
QUERY_2 = """
    SELECT
        strategy,
        scenario,
        ROUND(100.0 * SUM(CASE WHEN total_return < 1000000 THEN 1 ELSE 0 END)
              / COUNT(*), 1)                                 AS pct_below_budget,
        ROUND(100.0 * SUM(CASE WHEN total_return > 2000000 THEN 1 ELSE 0 END)
              / COUNT(*), 1)                                 AS pct_above_2x
    FROM simulation_results
    GROUP BY strategy, scenario
    ORDER BY scenario, strategy;
"""
q2 = pd.read_sql_query(QUERY_2, conn)
print("\n📊 Query 2 — Risk Profile: % Simulations Below Budget / Above 2× Return")
print(q2.to_string(index=False))

# ── SQL Query 3: Top Strategy by Average Return per Scenario ─────────────────
QUERY_3 = """
    WITH avg_returns AS (
        SELECT
            strategy,
            scenario,
            ROUND(AVG(total_return), 0) AS avg_return
        FROM simulation_results
        GROUP BY strategy, scenario
    ),
    ranked AS (
        SELECT *,
            RANK() OVER (PARTITION BY scenario ORDER BY avg_return DESC) AS rnk
        FROM avg_returns
    )
    SELECT scenario, strategy, avg_return
    FROM ranked
    WHERE rnk = 1
    ORDER BY scenario ASC, avg_return DESC;
"""
q3 = pd.read_sql_query(QUERY_3, conn)
print("\n📊 Query 3 — Top Strategy by Average Return per Scenario")
print(q3.to_string(index=False))

# ── SQL Query 4: Channel spend breakdown by strategy ─────────────────────────
QUERY_4 = """
    SELECT
        a.strategy,
        a.channel_name,
        ROUND(a.alloc_pct * 100, 1)  AS alloc_pct,
        ROUND(a.spend_dollars, 0)    AS spend_dollars,
        ROUND(c.baseline_roi, 2)     AS baseline_roi,
        ROUND(c.volatility, 2)       AS volatility,
        ROUND(a.spend_dollars * c.baseline_roi, 0) AS expected_base_return
    FROM allocations a
    JOIN channels c ON a.channel_name = c.channel_name
    ORDER BY a.strategy, a.alloc_pct DESC;
"""
q4 = pd.read_sql_query(QUERY_4, conn)
print("\n📊 Query 4 — Channel Spend, ROI & Expected Return by Strategy")
print(q4.to_string(index=False))


# =============================================================================
# SECTION 5 — ANALYTICS IN PANDAS
# Pull SQL results into pandas and compute derived metrics:
# efficiency ratio, risk-adjusted return, and scenario spread.
# =============================================================================

# Master summary from Query 1
summary = q1.copy()

# Compute standard deviation from raw simulation data (not available in SQL easily)
std_df = (sim_df.groupby(["strategy", "scenario"])["total_return"]
                .std()
                .reset_index()
                .rename(columns={"total_return": "std_return"}))

summary = summary.merge(std_df, on=["strategy", "scenario"])

# Efficiency ratio: mean return per dollar of std dev (Sharpe-like)
summary["efficiency_ratio"] = (summary["avg_return"] / summary["std_return"]).round(2)

# Scenario ordering for cleaner charts
scenario_order  = ["Low", "Base", "High"]
strategy_order  = ["Conservative", "Balanced", "Aggressive"]
summary["scenario"]  = pd.Categorical(summary["scenario"],  categories=scenario_order,  ordered=True)
summary["strategy"]  = pd.Categorical(summary["strategy"],  categories=strategy_order,  ordered=True)
summary = summary.sort_values(["scenario", "strategy"]).reset_index(drop=True)

# Pivot for heatmap-style views
pivot_avg = summary.pivot(index="strategy", columns="scenario", values="avg_return")
pivot_eff = summary.pivot(index="strategy", columns="scenario", values="efficiency_ratio")

print("\n✓ Derived metrics computed")
print("\nEfficiency Ratio (higher = better risk-adjusted return):")
print(pivot_eff.to_string())


# =============================================================================
# SECTION 6 — VISUALISATIONS
# Four polished charts, each answering a distinct analytical question.
# Saved to results/ at 150 dpi for GitHub README embedding.
# =============================================================================

# ── Visual style ──────────────────────────────────────────────────────────────
plt.rcParams.update({
    "figure.facecolor":  "#F8F9FA",
    "axes.facecolor":    "#FFFFFF",
    "axes.grid":         True,
    "grid.color":        "#E0E0E0",
    "grid.linestyle":    "--",
    "grid.linewidth":    0.6,
    "font.family":       "DejaVu Sans",
    "axes.spines.top":   False,
    "axes.spines.right": False,
    "axes.titlesize":    13,
    "axes.titleweight":  "bold",
    "axes.labelsize":    11,
    "xtick.labelsize":   10,
    "ytick.labelsize":   10,
})

COLORS = {
    "Conservative": "#2196F3",   # blue
    "Balanced":     "#4CAF50",   # green
    "Aggressive":   "#FF5722",   # orange-red
}
SCENARIO_COLORS = {"Low": "#EF9A9A", "Base": "#90CAF9", "High": "#A5D6A7"}


# ─────────────────────────────────────────────────────────────────────────────
# Chart 1: Expected Return by Strategy × Scenario (grouped bar)
# Question answered: "Which strategy performs best in each scenario?"
# ─────────────────────────────────────────────────────────────────────────────
fig, ax = plt.subplots(figsize=(11, 6))

x        = np.arange(len(scenario_order))
n_strats = len(strategy_order)
width    = 0.22
offsets  = np.linspace(-(n_strats - 1) / 2 * width, (n_strats - 1) / 2 * width, n_strats)

for i, strat in enumerate(strategy_order):
    vals = [pivot_avg.loc[strat, scen] / 1e6 for scen in scenario_order]
    bars = ax.bar(x + offsets[i], vals, width=width,
                  label=strat, color=COLORS[strat], alpha=0.88, edgecolor="white", linewidth=0.8)
    for bar, val in zip(bars, vals):
        if val >= 0.01: # Only label if value is large enough to be visible
            ax.text(bar.get_x() + bar.get_width() / 2,
                    bar.get_height() + 0.02,
                    f"${val:.2f}M", ha="center", va="bottom", fontsize=8.5, fontweight="bold")

ax.axhline(y=TOTAL_BUDGET / 1e6, color="#555", linestyle=":", linewidth=1.2, label="Budget ($1M)")
ax.set_xticks(x)
ax.set_xticklabels(scenario_order)
ax.set_xlabel("Performance Scenario")
ax.set_ylabel("Expected Total Return ($M)")
ax.set_title("Expected Return by Strategy & Scenario")
ax.yaxis.set_major_formatter(mticker.FuncFormatter(lambda v, _: f"${v:.1f}M"))
ax.legend(framealpha=0.9, fontsize=10, bbox_to_anchor=(1.05, 1), loc='upper left', borderaxespad=0.)
fig.tight_layout()
fig.savefig("results/chart1_expected_returns.png", dpi=150, bbox_inches="tight")
plt.show()
print("✓ Chart 1 saved")


# ─────────────────────────────────────────────────────────────────────────────
# Chart 2: Return Distribution Boxplots (Base Scenario)
# Question answered: "How wide is the range of outcomes for each strategy?"
# ─────────────────────────────────────────────────────────────────────────────
fig, ax = plt.subplots(figsize=(9, 6))

base_data = [
    sim_df[(sim_df["strategy"] == s) & (sim_df["scenario"] == "Base")]["total_return"].values / 1e6
    for s in strategy_order
]

bp = ax.boxplot(base_data, patch_artist=True, notch=True,
                medianprops=dict(color="black", linewidth=2),
                whiskerprops=dict(linewidth=1.3),
                capprops=dict(linewidth=1.3),
                flierprops=dict(marker=".", markersize=3, alpha=0.35))

for patch, strat in zip(bp["boxes"], strategy_order):
    patch.set_facecolor(COLORS[strat])
    patch.set_alpha(0.75)

ax.axhline(y=TOTAL_BUDGET / 1e6, color="#555", linestyle=":", linewidth=1.2, label="Budget ($1M)")
ax.set_xticks(range(1, len(strategy_order) + 1))
ax.set_xticklabels(strategy_order)
ax.set_ylabel("Total Return ($M)")
ax.set_title("Return Distribution — Base Scenario\n(Notch = 95% CI of Median)")
ax.yaxis.set_major_formatter(mticker.FuncFormatter(lambda v, _: f"${v:.1f}M"))
ax.legend()
fig.tight_layout()
fig.savefig("results/chart2_distribution_boxplot.png", dpi=150, bbox_inches="tight")
plt.show()
print("✓ Chart 2 saved")


# ─────────────────────────────────────────────────────────────────────────────
# Chart 3: Risk vs. Return Scatter (all 9 strategy × scenario combos)
# Question answered: "What is the risk-return tradeoff?"
# ─────────────────────────────────────────────────────────────────────────────
fig, ax = plt.subplots(figsize=(9, 6))

for _, row in summary.iterrows():
    ax.scatter(row["std_return"] / 1e6, row["avg_return"] / 1e6,
               s=180, color=COLORS[row["strategy"]],
               marker={"Low": "v", "Base": "o", "High": "^"}[row["scenario"]],
               edgecolors="white", linewidths=0.8, zorder=3,
               label=f"{row['strategy']} / {row['scenario']}")
    ax.annotate(
        f"{row['strategy'][:3]}\n{row['scenario']}",
        xy=(row["std_return"] / 1e6, row["avg_return"] / 1e6),
        xytext=(5, 4), textcoords="offset points",
        fontsize=7.5, color="#333"
    )

ax.axhline(y=TOTAL_BUDGET / 1e6, color="#555", linestyle=":", linewidth=1.2, label="Budget ($1M)")
ax.set_xlabel("Risk (Std Dev of Return, $M)")
ax.set_ylabel("Expected Return ($M)")
ax.set_title("Risk vs. Return: All Strategies & Scenarios")
ax.xaxis.set_major_formatter(mticker.FuncFormatter(lambda v, _: f"${v:.2f}M"))
ax.yaxis.set_major_formatter(mticker.FuncFormatter(lambda v, _: f"${v:.1f}M"))

# Custom legend (strategies by color, scenarios by marker)
from matplotlib.lines import Line2D
legend_elements = (
    [Line2D([0], [0], marker="o", color="w", markerfacecolor=c,
             markersize=10, label=s) for s, c in COLORS.items()] +
    [Line2D([0], [0], marker=m, color="#555", markersize=8, linestyle="none", label=f"{sc} scenario")
     for sc, m in zip(["Low", "Base", "High"], ["v", "o", "^"])]
)
ax.legend(handles=legend_elements, fontsize=8.5, framealpha=0.9)
fig.tight_layout()
fig.savefig("results/chart3_risk_return_scatter.png", dpi=150, bbox_inches="tight")
plt.show()
print("✓ Chart 3 saved")


# ─────────────────────────────────────────────────────────────────────────────
# Chart 4: Budget Allocation Breakdown (stacked bar per strategy)
# Question answered: "Where does each strategy actually put the money?"
# ─────────────────────────────────────────────────────────────────────────────
fig, ax = plt.subplots(figsize=(10, 5))

channel_colors = ["#5C6BC0", "#26C6DA", "#66BB6A", "#FFA726", "#EF5350"]
ch_names       = CHANNELS["channel"].tolist()
bar_positions  = np.arange(len(strategy_order))

bottoms = np.zeros(len(strategy_order))
for ch, color in zip(ch_names, channel_colors):
    vals = [STRATEGIES.loc[s, ch] * 100 for s in strategy_order]
    bars = ax.bar(bar_positions, vals, bottom=bottoms,
                  color=color, label=ch, edgecolor="white", linewidth=0.6)
    for j, (bar, val) in enumerate(zip(bars, vals)):
        if val >= 7:    # only label if segment is wide enough to read
            ax.text(bar.get_x() + bar.get_width() / 2,
                    bottoms[j] + val / 2,
                    f"{val:.0f}%", ha="center", va="center",
                    fontsize=9, color="white", fontweight="bold")
    bottoms += np.array(vals)

ax.set_xticks(bar_positions)
ax.set_xticklabels(strategy_order, fontsize=12)
ax.set_ylabel("Budget Allocation (%)")
ax.set_title("Budget Allocation by Channel & Strategy")
ax.set_ylim(0, 105)
ax.yaxis.set_major_formatter(mticker.FuncFormatter(lambda v, _: f"{v:.0f}%"))
ax.legend(loc="upper right", fontsize=9, framealpha=0.9)
fig.tight_layout()
fig.savefig("results/chart4_allocation_breakdown.png", dpi=150, bbox_inches="tight")
plt.show()
print("✓ Chart 4 saved")


# =============================================================================
# SECTION 7 — EXPORT TABLES TO CSV
# Machine-readable outputs for the results/ folder and README.
# =============================================================================

# Full summary table
summary_export = summary[[
    "strategy", "scenario", "avg_return", "min_return",
    "max_return", "std_return", "efficiency_ratio"
]].copy()
summary_export.columns = [
    "Strategy", "Scenario", "Avg Return ($)",
    "Min Return ($)", "Max Return ($)", "Std Dev ($)", "Efficiency Ratio"
]
summary_export.to_csv("results/summary_by_strategy_scenario.csv", index=False)

# Channel allocation + expected returns (from SQL query 4)
q4.to_csv("results/channel_allocations.csv", index=False)

# Risk profile table (from SQL query 2)
q2.to_csv("results/risk_profile.csv", index=False)

print("\n✓ Tables exported to results/")


# =============================================================================
# SECTION 8 — DECISION SUMMARY
# Plain-language takeaways. This is what goes in RESULTS.md.
# =============================================================================

print("\n" + "="*65)
print("DECISION SUMMARY")
print("="*65)

best_base = summary[summary["scenario"] == "Base"].sort_values("avg_return", ascending=False).iloc[0]
safest    = summary[summary["scenario"] == "Low"].sort_values("min_return", ascending=False).iloc[0]
best_eff  = summary[summary["scenario"] == "Base"].sort_values("efficiency_ratio", ascending=False).iloc[0]
best_high = summary[summary["scenario"] == "High"].sort_values("avg_return", ascending=False).iloc[0]

print(f"""
 1. HIGHEST EXPECTED RETURN (Base Scenario)
     → {best_base['strategy']} with avg return of ${int(best_base['avg_return']):,d}

  2. BEST DOWNSIDE PROTECTION (Low Scenario, highest floor)
     → {safest['strategy']} with min return of ${int(safest['min_return']):,d}

  3. BEST RISK-ADJUSTED RETURN (Efficiency Ratio, Base Scenario)
     → {best_eff['strategy']} with efficiency ratio of {best_eff['efficiency_ratio']:.2f}

  4. BEST UPSIDE CAPTURE (High Scenario)
     → {best_high['strategy']} with avg return of ${int(best_high['avg_return']):,d}
""")

conn.close()
print("="*65)
print("✓ Analysis complete. All outputs saved to results/")
print("="*65)
