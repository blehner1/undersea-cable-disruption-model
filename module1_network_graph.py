import networkx as nx
import pandas as pd
import matplotlib.pyplot as plt
import folium
import json

# ─────────────────────────────────────────────
# 1. BUILD THE LANDING STATION NODE LIST
#    (seeded from your Naval Intelligence report)
#    Format: id, name, country, lat, lon, chinese_affiliated
# ─────────────────────────────────────────────

nodes = [
    # East Asia
    {"id": "SHA", "name": "Shanghai",        "country": "China",        "lat": 31.23,  "lon": 121.47, "chinese": True},
    {"id": "HKG", "name": "Hong Kong",       "country": "China",        "lat": 22.30,  "lon": 114.17, "chinese": True},
    {"id": "GZH", "name": "Guangzhou",       "country": "China",        "lat": 23.13,  "lon": 113.26, "chinese": True},
    {"id": "TPE", "name": "Taipei",          "country": "Taiwan",       "lat": 25.03,  "lon": 121.56, "chinese": False},
    {"id": "TKO", "name": "Tseung Kwan O",   "country": "Hong Kong",    "lat": 22.32,  "lon": 114.26, "chinese": True},
    {"id": "KRS", "name": "Keoje (Busan)",   "country": "South Korea",  "lat": 35.10,  "lon": 129.03, "chinese": False},
    {"id": "OKI", "name": "Okinawa",         "country": "Japan",        "lat": 26.33,  "lon": 127.98, "chinese": False},
    {"id": "CHP", "name": "Chikura",         "country": "Japan",        "lat": 35.00,  "lon": 140.08, "chinese": False},

    # Southeast Asia (choke points)
    {"id": "SIN", "name": "Singapore",       "country": "Singapore",    "lat": 1.35,   "lon": 103.82, "chinese": False},
    {"id": "BKK", "name": "Satun (Bangkok)", "country": "Thailand",     "lat": 6.62,   "lon": 100.07, "chinese": False},
    {"id": "MNL", "name": "Manila",          "country": "Philippines",  "lat": 14.60,  "lon": 120.98, "chinese": False},
    {"id": "JKT", "name": "Jakarta",         "country": "Indonesia",    "lat": -6.21,  "lon": 106.85, "chinese": False},

    # South Asia / Indian Ocean
    {"id": "MUM", "name": "Mumbai",          "country": "India",        "lat": 19.08,  "lon": 72.88,  "chinese": False},
    {"id": "CHN", "name": "Chennai",         "country": "India",        "lat": 13.08,  "lon": 80.27,  "chinese": False},
    {"id": "COL", "name": "Colombo",         "country": "Sri Lanka",    "lat": 6.93,   "lon": 79.85,  "chinese": False},
    {"id": "DJI", "name": "Djibouti",        "country": "Djibouti",     "lat": 11.59,  "lon": 43.14,  "chinese": True},  # PEACE cable hub
    {"id": "KHI", "name": "Karachi",         "country": "Pakistan",     "lat": 24.86,  "lon": 67.01,  "chinese": True},  # PEACE cable

    # Middle East
    {"id": "JED", "name": "Jeddah",          "country": "Saudi Arabia", "lat": 21.49,  "lon": 39.19,  "chinese": False},
    {"id": "FUJ", "name": "Fujairah",        "country": "UAE",          "lat": 25.12,  "lon": 56.34,  "chinese": False},

    # Europe
    {"id": "MRS", "name": "Marseille",       "country": "France",       "lat": 43.30,  "lon": 5.37,   "chinese": False},
    {"id": "PTE", "name": "Portunus (UK)",   "country": "UK",           "lat": 51.50,  "lon": -0.90,  "chinese": False},

    # Africa
    {"id": "MOM", "name": "Mombasa",         "country": "Kenya",        "lat": -4.05,  "lon": 39.67,  "chinese": False},

    # Pacific / North America
    {"id": "LAX", "name": "Los Angeles",     "country": "USA",          "lat": 33.93,  "lon": -118.41,"chinese": False},
    {"id": "SFO", "name": "San Francisco",   "country": "USA",          "lat": 37.52,  "lon": -122.37,"chinese": False},
    {"id": "GUM", "name": "Guam",            "country": "USA (Guam)",   "lat": 13.44,  "lon": 144.79, "chinese": False},
    {"id": "HAW", "name": "Hawaii (Oahu)",   "country": "USA",          "lat": 21.31,  "lon": -157.86,"chinese": False},
]

