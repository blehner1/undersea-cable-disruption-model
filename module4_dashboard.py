import dash
from dash import dcc, html, Input, Output, dash_table
import dash_bootstrap_components as dbc
import plotly.graph_objects as go
import plotly.express as px
import pandas as pd
import numpy as np

# ─────────────────────────────────────────────
# 1. DATA — pulled from Modules 1, 2, 3
# ─────────────────────────────────────────────

# Choke point index (Module 1)
choke_points = pd.DataFrame([
    {"name": "Singapore",      "country": "Singapore",    "chinese": False, "betweenness": 0.3128, "capacity_tbps": 10.56},
    {"name": "Manila",         "country": "Philippines",  "chinese": False, "betweenness": 0.2214, "capacity_tbps": 13.12},
    {"name": "Guam",           "country": "USA",          "chinese": False, "betweenness": 0.1881, "capacity_tbps": 8.00},
    {"name": "Mumbai",         "country": "India",        "chinese": False, "betweenness": 0.1858, "capacity_tbps": 6.72},
    {"name": "Hawaii",         "country": "USA",          "chinese": False, "betweenness": 0.1814, "capacity_tbps": 12.00},
    {"name": "Hong Kong",      "country": "China",        "chinese": True,  "betweenness": 0.1706, "capacity_tbps": 12.64},
    {"name": "Karachi",        "country": "Pakistan",     "chinese": True,  "betweenness": 0.1333, "capacity_tbps": 34.24},
    {"name": "Guangzhou",      "country": "China",        "chinese": True,  "betweenness": 0.1042, "capacity_tbps": 21.12},
    {"name": "Okinawa",        "country": "Japan",        "chinese": False, "betweenness": 0.0986, "capacity_tbps": 5.12},
    {"name": "Djibouti",       "country": "Djibouti",     "chinese": True,  "betweenness": 0.0733, "capacity_tbps": 48.00},
])

# Landing station coordinates
coords = {
    "Singapore": (1.35, 103.82),   "Manila": (14.60, 120.98),
    "Guam":      (13.44, 144.79),  "Mumbai": (19.08, 72.88),
    "Hawaii":    (21.31, -157.86), "Hong Kong": (22.30, 114.17),
    "Karachi":   (24.86, 67.01),   "Guangzhou": (23.13, 113.26),
    "Okinawa":   (26.33, 127.98),  "Djibouti":  (11.59, 43.14),
}
choke_points["lat"] = choke_points["name"].map(lambda x: coords[x][0])
choke_points["lon"] = choke_points["name"].map(lambda x: coords[x][1])

# Scenario results (Module 2)
scenario_results = pd.DataFrame([
    {"scenario": "S1: AAG severed",        "p10": 75.0, "p50": 81.6, "p90": 88.3, "repair_weeks": 5.3},
    {"scenario": "S2: AAG + CHUS severed", "p10": 85.3, "p50": 92.5, "p90": 99.7, "repair_weeks": 9.2},
    {"scenario": "S3: Choke point attack", "p10": 69.6, "p50": 76.0, "p90": 82.6, "repair_weeks": 12.2},
    {"scenario": "S4: Grey zone (partial)","p10": 25.2, "p50": 29.9, "p90": 34.7, "repair_weeks": 4.2},
])

# GDP-at-risk (Module 3) — China, median, all durations
gdp_china = pd.DataFrame([
    {"scenario": "S1: AAG severed",        "30 days": 3.07,  "90 days": 9.21,  "1 year": 37.35},
    {"scenario": "S2: AAG + CHUS severed", "30 days": 3.48,  "90 days": 10.44, "1 year": 42.34},
    {"scenario": "S3: Choke point attack", "30 days": 2.86,  "90 days": 8.58,  "1 year": 34.78},
    {"scenario": "S4: Grey zone (partial)","30 days": 1.12,  "90 days": 3.37,  "1 year": 13.68},
])

# Ownership concentration (Module 1)
ownership = pd.DataFrame([
    {"origin": "Japan",        "chinese_exposure_pct": 100.0},
    {"origin": "South Korea",  "chinese_exposure_pct": 100.0},
    {"origin": "Singapore",    "chinese_exposure_pct": 85.7},
    {"origin": "India",        "chinese_exposure_pct": 81.2},
    {"origin": "Philippines",  "chinese_exposure_pct": 66.7},
])

