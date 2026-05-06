import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.ticker as mticker
import matplotlib.patches as mpatches

# ─────────────────────────────────────────────
# 1. COUNTRY ECONOMIC BASELINE DATA
#    GDP figures: World Bank 2023 (current USD)
#    Internet contribution to GDP: World Bank / ITU estimates
#    Digital trade share: UNCTAD / McKinsey estimates
# ─────────────────────────────────────────────

countries = {
    "China": {
        "gdp_usd":              18.53e12,   # $18.53 trillion
        "internet_gdp_share":   0.065,      # ~6.5% of GDP is digitally dependent
        "digital_trade_share":  0.35,       # 35% of trade is digitally facilitated
        "economy_type":         "developing",
        "bandwidth_baseline_tbps": 67.6,
    },
    "Japan": {
        "gdp_usd":              4.21e12,
        "internet_gdp_share":   0.055,
        "digital_trade_share":  0.30,
        "economy_type":         "developed",
        "bandwidth_baseline_tbps": 23.04,
    },
    "South Korea": {
        "gdp_usd":              1.71e12,
        "internet_gdp_share":   0.060,
        "digital_trade_share":  0.32,
        "economy_type":         "developed",
        "bandwidth_baseline_tbps": 15.04,
    },
    "Singapore": {
        "gdp_usd":              0.497e12,
        "internet_gdp_share":   0.080,      # highly digitally dependent economy
        "digital_trade_share":  0.45,
        "economy_type":         "developed",
        "bandwidth_baseline_tbps": 23.52,
    },
    "India": {
        "gdp_usd":              3.55e12,
        "internet_gdp_share":   0.045,
        "digital_trade_share":  0.25,
        "economy_type":         "developing",
        "bandwidth_baseline_tbps": 15.0,    # approximate — Mumbai node
    },
}

# ─────────────────────────────────────────────
# 2. ELASTICITY COEFFICIENTS
#    Based on Qiang & Rossotto (2009) World Bank study
#    and updated estimates from ITU (2022)
#    Interpretation: per 10% connectivity loss,
#    what % of GDP is at risk?
# ─────────────────────────────────────────────

elasticity = {
    "developed":  0.25,   # 0.25% GDP per 10% connectivity loss
    "developing": 0.38,   # 0.38% GDP per 10% connectivity loss
}

# ─────────────────────────────────────────────
# 3. SCENARIO BANDWIDTH LOSS RESULTS
#    Pulled directly from Module 2 median outputs
# ─────────────────────────────────────────────

scenarios = {
    "S1: AAG severed": {
        "china_bw_loss_p10":  75.0,
        "china_bw_loss_p50":  81.6,
        "china_bw_loss_p90":  88.3,
        "repair_weeks":       5.3,
        # For allied nations — AAG disruption also affects regional routing
        "allied_bw_loss_pct": 45.0,  # estimated collateral loss for Japan/S.Korea
    },
    "S2: AAG + CHUS severed": {
        "china_bw_loss_p10":  85.3,
        "china_bw_loss_p50":  92.5,
        "china_bw_loss_p90":  99.7,
        "repair_weeks":       9.2,
        "allied_bw_loss_pct": 65.0,
    },
    "S3: Choke point attack": {
        "china_bw_loss_p10":  69.6,
        "china_bw_loss_p50":  76.0,
        "china_bw_loss_p90":  82.6,
        "repair_weeks":       12.2,
        "allied_bw_loss_pct": 70.0,  # Singapore/Manila disabled hits allies hard
    },
    "S4: Grey zone (partial)": {
        "china_bw_loss_p10":  25.2,
        "china_bw_loss_p50":  29.9,
        "china_bw_loss_p90":  34.7,
        "repair_weeks":       4.2,
        "allied_bw_loss_pct": 20.0,
    },
}

# ─────────────────────────────────────────────
# 4. DURATION MULTIPLIERS
#    GDP-at-risk scales with disruption duration
#    Annual GDP impact prorated to actual outage window
# ─────────────────────────────────────────────