# ─────────────────────────────────────────────
# 2. BUILD THE CABLE EDGE LIST
#    Each edge = one cable segment between two landing stations
#    capacity_tbps: approximate — update with TeleGeography data
#    cable: cable system name from your report
# ─────────────────────────────────────────────

edges = [
    # Asia-America Gateway (AAG) — China to US via Pacific
    {"src": "HKG", "dst": "MNL", "cable": "AAG", "capacity_tbps": 4.0,  "hmn_built": False},
    {"src": "MNL", "dst": "GUM", "cable": "AAG", "capacity_tbps": 4.0,  "hmn_built": False},
    {"src": "GUM", "dst": "HAW", "cable": "AAG", "capacity_tbps": 4.0,  "hmn_built": False},
    {"src": "HAW", "dst": "LAX", "cable": "AAG", "capacity_tbps": 4.0,  "hmn_built": False},

    # China-US Cable Network (CHUS)
    {"src": "SHA", "dst": "CHP", "cable": "CHUS", "capacity_tbps": 2.0, "hmn_built": False},
    {"src": "CHP", "dst": "HAW", "cable": "CHUS", "capacity_tbps": 2.0, "hmn_built": False},
    {"src": "HAW", "dst": "SFO", "cable": "CHUS", "capacity_tbps": 2.0, "hmn_built": False},

    # APCN-2 (Asia-Pacific Cable Network) — regional Asia loop
    {"src": "SHA", "dst": "KRS", "cable": "APCN2", "capacity_tbps": 2.56,"hmn_built": False},
    {"src": "KRS", "dst": "OKI", "cable": "APCN2", "capacity_tbps": 2.56,"hmn_built": False},
    {"src": "OKI", "dst": "HKG", "cable": "APCN2", "capacity_tbps": 2.56,"hmn_built": False},
    {"src": "HKG", "dst": "MNL", "cable": "APCN2", "capacity_tbps": 2.56,"hmn_built": False},
    {"src": "MNL", "dst": "SIN", "cable": "APCN2", "capacity_tbps": 2.56,"hmn_built": False},

    # SEA-ME-WE 4 — China/Asia to Europe via Indian Ocean
    {"src": "TKO", "dst": "SIN", "cable": "SMW4", "capacity_tbps": 1.28, "hmn_built": True},
    {"src": "SIN", "dst": "MUM", "cable": "SMW4", "capacity_tbps": 1.28, "hmn_built": True},
    {"src": "MUM", "dst": "JED", "cable": "SMW4", "capacity_tbps": 1.28, "hmn_built": True},
    {"src": "JED", "dst": "MRS", "cable": "SMW4", "capacity_tbps": 1.28, "hmn_built": True},

    # SEA-ME-WE 3 — older parallel route
    {"src": "HKG", "dst": "SIN", "cable": "SMW3", "capacity_tbps": 0.96, "hmn_built": False},
    {"src": "SIN", "dst": "COL", "cable": "SMW3", "capacity_tbps": 0.96, "hmn_built": False},
    {"src": "COL", "dst": "MUM", "cable": "SMW3", "capacity_tbps": 0.96, "hmn_built": False},
    {"src": "MUM", "dst": "FUJ", "cable": "SMW3", "capacity_tbps": 0.96, "hmn_built": False},
    {"src": "FUJ", "dst": "MRS", "cable": "SMW3", "capacity_tbps": 0.96, "hmn_built": False},

    # PEACE Cable (Digital Silk Road) — China to Europe via Pakistan/Djibouti
    {"src": "GZH", "dst": "KHI", "cable": "PEACE", "capacity_tbps": 16.0, "hmn_built": True},
    {"src": "KHI", "dst": "DJI", "cable": "PEACE", "capacity_tbps": 16.0, "hmn_built": True},
    {"src": "DJI", "dst": "MOM", "cable": "PEACE", "capacity_tbps": 16.0, "hmn_built": True},
    {"src": "DJI", "dst": "MRS", "cable": "PEACE", "capacity_tbps": 16.0, "hmn_built": True},

 # Intra-Asia connectivity
    {"src": "SIN", "dst": "CHN", "cable": "SMW3", "capacity_tbps": 0.96, "hmn_built": False},
    {"src": "CHN", "dst": "MUM", "cable": "SMW3", "capacity_tbps": 0.96, "hmn_built": False},

    # Guangzhou connections (was missing — fix)
    {"src": "GZH", "dst": "SIN", "cable": "APCN2", "capacity_tbps": 2.56, "hmn_built": False},
    {"src": "GZH", "dst": "HKG", "cable": "APCN2", "capacity_tbps": 2.56, "hmn_built": False},

    # Karachi connections (was missing — fix)
    {"src": "KHI", "dst": "MUM", "cable": "SMW4", "capacity_tbps": 1.28, "hmn_built": True},
    {"src": "KHI", "dst": "FUJ", "cable": "SMW3", "capacity_tbps": 0.96, "hmn_built": False},
]

