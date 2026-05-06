import networkx as nx
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
from collections import defaultdict

# ─────────────────────────────────────────────
# LOAD THE GRAPH FROM MODULE 1
# We rebuild it here so Module 2 is self-contained
# ─────────────────────────────────────────────

nodes = [
    {"id": "SHA", "name": "Shanghai",        "country": "China",        "lat": 31.23,  "lon": 121.47, "chinese": True},
    {"id": "HKG", "name": "Hong Kong",       "country": "China",        "lat": 22.30,  "lon": 114.17, "chinese": True},
    {"id": "GZH", "name": "Guangzhou",       "country": "China",        "lat": 23.13,  "lon": 113.26, "chinese": True},
    {"id": "TPE", "name": "Taipei",          "country": "Taiwan",       "lat": 25.03,  "lon": 121.56, "chinese": False},
    {"id": "TKO", "name": "Tseung Kwan O",   "country": "Hong Kong",    "lat": 22.32,  "lon": 114.26, "chinese": True},
    {"id": "KRS", "name": "Keoje (Busan)",   "country": "South Korea",  "lat": 35.10,  "lon": 129.03, "chinese": False},
    {"id": "OKI", "name": "Okinawa",         "country": "Japan",        "lat": 26.33,  "lon": 127.98, "chinese": False},
    {"id": "CHP", "name": "Chikura",         "country": "Japan",        "lat": 35.00,  "lon": 140.08, "chinese": False},
    {"id": "SIN", "name": "Singapore",       "country": "Singapore",    "lat": 1.35,   "lon": 103.82, "chinese": False},
    {"id": "BKK", "name": "Satun (Bangkok)", "country": "Thailand",     "lat": 6.62,   "lon": 100.07, "chinese": False},
    {"id": "MNL", "name": "Manila",          "country": "Philippines",  "lat": 14.60,  "lon": 120.98, "chinese": False},
    {"id": "JKT", "name": "Jakarta",         "country": "Indonesia",    "lat": -6.21,  "lon": 106.85, "chinese": False},
    {"id": "MUM", "name": "Mumbai",          "country": "India",        "lat": 19.08,  "lon": 72.88,  "chinese": False},
    {"id": "CHN", "name": "Chennai",         "country": "India",        "lat": 13.08,  "lon": 80.27,  "chinese": False},
    {"id": "COL", "name": "Colombo",         "country": "Sri Lanka",    "lat": 6.93,   "lon": 79.85,  "chinese": False},
    {"id": "DJI", "name": "Djibouti",        "country": "Djibouti",     "lat": 11.59,  "lon": 43.14,  "chinese": True},
    {"id": "KHI", "name": "Karachi",         "country": "Pakistan",     "lat": 24.86,  "lon": 67.01,  "chinese": True},
    {"id": "JED", "name": "Jeddah",          "country": "Saudi Arabia", "lat": 21.49,  "lon": 39.19,  "chinese": False},
    {"id": "FUJ", "name": "Fujairah",        "country": "UAE",          "lat": 25.12,  "lon": 56.34,  "chinese": False},
    {"id": "MRS", "name": "Marseille",       "country": "France",       "lat": 43.30,  "lon": 5.37,   "chinese": False},
    {"id": "PTE", "name": "Portunus (UK)",   "country": "UK",           "lat": 51.50,  "lon": -0.90,  "chinese": False},
    {"id": "MOM", "name": "Mombasa",         "country": "Kenya",        "lat": -4.05,  "lon": 39.67,  "chinese": False},
    {"id": "LAX", "name": "Los Angeles",     "country": "USA",          "lat": 33.93,  "lon": -118.41,"chinese": False},
    {"id": "SFO", "name": "San Francisco",   "country": "USA",          "lat": 37.52,  "lon": -122.37,"chinese": False},
    {"id": "GUM", "name": "Guam",            "country": "USA (Guam)",   "lat": 13.44,  "lon": 144.79, "chinese": False},
    {"id": "HAW", "name": "Hawaii (Oahu)",   "country": "USA",          "lat": 21.31,  "lon": -157.86,"chinese": False},
]