# Cable routes for map
cable_routes = [
    # AAG
    {"cable": "AAG", "lats": [22.30, 14.60, 13.44, 21.31, 33.93], "lons": [114.17, 120.98, 144.79, -157.86, -118.41], "color": "#f59e0b"},
    # CHUS
    {"cable": "CHUS", "lats": [31.23, 35.00, 21.31, 37.52], "lons": [121.47, 140.08, -157.86, -122.37], "color": "#f59e0b"},
    # SEA-ME-WE 4
    {"cable": "SEA-ME-WE 4", "lats": [22.32, 1.35, 19.08, 21.49, 43.30], "lons": [114.26, 103.82, 72.88, 39.19, 5.37], "color": "#34d399"},
    # SEA-ME-WE 3
    {"cable": "SEA-ME-WE 3", "lats": [22.30, 1.35, 6.93, 19.08, 25.12, 43.30], "lons": [114.17, 103.82, 79.85, 72.88, 56.34, 5.37], "color": "#34d399"},
    # PEACE
    {"cable": "PEACE", "lats": [23.13, 24.86, 11.59, -4.05], "lons": [113.26, 67.01, 43.14, 39.67], "color": "#f87171"},
    {"cable": "PEACE (Europe)", "lats": [11.59, 43.30], "lons": [43.14, 5.37], "color": "#f87171"},
    # APCN2
    {"cable": "APCN-2", "lats": [31.23, 35.10, 26.33, 22.30, 14.60, 1.35], "lons": [121.47, 129.03, 127.98, 114.17, 120.98, 103.82], "color": "#a78bfa"},
]

# ─────────────────────────────────────────────
# 2. APP SETUP
# ─────────────────────────────────────────────

app = dash.Dash(__name__, external_stylesheets=[dbc.themes.FLATLY])
app.title = "Undersea Cable Disruption — Strategic Risk Dashboard"

NAVY  = "#0f2942"
LIGHT = "#f8fafc"
CARD  = "#ffffff"

# ─────────────────────────────────────────────
# 3. HELPER: BUILD GLOBAL CABLE MAP
# ─────────────────────────────────────────────

def build_map(highlight_scenario=None):
    fig = go.Figure()

    # Draw cable routes
    for route in cable_routes:
        fig.add_trace(go.Scattergeo(
            lat=route["lats"], lon=route["lons"],
            mode="lines",
            line=dict(width=2, color=route["color"]),
            name=route["cable"],
            hoverinfo="name",
            showlegend=True,
        ))

    # Draw landing stations
    for _, row in choke_points.iterrows():
        color  = "#ef4444" if row["chinese"] else "#3b82f6"
        size   = 10 + (row["betweenness"] * 60)
        label  = "Chinese-affiliated" if row["chinese"] else "Neutral"
        fig.add_trace(go.Scattergeo(
            lat=[row["lat"]], lon=[row["lon"]],
            mode="markers+text",
            marker=dict(size=size, color=color, opacity=0.85,
                        line=dict(width=1, color="white")),
            text=row["name"],
            textposition="top center",
            textfont=dict(size=9, color="white"),
            name=f"{row['name']} ({label})",
            hovertemplate=(
                f"<b>{row['name']}</b><br>"
                f"Country: {row['country']}<br>"
                f"Chinese affiliated: {row['chinese']}<br>"
                f"Betweenness centrality: {row['betweenness']}<br>"
                f"Capacity: {row['capacity_tbps']} Tbps"
                "<extra></extra>"
            ),
            showlegend=False,
        ))

    fig.update_layout(
        geo=dict(
            showland=True, landcolor="#1e293b",
            showocean=True, oceancolor="#0c1a2e",
            showcoastlines=True, coastlinecolor="#334155",
            showcountries=True, countrycolor="#334155",
            projection_type="natural earth",
            bgcolor="#0c1a2e",
        ),
        paper_bgcolor="#0c1a2e",
        plot_bgcolor="#0c1a2e",
        margin=dict(l=0, r=0, t=0, b=0),
        height=480,
        legend=dict(
            bgcolor="rgba(15,41,66,0.8)",
            font=dict(color="white", size=10),
            x=0.01, y=0.99,
        ),
        showlegend=True,
    )
    return fig