# ─────────────────────────────────────────────
# 3. CONSTRUCT THE NETWORKX GRAPH
# ─────────────────────────────────────────────

G = nx.Graph()

# Add nodes with attributes
for n in nodes:
    G.add_node(
        n["id"],
        name=n["name"],
        country=n["country"],
        lat=n["lat"],
        lon=n["lon"],
        chinese=n["chinese"]
    )

# Add edges with attributes
for e in edges:
    # If edge already exists, add capacity (parallel cables)
    if G.has_edge(e["src"], e["dst"]):
        G[e["src"]][e["dst"]]["capacity_tbps"] += e["capacity_tbps"]
        G[e["src"]][e["dst"]]["cables"].append(e["cable"])
    else:
        G.add_edge(
            e["src"], e["dst"],
            capacity_tbps=e["capacity_tbps"],
            cables=[e["cable"]],
            hmn_built=e["hmn_built"]
        )

print(f"Graph built: {G.number_of_nodes()} nodes, {G.number_of_edges()} edges")

# ─────────────────────────────────────────────
# 4. COMPUTE CENTRALITY METRICS
# ─────────────────────────────────────────────

# Betweenness centrality — identifies choke points
# weight=None treats all edges equally (connectivity focus)
betweenness = nx.betweenness_centrality(G, normalized=True)

# Degree centrality — how many direct connections
degree = nx.degree_centrality(G)

# Build results dataframe
node_attrs = {n["id"]: n for n in nodes}

results = []
for node_id in G.nodes():
    attrs = node_attrs[node_id]
    results.append({
        "id": node_id,
        "name": attrs["name"],
        "country": attrs["country"],
        "chinese_affiliated": attrs["chinese"],
        "betweenness_centrality": round(betweenness[node_id], 4),
        "degree_centrality": round(degree[node_id], 4),
        "num_connections": G.degree(node_id),
        "total_capacity_tbps": round(
            sum(G[node_id][nb]["capacity_tbps"] for nb in G.neighbors(node_id)), 2
        ),
    })

df = pd.DataFrame(results).sort_values("betweenness_centrality", ascending=False)

print("\n── CHOKE POINT INDEX (Top 10 by Betweenness Centrality) ──")
print(df[["name", "country", "chinese_affiliated",
          "betweenness_centrality", "total_capacity_tbps"]].head(10).to_string(index=False))

df.to_csv("choke_point_index.csv", index=False)
print("\nSaved: choke_point_index.csv")

# ─────────────────────────────────────────────
# 5. BANDWIDTH REDUNDANCY PER COUNTRY
#    How many independent paths does each country have
#    to reach US internet hubs (LAX, SFO)?
# ─────────────────────────────────────────────

us_hubs = ["LAX", "SFO"]
china_nodes = [n for n in G.nodes() if G.nodes[n]["chinese"]]

print("\n── BANDWIDTH REDUNDANCY: China landing stations → US hubs ──")
for cn in china_nodes:
    for hub in us_hubs:
        try:
            paths = list(nx.all_simple_paths(G, cn, hub, cutoff=8))
            total_bw = sum(
                min(G[path[i]][path[i+1]]["capacity_tbps"] for i in range(len(path)-1))
                for path in paths
            )
            print(f"  {G.nodes[cn]['name']} → {G.nodes[hub]['name']}: "
                  f"{len(paths)} paths, ~{round(total_bw, 2)} Tbps aggregate capacity")
        except nx.NetworkXNoPath:
            print(f"  {G.nodes[cn]['name']} → {G.nodes[hub]['name']}: NO PATH")

# ─────────────────────────────────────────────
# 6. SIMULATE A SINGLE CABLE DISRUPTION
#    Scenario 1: AAG severed — remove all AAG edges
#    Measure: which nodes become disconnected or lose paths to US
# ─────────────────────────────────────────────

print("\n── SCENARIO 1: AAG Cable Severed ──")

G_scenario = G.copy()

# Remove all AAG edges
aag_edges = [(e["src"], e["dst"]) for e in edges if e["cable"] == "AAG"]
G_scenario.remove_edges_from(aag_edges)

print(f"Removed {len(aag_edges)} AAG segments")
print(f"Graph still connected: {nx.is_connected(G_scenario)}")

# Recompute betweenness on disrupted graph
bc_disrupted = nx.betweenness_centrality(G_scenario, normalized=True)