durations = {
    "30 days":  30  / 365,
    "90 days":  90  / 365,
    "1 year":   365 / 365,
}

# ─────────────────────────────────────────────
# 5. GDP-AT-RISK CALCULATION
#    Formula:
#    GDP-at-risk = GDP
#                × internet_gdp_share
#                × (bw_loss_pct / 100)
#                × (elasticity / 10)   ← per 10% loss
#                × duration_fraction
# ─────────────────────────────────────────────

print("── GDP-AT-RISK MODEL ──\n")
print("Methodology: World Bank elasticity coefficients (Qiang & Rossotto 2009)")
print("Caveat: Estimates assume linear elasticity — actual impact may be non-linear\n")

results = []

for scenario_name, scenario_data in scenarios.items():
    for duration_label, duration_frac in durations.items():
        for country, cdata in countries.items():

            # Use China's own bandwidth loss; allies use collateral estimate
            if country == "China":
                bw_loss_p10 = scenario_data["china_bw_loss_p10"]
                bw_loss_p50 = scenario_data["china_bw_loss_p50"]
                bw_loss_p90 = scenario_data["china_bw_loss_p90"]
            else:
                # Allied nations experience collateral disruption
                bw_loss_p50 = scenario_data["allied_bw_loss_pct"]
                bw_loss_p10 = bw_loss_p50 * 0.75
                bw_loss_p90 = bw_loss_p50 * 1.25

            elast = elasticity[cdata["economy_type"]]
            gdp   = cdata["gdp_usd"]
            share = cdata["internet_gdp_share"]

            def calc_risk(bw_loss_pct):
                return gdp * share * (bw_loss_pct / 100) * (elast / 10) * duration_frac

            risk_p10 = calc_risk(bw_loss_p10)
            risk_p50 = calc_risk(bw_loss_p50)
            risk_p90 = calc_risk(bw_loss_p90)

            results.append({
                "scenario":       scenario_name,
                "country":        country,
                "duration":       duration_label,
                "bw_loss_p50":    bw_loss_p50,
                "gdp_risk_p10_bn": round(risk_p10 / 1e9, 2),
                "gdp_risk_p50_bn": round(risk_p50 / 1e9, 2),
                "gdp_risk_p90_bn": round(risk_p90 / 1e9, 2),
            })

df = pd.DataFrame(results)

# ─────────────────────────────────────────────
# 6. PRINT KEY RESULTS — China focus
# ─────────────────────────────────────────────

print("── CHINA GDP-AT-RISK BY SCENARIO (Median estimate, $USD Billions) ──\n")

china_df = df[df["country"] == "China"].copy()

pivot = china_df.pivot_table(
    index="scenario",
    columns="duration",
    values="gdp_risk_p50_bn"
)[["30 days", "90 days", "1 year"]]

print(pivot.to_string())
print()

# ─────────────────────────────────────────────
# 7. PRINT ALLIED NATION COLLATERAL DAMAGE
#    S2 scenario, 90-day window
# ─────────────────────────────────────────────

print("── ALLIED NATION COLLATERAL GDP-AT-RISK ──")
print("Scenario: S2 (AAG + CHUS severed) | Duration: 90 days\n")

allied_s2 = df[
    (df["scenario"] == "S2: AAG + CHUS severed") &
    (df["duration"] == "90 days") &
    (df["country"] != "China")
][["country", "bw_loss_p50", "gdp_risk_p10_bn", "gdp_risk_p50_bn", "gdp_risk_p90_bn"]]

print(allied_s2.to_string(index=False))

# ─────────────────────────────────────────────
# 8. TOTAL REGIONAL ECONOMIC IMPACT
#    Sum across all countries for each scenario
# ─────────────────────────────────────────────

print("\n── TOTAL REGIONAL GDP-AT-RISK (All countries, 90-day window, $B) ──\n")

regional = df[df["duration"] == "90 days"].groupby("scenario")["gdp_risk_p50_bn"].sum().round(2)
print(regional.to_string())

# ─────────────────────────────────────────────
# 9. VISUALIZATION 1 — China GDP-at-risk heatmap
# ─────────────────────────────────────────────