# ─────────────────────────────────────────────
# 4. LAYOUT
# ─────────────────────────────────────────────

app.layout = dbc.Container([

    # Header
    dbc.Row([
        dbc.Col([
            html.H2("Undersea Cable Disruption — Strategic Risk Dashboard",
                    style={"color": "white", "marginBottom": "4px", "fontWeight": "600"}),
            html.P("Quantitative impact model | U.S.–China strategic competition | Cox MBAn Portfolio Project",
                   style={"color": "#94a3b8", "fontSize": "13px", "marginBottom": "0"}),
        ])
    ], style={"backgroundColor": NAVY, "padding": "20px 24px 16px"}),

    # KPI cards
    dbc.Row([
        dbc.Col(dbc.Card([
            dbc.CardBody([
                html.P("S2 China bandwidth loss", className="text-muted",
                       style={"fontSize": "12px", "marginBottom": "4px"}),
                html.H4("92.5%", style={"fontWeight": "700", "color": "#ef4444", "marginBottom": "2px"}),
                html.P("median | AAG + CHUS severed", style={"fontSize": "11px", "color": "#94a3b8", "marginBottom": "0"}),
            ])
        ], style={"borderLeft": "4px solid #ef4444", "borderRadius": "8px"}), md=3),

        dbc.Col(dbc.Card([
            dbc.CardBody([
                html.P("China GDP-at-risk (S2, 1 year)", className="text-muted",
                       style={"fontSize": "12px", "marginBottom": "4px"}),
                html.H4("$42.3B", style={"fontWeight": "700", "color": "#f59e0b", "marginBottom": "2px"}),
                html.P("median estimate", style={"fontSize": "11px", "color": "#94a3b8", "marginBottom": "0"}),
            ])
        ], style={"borderLeft": "4px solid #f59e0b", "borderRadius": "8px"}), md=3),

        dbc.Col(dbc.Card([
            dbc.CardBody([
                html.P("Top choke point", className="text-muted",
                       style={"fontSize": "12px", "marginBottom": "4px"}),
                html.H4("Singapore", style={"fontWeight": "700", "color": "#3b82f6", "marginBottom": "2px"}),
                html.P("betweenness centrality: 0.31", style={"fontSize": "11px", "color": "#94a3b8", "marginBottom": "0"}),
            ])
        ], style={"borderLeft": "4px solid #3b82f6", "borderRadius": "8px"}), md=3),

        dbc.Col(dbc.Card([
            dbc.CardBody([
                html.P("Japan/S.Korea ownership exposure", className="text-muted",
                       style={"fontSize": "12px", "marginBottom": "4px"}),
                html.H4("100%", style={"fontWeight": "700", "color": "#a78bfa", "marginBottom": "2px"}),
                html.P("of US-bound paths via Chinese node", style={"fontSize": "11px", "color": "#94a3b8", "marginBottom": "0"}),
            ])
        ], style={"borderLeft": "4px solid #a78bfa", "borderRadius": "8px"}), md=3),
    ], style={"padding": "16px 24px", "backgroundColor": "#f8fafc", "gap": "0"}),

    # Map + choke point table
    dbc.Row([
        dbc.Col([
            dbc.Card([
                dbc.CardHeader(html.B("Global Cable Network — Landing Station Risk Map",
                                      style={"fontSize": "13px"})),
                dbc.CardBody([
                    html.P("Node size = betweenness centrality  |  Red = Chinese-affiliated  |  Blue = Neutral",
                           style={"fontSize": "11px", "color": "#64748b", "marginBottom": "8px"}),
                    dcc.Graph(id="cable-map", figure=build_map(),
                              config={"displayModeBar": False}),
                ])
            ], style={"borderRadius": "8px"}),
        ], md=8),

        dbc.Col([
            dbc.Card([
                dbc.CardHeader(html.B("Choke Point Index", style={"fontSize": "13px"})),
                dbc.CardBody([
                    dash_table.DataTable(
                        data=choke_points[["name", "country", "chinese",
                                           "betweenness", "capacity_tbps"]].to_dict("records"),
                        columns=[
                            {"name": "Station",     "id": "name"},
                            {"name": "Country",     "id": "country"},
                            {"name": "CN affil.",   "id": "chinese"},
                            {"name": "Centrality",  "id": "betweenness"},
                            {"name": "Tbps",        "id": "capacity_tbps"},
                        ],
                        style_table={"overflowX": "auto", "fontSize": "12px"},
                        style_header={"backgroundColor": "#0f2942", "color": "white",
                                      "fontWeight": "600", "fontSize": "11px"},
                        style_data_conditional=[
                            {"if": {"filter_query": "{chinese} = True"},
                             "backgroundColor": "#fef2f2", "color": "#991b1b"},
                            {"if": {"row_index": "odd"},
                             "backgroundColor": "#f8fafc"},
                        ],
                        style_cell={"padding": "6px 10px", "textAlign": "left"},
                        page_size=10,
                    ),
                    html.P("Red rows = Chinese-affiliated stations",
                           style={"fontSize": "10px", "color": "#94a3b8",
                                  "marginTop": "8px", "marginBottom": "0"}),
                ])
            ], style={"borderRadius": "8px", "height": "100%"}),
        ], md=4),
    ], style={"padding": "0 24px 16px"}),

    # Scenario selector + charts
    dbc.Row([
        dbc.Col([
            dbc.Card([
                dbc.CardHeader(html.B("Scenario Analysis — Bandwidth Loss & GDP Impact",
                                      style={"fontSize": "13px"})),
                dbc.CardBody([
                    dbc.Row([
                        dbc.Col([
                            html.Label("Select scenario:", style={"fontSize": "12px", "fontWeight": "600"}),
                            dcc.Dropdown(
                                id="scenario-dropdown",
                                options=[{"label": s, "value": s}
                                         for s in scenario_results["scenario"]],
                                value="S2: AAG + CHUS severed",
                                clearable=False,
                                style={"fontSize": "12px"},
                            ),
                        ], md=5),
                        dbc.Col([
                            html.Label("GDP impact duration:", style={"fontSize": "12px", "fontWeight": "600"}),
                            dcc.RadioItems(
                                id="duration-radio",
                                options=[
                                    {"label": " 30 days", "value": "30 days"},
                                    {"label": " 90 days", "value": "90 days"},
                                    {"label": " 1 year",  "value": "1 year"},
                                ],
                                value="90 days",
                                inline=True,
                                style={"fontSize": "12px", "marginTop": "6px"},
                            ),
                        ], md=5),
                    ]),

                    dbc.Row([
                        dbc.Col(dcc.Graph(id="bw-loss-chart",
                                          config={"displayModeBar": False}), md=6),
                        dbc.Col(dcc.Graph(id="gdp-risk-chart",
                                          config={"displayModeBar": False}), md=6),
                    ], style={"marginTop": "12px"}),
                ])
            ], style={"borderRadius": "8px"}),
        ], md=12),
    ], style={"padding": "0 24px 16px"}),

    # Ownership concentration
    dbc.Row([
        dbc.Col([
            dbc.Card([
                dbc.CardHeader(html.B("Chinese Ownership Exposure — % of US-Bound Paths via Chinese Node",
                                      style={"fontSize": "13px"})),
                dbc.CardBody([
                    dcc.Graph(id="ownership-chart",
                              figure=px.bar(
                                  ownership.sort_values("chinese_exposure_pct"),
                                  x="chinese_exposure_pct", y="origin",
                                  orientation="h",
                                  color="chinese_exposure_pct",
                                  color_continuous_scale=["#3b82f6", "#f59e0b", "#ef4444"],
                                  labels={"chinese_exposure_pct": "% paths via Chinese node",
                                          "origin": "Nation"},
                                  text="chinese_exposure_pct",
                              ).update_traces(
                                  texttemplate="%{text}%", textposition="outside"
                              ).update_layout(
                                  height=260,
                                  margin=dict(l=10, r=40, t=10, b=10),
                                  coloraxis_showscale=False,
                                  paper_bgcolor="white",
                                  plot_bgcolor="white",
                                  xaxis=dict(range=[0, 115], showgrid=True,
                                             gridcolor="#f1f5f9"),
                              ),
                              config={"displayModeBar": False}),
                    html.P("Source: Module 1 network graph — all_simple_paths analysis",
                           style={"fontSize": "10px", "color": "#94a3b8", "marginBottom": "0"}),
                ])
            ], style={"borderRadius": "8px"}),
        ], md=12),
    ], style={"padding": "0 24px 16px"}),

    # Footer
    dbc.Row([
        dbc.Col([
            html.P("Bryce Lehner | Cox School of Business MBAn | Naval Intelligence Research Background | May 2026",
                   style={"fontSize": "11px", "color": "#94a3b8",
                          "textAlign": "center", "marginBottom": "0"}),
        ])
    ], style={"backgroundColor": NAVY, "padding": "12px 24px"}),

], fluid=True, style={"padding": "0", "backgroundColor": "#f8fafc"})

