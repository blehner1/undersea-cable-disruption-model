# Undersea Cable Disruption — Economic & Connectivity Impact Model

A four-module quantitative analytics framework modeling the strategic and 
economic consequences of undersea cable disruption in U.S.–China competition.

Extends independent qualitative research conducted during a National Maritime Intelligence-Integration Office internship.

---

## The Research Question

Undersea cables carry 95% of global internet traffic. Existing policy 
literature identifies which cables matter — but stops short of answering 
the operationally relevant questions:

- How much bandwidth does China lose under a specific disruption scenario?
- What is the GDP impact in dollars, and over what timeframe?
- Which nodes are true choke points?
- How does Chinese ownership amplify strategic risk?

This project answers all four.

---

## Key Findings

- **Singapore** is the world's highest-leverage neutral choke point 
  (betweenness centrality: 0.31) — 31% of all network paths pass through 
  a single city
- **100%** of Japan and South Korea's U.S.-bound internet paths route 
  through Chinese-affiliated infrastructure
- Severing just two cable systems (AAG + CHUS) produces a **92.5% median 
  bandwidth loss** for China over a 9.2-week repair window
- S2 scenario puts **$42.3B** of Chinese GDP at risk annually, with 
  **~$3B in allied collateral damage** over 90 days
- Djibouti — a Chinese-affiliated node — carries the highest capacity 
  in the network at 48 Tbps, placed strategically at the Horn of Africa

---

## Project Structure

| Module | File | Description |
|---|---|---|
| 1 | `module1_network_graph.py` | Cable network graph, centrality analysis, ownership concentration |
| 2 | `module2_scenario_engine.py` | Monte Carlo disruption simulation (N=10,000) |
| 3 | `module3_economic_impact.py` | GDP-at-risk model using World Bank elasticity |
| 4 | `module4_dashboard.py` | Interactive Plotly Dash dashboard |

---

## Scenarios Modeled

| Scenario | Median BW Loss | Repair Time |
|---|---|---|
| S1: AAG severed | 81.6% | 5.3 weeks |
| S2: AAG + CHUS severed | 92.5% | 9.2 weeks |
| S3: Choke point attack (Singapore + Manila) | 76.0% | 12.2 weeks |
| S4: Grey zone partial degradation | 29.9% | 4.2 weeks |

---

## Setup & Installation

```bash
pip3 install networkx pandas geopandas matplotlib folium
pip3 install dash plotly dash-bootstrap-components
```

Run modules in order:

```bash
python3 module1_network_graph.py
python3 module2_scenario_engine.py
python3 module3_economic_impact.py
python3 module4_dashboard.py
```

For the dashboard, open `http://127.0.0.1:8050` in your browser after 
running Module 4.

---

## Data Sources

- TeleGeography Submarine Cable Map — cable routes and landing stations
- UN Comtrade — bilateral trade flows
- World Bank WDI — GDP and internet penetration
- Qiang & Rossotto (2009) — internet-GDP elasticity coefficients
- CSIS, Atlantic Council, UNIDIR — repair timeline and threat assessments

---

## Methodology Note

GDP-at-risk estimates use linear elasticity coefficients and should be 
interpreted as conservative lower bounds. Non-linear effects including 
financial contagion, supply chain cascade, and investor confidence 
deterioration are not modeled and would increase real-world estimates.

---

## Author

**Bryce Lehner**
MS Business Analytics candidate, SMU Cox School of Business | BA Intelligence & Cyber Operations, USC