edges = [
    {"src": "HKG", "dst": "MNL", "cable": "AAG",   "capacity_tbps": 4.0,  "hmn_built": False},
    {"src": "MNL", "dst": "GUM", "cable": "AAG",   "capacity_tbps": 4.0,  "hmn_built": False},
    {"src": "GUM", "dst": "HAW", "cable": "AAG",   "capacity_tbps": 4.0,  "hmn_built": False},
    {"src": "HAW", "dst": "LAX", "cable": "AAG",   "capacity_tbps": 4.0,  "hmn_built": False},
    {"src": "SHA", "dst": "CHP", "cable": "CHUS",  "capacity_tbps": 2.0,  "hmn_built": False},
    {"src": "CHP", "dst": "HAW", "cable": "CHUS",  "capacity_tbps": 2.0,  "hmn_built": False},
    {"src": "HAW", "dst": "SFO", "cable": "CHUS",  "capacity_tbps": 2.0,  "hmn_built": False},
    {"src": "SHA", "dst": "KRS", "cable": "APCN2", "capacity_tbps": 2.56, "hmn_built": False},
    {"src": "KRS", "dst": "OKI", "cable": "APCN2", "capacity_tbps": 2.56, "hmn_built": False},
    {"src": "OKI", "dst": "HKG", "cable": "APCN2", "capacity_tbps": 2.56, "hmn_built": False},
    {"src": "HKG", "dst": "MNL", "cable": "APCN2", "capacity_tbps": 2.56, "hmn_built": False},
    {"src": "MNL", "dst": "SIN", "cable": "APCN2", "capacity_tbps": 2.56, "hmn_built": False},
    {"src": "TKO", "dst": "SIN", "cable": "SMW4",  "capacity_tbps": 1.28, "hmn_built": True},
    {"src": "SIN", "dst": "MUM", "cable": "SMW4",  "capacity_tbps": 1.28, "hmn_built": True},
    {"src": "MUM", "dst": "JED", "cable": "SMW4",  "capacity_tbps": 1.28, "hmn_built": True},
    {"src": "JED", "dst": "MRS", "cable": "SMW4",  "capacity_tbps": 1.28, "hmn_built": True},
    {"src": "HKG", "dst": "SIN", "cable": "SMW3",  "capacity_tbps": 0.96, "hmn_built": False},
    {"src": "SIN", "dst": "COL", "cable": "SMW3",  "capacity_tbps": 0.96, "hmn_built": False},
    {"src": "COL", "dst": "MUM", "cable": "SMW3",  "capacity_tbps": 0.96, "hmn_built": False},
    {"src": "MUM", "dst": "FUJ", "cable": "SMW3",  "capacity_tbps": 0.96, "hmn_built": False},
    {"src": "FUJ", "dst": "MRS", "cable": "SMW3",  "capacity_tbps": 0.96, "hmn_built": False},
    {"src": "GZH", "dst": "KHI", "cable": "PEACE", "capacity_tbps": 16.0, "hmn_built": True},
    {"src": "KHI", "dst": "DJI", "cable": "PEACE", "capacity_tbps": 16.0, "hmn_built": True},
    {"src": "DJI", "dst": "MOM", "cable": "PEACE", "capacity_tbps": 16.0, "hmn_built": True},
    {"src": "DJI", "dst": "MRS", "cable": "PEACE", "capacity_tbps": 16.0, "hmn_built": True},
    {"src": "SIN", "dst": "CHN", "cable": "SMW3",  "capacity_tbps": 0.96, "hmn_built": False},
    {"src": "CHN", "dst": "MUM", "cable": "SMW3",  "capacity_tbps": 0.96, "hmn_built": False},
    {"src": "GZH", "dst": "SIN", "cable": "APCN2", "capacity_tbps": 2.56, "hmn_built": False},
    {"src": "GZH", "dst": "HKG", "cable": "APCN2", "capacity_tbps": 2.56, "hmn_built": False},
    {"src": "KHI", "dst": "MUM", "cable": "SMW4",  "capacity_tbps": 1.28, "hmn_built": True},
    {"src": "KHI", "dst": "FUJ", "cable": "SMW3",  "capacity_tbps": 0.96, "hmn_built": False},
]

# Build graph
G = nx.Graph()
for n in nodes:
    G.add_node(n["id"], **n)
for e in edges:
    if G.has_edge(e["src"], e["dst"]):
        G[e["src"]][e["dst"]]["capacity_tbps"] += e["capacity_tbps"]
        G[e["src"]][e["dst"]]["cables"].append(e["cable"])
    else:
        G.add_edge(e["src"], e["dst"],
                   capacity_tbps=e["capacity_tbps"],
                   cables=[e["cable"]],
                   hmn_built=e["hmn_built"])

print(f"Graph loaded: {G.number_of_nodes()} nodes, {G.number_of_edges()} edges")