# ─────────────────────────────────────────────
# 5. CALLBACKS — interactive scenario updates
# ─────────────────────────────────────────────

@app.callback(
    Output("bw-loss-chart", "figure"),
    Output("gdp-risk-chart", "figure"),
    Input("scenario-dropdown", "value"),
    Input("duration-radio", "value"),
)
def update_charts(selected_scenario, selected_duration):

    # ── Bandwidth loss chart ──
    row = scenario_results[scenario_results["scenario"] == selected_scenario].iloc[0]

    bw_fig = go.Figure()
    bw_fig.add_trace(go.Bar(
        x=["P10 (optimistic)", "Median", "P90 (severe)"],
        y=[row["p10"], row["p50"], row["p90"]],
        marker_color=["#93c5fd", "#1d4ed8", "#1e3a5f"],
        text=[f"{v}%" for v in [row["p10"], row["p50"], row["p90"]]],
        textposition="outside",
    ))
    bw_fig.update_layout(
        title=dict(text=f"China Bandwidth Loss<br><sup>{selected_scenario}</sup>",
                   font=dict(size=12)),
        yaxis=dict(range=[0, 115], title="Bandwidth loss (%)",
                   gridcolor="#f1f5f9"),
        xaxis=dict(title=""),
        height=280,
        margin=dict(l=10, r=10, t=50, b=10),
        paper_bgcolor="white", plot_bgcolor="white",
        showlegend=False,
    )
    bw_fig.add_annotation(
        text=f"Repair time: ~{row['repair_weeks']} weeks",
        xref="paper", yref="paper", x=0.98, y=0.98,
        showarrow=False, font=dict(size=10, color="#64748b"),
        align="right",
    )

    # ── GDP-at-risk chart ──
    gdp_row = gdp_china[gdp_china["scenario"] == selected_scenario].iloc[0]
    gdp_val = gdp_row[selected_duration]

    all_scenarios = gdp_china["scenario"].tolist()
    all_vals      = [gdp_china[gdp_china["scenario"] == s].iloc[0][selected_duration]
                     for s in all_scenarios]
    bar_colors    = ["#ef4444" if s == selected_scenario else "#93c5fd"
                     for s in all_scenarios]

    gdp_fig = go.Figure()
    gdp_fig.add_trace(go.Bar(
        x=["S1", "S2", "S3", "S4"],
        y=all_vals,
        marker_color=bar_colors,
        text=[f"${v}B" for v in all_vals],
        textposition="outside",
    ))
    gdp_fig.update_layout(
        title=dict(text=f"China GDP-at-Risk ({selected_duration})<br>"
                        f"<sup>Selected: {selected_scenario} = ${gdp_val}B</sup>",
                   font=dict(size=12)),
        yaxis=dict(title="GDP-at-risk (USD Billions)", gridcolor="#f1f5f9"),
        xaxis=dict(title="Scenario"),
        height=280,
        margin=dict(l=10, r=10, t=50, b=10),
        paper_bgcolor="white", plot_bgcolor="white",
        showlegend=False,
    )

    return bw_fig, gdp_fig

# ─────────────────────────────────────────────
# 6. RUN
# ─────────────────────────────────────────────

if __name__ == "__main__":
    app.run(debug=True)