fig, axes = plt.subplots(1, 2, figsize=(14, 6))

# Chart 1: China GDP-at-risk by scenario and duration
china_plot = china_df.pivot_table(
    index="scenario", columns="duration", values="gdp_risk_p50_bn"
)[["30 days", "90 days", "1 year"]]

scenario_labels = ["S1: AAG\nsevered", "S2: AAG+CHUS\nsevered",
                   "S3: Choke point\nattack", "S4: Grey zone\n(partial)"]

x = np.arange(len(scenario_labels))
width = 0.25
colors = ["#93c5fd", "#1d4ed8", "#1e3a5f"]

for i, (duration, color) in enumerate(zip(["30 days", "90 days", "1 year"], colors)):
    vals = china_plot[duration].values
    bars = axes[0].bar(x + (i - 1) * width, vals, width,
                       label=duration, color=color)
    for bar in bars:
        h = bar.get_height()
        if h > 0:
            axes[0].annotate(f"${h:.1f}B",
                             xy=(bar.get_x() + bar.get_width() / 2, h),
                             xytext=(0, 3), textcoords="offset points",
                             ha="center", va="bottom", fontsize=7.5)

axes[0].set_title("China GDP-at-Risk by Scenario & Duration\n(Median estimate)", fontsize=11)
axes[0].set_ylabel("GDP-at-Risk (USD Billions)", fontsize=10)
axes[0].set_xticks(x)
axes[0].set_xticklabels(scenario_labels, fontsize=9)
axes[0].legend(fontsize=9)
axes[0].grid(axis="y", alpha=0.3)
axes[0].spines["top"].set_visible(False)
axes[0].spines["right"].set_visible(False)

# Chart 2: Regional collateral damage — S2, 90 days
s2_90 = df[
    (df["scenario"] == "S2: AAG + CHUS severed") &
    (df["duration"] == "90 days")
].sort_values("gdp_risk_p50_bn", ascending=True)

bar_colors = ["#ef4444" if c == "China" else "#1d4ed8"
              for c in s2_90["country"]]

bars2 = axes[1].barh(s2_90["country"], s2_90["gdp_risk_p50_bn"],
                     color=bar_colors, edgecolor="none")

for bar in bars2:
    w = bar.get_width()
    axes[1].annotate(f"${w:.1f}B",
                     xy=(w, bar.get_y() + bar.get_height() / 2),
                     xytext=(4, 0), textcoords="offset points",
                     ha="left", va="center", fontsize=9)

axes[1].set_title("Regional GDP-at-Risk: S2 Scenario\n(AAG + CHUS severed, 90-day window)", fontsize=11)
axes[1].set_xlabel("GDP-at-Risk (USD Billions)", fontsize=10)
axes[1].grid(axis="x", alpha=0.3)
axes[1].spines["top"].set_visible(False)
axes[1].spines["right"].set_visible(False)

# Legend for chart 2
red_patch  = mpatches.Patch(color="#ef4444", label="China (primary target)")
blue_patch = mpatches.Patch(color="#1d4ed8", label="Allied nations (collateral)")
axes[1].legend(handles=[red_patch, blue_patch], fontsize=9)

plt.tight_layout()
plt.savefig("gdp_at_risk.png", dpi=150, bbox_inches="tight")
plt.close()
print("\nSaved: gdp_at_risk.png")

# ─────────────────────────────────────────────
# 10. SAVE FULL RESULTS
# ─────────────────────────────────────────────

df.to_csv("economic_impact.csv", index=False)
print("Saved: economic_impact.csv")

print("\n── MODULE 3 COMPLETE ──")
print("Outputs:")
print("  economic_impact.csv  — full GDP-at-risk table")
print("  gdp_at_risk.png      — visualization")
print("\nMethodology note:")
print("  Elasticity coefficients from Qiang & Rossotto (2009) World Bank.")
print("  Estimates assume partial digital-GDP exposure — not total GDP impact.")
print("  Non-linear effects (financial contagion, supply chain cascade)")
print("  are not modeled and would increase real-world estimates.")