print("\nChoke point shifts after AAG removal (top 5):")
shifted = sorted(
    [(n, bc_disrupted[n] - betweenness[n]) for n in G.nodes()],
    key=lambda x: x[1], reverse=True
)[:5]
for node_id, delta in shifted:
    print(f"  {G.nodes[node_id]['name']} ({node_id}): "
          f"centrality +{round(delta, 4)} (now {round(bc_disrupted[node_id], 4)})")

# ─────────────────────────────────────────────
# 7. FOLIUM MAP — Interactive cable network
# ─────────────────────────────────────────────

m = folium.Map(location=[20, 110], zoom_start=3, tiles="CartoDB dark_matter")

# Color nodes: red = Chinese-affiliated, blue = neutral
for node_id, attrs in G.nodes(data=True):
    color = "#ef4444" if attrs["chinese"] else "#3b82f6"
    bc_score = betweenness[node_id]
    radius = 6 + (bc_score * 60)  # scale dot size by centrality

    folium.CircleMarker(
        location=[attrs["lat"], attrs["lon"]],
        radius=radius,
        color=color,
        fill=True,
        fill_opacity=0.8,
        popup=folium.Popup(
            f"<b>{attrs['name']}</b><br>"
            f"Country: {attrs['country']}<br>"
            f"Chinese affiliated: {attrs['chinese']}<br>"
            f"Betweenness centrality: {round(bc_score, 4)}<br>"
            f"Connections: {G.degree(node_id)}",
            max_width=200
        )
    ).add_to(m)

# Draw cable edges
cable_colors = {
    "AAG":   "#f59e0b",
    "CHUS":  "#f59e0b",
    "APCN2": "#a78bfa",
    "SMW4":  "#34d399",
    "SMW3":  "#34d399",
    "PEACE": "#f87171",
}

for src, dst, data in G.edges(data=True):
    src_attrs = G.nodes[src]
    dst_attrs = G.nodes[dst]
    # Use color of first cable on this edge
    cable_name = data["cables"][0]
    color = cable_colors.get(cable_name, "#94a3b8")

    folium.PolyLine(
        locations=[
            [src_attrs["lat"], src_attrs["lon"]],
            [dst_attrs["lat"], dst_attrs["lon"]]
        ],
        color=color,
        weight=1.5 + (data["capacity_tbps"] / 4),
        opacity=0.7,
        tooltip=f"{', '.join(data['cables'])} — {data['capacity_tbps']} Tbps"
    ).add_to(m)

m.save("cable_network_map.html")
# ─────────────────────────────────────────────
# 8. OWNERSHIP CONCENTRATION SCORE
#    For each non-Chinese country, what % of its
#    paths to US hubs pass through a Chinese-affiliated node?
# ─────────────────────────────────────────────

print("\n── OWNERSHIP CONCENTRATION SCORE ──")
print("% of bandwidth paths to US that pass through a Chinese-affiliated node\n")

# Identify Chinese-affiliated node IDs
chinese_nodes = {n for n in G.nodes() if G.nodes[n]["chinese"]}

# Countries to analyze — focus on key nations
target_nodes = {
    "TPE": "Taiwan",
    "SIN": "Singapore",
    "MNL": "Philippines",
    "OKI": "Japan (Okinawa)",
    "KRS": "South Korea",
    "MUM": "India (Mumbai)",
    "JKT": "Indonesia",
}

us_hubs = ["LAX", "SFO"]

concentration_results = []

for node_id, label in target_nodes.items():
    for hub in us_hubs:
        try:
            paths = list(nx.all_simple_paths(G, node_id, hub, cutoff=8))
            if not paths:
                continue

            paths_through_chinese = sum(
                1 for path in paths
                if any(step in chinese_nodes for step in path[1:-1])
            )

            pct = round((paths_through_chinese / len(paths)) * 100, 1)

            concentration_results.append({
                "origin": label,
                "destination": G.nodes[hub]["name"],
                "total_paths": len(paths),
                "paths_via_chinese_node": paths_through_chinese,
                "chinese_exposure_pct": pct
            })

        except nx.NetworkXNoPath:
            pass

df_concentration = pd.DataFrame(concentration_results)
print(df_concentration.to_string(index=False))
df_concentration.to_csv("ownership_concentration.csv", index=False)
print("\nSaved: ownership_concentration.csv")
print("\nSaved: cable_network_map.html — open in your browser")
print("\nModule 1 complete. Outputs:")
print("  choke_point_index.csv  — ranked landing stations by strategic importance")
print("  cable_network_map.html — interactive map with cable routes and node centrality")