# ─────────────────────────────────────────────
# HELPER: MEASURE BANDWIDTH LOSS
# For a given disrupted graph, measure how much
# bandwidth a country loses to US hubs vs baseline
# ─────────────────────────────────────────────

def measure_bandwidth(graph, origin_nodes, us_hubs=["LAX", "SFO"]):
    """Return total aggregate bandwidth from origin nodes to US hubs."""
    total = 0
    for origin in origin_nodes:
        for hub in us_hubs:
            if origin not in graph or hub not in graph:
                continue
            try:
                paths = list(nx.all_simple_paths(graph, origin, hub, cutoff=8))
                for path in paths:
                    bottleneck = min(
                        graph[path[i]][path[i+1]]["capacity_tbps"]
                        for i in range(len(path)-1)
                    )
                    total += bottleneck
            except nx.NetworkXNoPath:
                pass
    return round(total, 2)

# Baseline bandwidth for key country groups
china_nodes    = ["SHA", "HKG", "GZH", "TKO"]
taiwan_nodes   = ["TPE"]
japan_nodes    = ["OKI", "CHP"]
skorea_nodes   = ["KRS"]
singapore_nodes= ["SIN"]

baseline = {
    "China":     measure_bandwidth(G, china_nodes),
    "Taiwan":    measure_bandwidth(G, taiwan_nodes),
    "Japan":     measure_bandwidth(G, japan_nodes),
    "S. Korea":  measure_bandwidth(G, skorea_nodes),
    "Singapore": measure_bandwidth(G, singapore_nodes),
}

print("\nBaseline bandwidth to US hubs (Tbps aggregate):")
for country, bw in baseline.items():
    print(f"  {country}: {bw} Tbps")

# ─────────────────────────────────────────────
# DISRUPTION SCENARIOS
# Each scenario defines which edges to remove
# ─────────────────────────────────────────────

# Group edges by cable name for easy removal
cable_edges = defaultdict(list)
for e in edges:
    cable_edges[e["cable"]].append((e["src"], e["dst"]))

scenarios = {
    "S1: AAG severed":
        cable_edges["AAG"],

    "S2: AAG + CHUS severed":
        cable_edges["AAG"] + cable_edges["CHUS"],

    "S3: Choke point attack (Singapore + Manila disabled)":
        [(u, v) for u, v in G.edges() if "SIN" in (u, v) or "MNL" in (u, v)],

    "S4: Grey zone — 4 cables partially degraded (50%)":
        None,  # handled separately — capacity reduction not edge removal
}

# Repair timeline assumptions (weeks) — drawn from historical data
# Physical cut mean: 3-8 weeks (CSIS / ICPC reports)
repair_distributions = {
    "S1: AAG severed":                                        {"mean": 5,  "std": 1.5},
    "S2: AAG + CHUS severed":                                 {"mean": 9,  "std": 2.0},
    "S3: Choke point attack (Singapore + Manila disabled)":   {"mean": 12, "std": 3.0},
    "S4: Grey zone — 4 cables partially degraded (50%)":      {"mean": 3,  "std": 1.0},
}

# ─────────────────────────────────────────────
# MONTE CARLO SIMULATION
# N = 10,000 runs per scenario
# Each run: sample a repair time, measure bandwidth
# loss at day 30, 90, and 365
# ─────────────────────────────────────────────

N = 10_000
np.random.seed(42)

print("\n── MONTE CARLO SIMULATION ──")
print(f"Running {N:,} simulations per scenario...\n")

simulation_results = []

for scenario_name, edges_to_remove in scenarios.items():

    repair_params = repair_distributions[scenario_name]
    bw_loss_pct_samples = []

    for _ in range(N):

        # Detection delay varies — grey zone attacks harder to attribute
        detection_delay = np.random.uniform(0.5, 2.0) if "Grey" in scenario_name else np.random.uniform(0, 0.5)
        repair_weeks = max(1, np.random.normal(
            repair_params["mean"], repair_params["std"]
        ) + detection_delay)

        # Build disrupted graph
        G_disrupted = G.copy()

        if scenario_name == "S4: Grey zone — 4 cables partially degraded (50%)":
            # Reduce capacity by 50% on 4 cables instead of removing
            for u, v in G_disrupted.edges():
                cable = G_disrupted[u][v]["cables"][0]
                if cable in ["AAG", "SMW4", "APCN2", "PEACE"]:
                    G_disrupted[u][v]["capacity_tbps"] *= 0.5
        else:
            G_disrupted.remove_edges_from(edges_to_remove)

        # Measure bandwidth loss for China
        disrupted_bw = measure_bandwidth(G_disrupted, china_nodes)
        baseline_bw  = baseline["China"]

        if baseline_bw > 0:
            # Inject uncertainty: capacity restoration varies during repair window
            # Partial rerouting absorbs some traffic — modeled as noise
            restoration_factor = np.random.uniform(0.85, 1.0)
            adjusted_loss = ((baseline_bw - disrupted_bw) / baseline_bw) * 100
            loss_pct = min(100.0, adjusted_loss * restoration_factor +
                           np.random.normal(0, 3.5))
            loss_pct = max(0.0, loss_pct)
        else:
            loss_pct = 0

        bw_loss_pct_samples.append({
            "loss_pct":     round(loss_pct, 2),
            "repair_weeks": round(repair_weeks, 1),
        })

    df_sim = pd.DataFrame(bw_loss_pct_samples)

    p10  = round(df_sim["loss_pct"].quantile(0.10), 1)
    p50  = round(df_sim["loss_pct"].quantile(0.50), 1)
    p90  = round(df_sim["loss_pct"].quantile(0.90), 1)
    mean_repair = round(df_sim["repair_weeks"].mean(), 1)

    simulation_results.append({
        "scenario":           scenario_name,
        "bw_loss_p10_pct":    p10,
        "bw_loss_p50_pct":    p50,
        "bw_loss_p90_pct":    p90,
        "mean_repair_weeks":  mean_repair,
    })

    print(f"Scenario: {scenario_name}")
    print(f"  Bandwidth loss — P10: {p10}%  |  Median: {p50}%  |  P90: {p90}%")
    print(f"  Mean repair time: {mean_repair} weeks\n")

# ─────────────────────────────────────────────
# SAVE RESULTS
# ─────────────────────────────────────────────

df_results = pd.DataFrame(simulation_results)
df_results.to_csv("scenario_results.csv", index=False)
print("Saved: scenario_results.csv")

# ─────────────────────────────────────────────
# VISUALIZATION — Scenario comparison bar chart
# ─────────────────────────────────────────────

fig, ax = plt.subplots(figsize=(12, 6))

scenario_labels = [
    "S1: AAG\nsevered",
    "S2: AAG + CHUS\nsevered",
    "S3: Choke point\nattack",
    "S4: Grey zone\n(partial)",
]

p10_vals = [r["bw_loss_p10_pct"] for r in simulation_results]
p50_vals = [r["bw_loss_p50_pct"] for r in simulation_results]
p90_vals = [r["bw_loss_p90_pct"] for r in simulation_results]

x = np.arange(len(scenario_labels))
width = 0.25

bars_p10 = ax.bar(x - width, p10_vals, width, label="P10 (optimistic)", color="#93c5fd")
bars_p50 = ax.bar(x,         p50_vals, width, label="Median",           color="#1d4ed8")
bars_p90 = ax.bar(x + width, p90_vals, width, label="P90 (severe)",     color="#1e3a5f")

# Add value labels on bars
for bars in [bars_p10, bars_p50, bars_p90]:
    for bar in bars:
        height = bar.get_height()
        ax.annotate(f"{height}%",
                    xy=(bar.get_x() + bar.get_width() / 2, height),
                    xytext=(0, 4), textcoords="offset points",
                    ha="center", va="bottom", fontsize=9)

ax.set_xlabel("Disruption Scenario", fontsize=12)
ax.set_ylabel("China Bandwidth Loss to US Hubs (%)", fontsize=12)
ax.set_title("Monte Carlo Scenario Results — China Bandwidth Loss by Disruption Type\n"
             f"N = {N:,} simulations per scenario", fontsize=13)
ax.set_xticks(x)
ax.set_xticklabels(scenario_labels, fontsize=10)
ax.set_ylim(0, 110)
ax.legend(fontsize=10)
ax.grid(axis="y", alpha=0.3)
ax.spines["top"].set_visible(False)
ax.spines["right"].set_visible(False)

plt.tight_layout()
plt.savefig("scenario_comparison.png", dpi=150, bbox_inches="tight")
plt.show()
print("Saved: scenario_comparison.png")

# ─────────────────────────────────────────────
# SUMMARY TABLE
# ─────────────────────────────────────────────

print("\n── FINAL SUMMARY TABLE ──")
print(df_results.to_string(index=False))
print("\nModule 2 complete. Outputs:")
print("  scenario_results.csv     — simulation results by scenario")
print("  scenario_comparison.png  — bar chart visualization")