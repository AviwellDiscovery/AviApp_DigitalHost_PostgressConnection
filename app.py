from __future__ import annotations

import os
from dotenv import load_dotenv
load_dotenv()

import pandas as pd
import dash
from dash import html, dcc, Input, Output, State, dash_table
import dash_bootstrap_components as dbc
import dash_cytoscape as cyto

from config import (
    TISSUES, DEFAULT_TOPK, DEFAULT_KN, DEFAULT_ABS_THR, DEFAULT_ACC_MIN,
    DEFAULT_CORR_MIN, DEFAULT_CORR_MAX
)
from router import table_for
from repo import fetch_seed_candidates
from graph_engine import build_graph, BuildParams
from viz import BASE_STYLE, LAYOUTS, to_cytoscape_elements, apply_focus, build_legend
from logger import LOG_PATH


app = dash.Dash(__name__, external_stylesheets=[dbc.themes.FLATLY])
app.title = "Multi-Omics Monotone Graph Explorer"

# -----------------------------
# Global centered overlay loader
# -----------------------------
OVERLAY_ON = {
    "display": "flex",
    "position": "fixed",
    "top": 0, "left": 0, "right": 0, "bottom": 0,
    "background": "rgba(255,255,255,0.65)",
    "zIndex": 9999,
    "alignItems": "center",
    "justifyContent": "center",
    "flexDirection": "column",
}
OVERLAY_OFF = {"display": "none"}

MAX_TABLE_ROWS = 1000
MAX_SEEDS_LOAD = 10000


app.layout = dbc.Container(fluid=True, children=[
    dbc.NavbarSimple(
        brand="Multi-Omics Monotone Graph Explorer (Dash Cytoscape + PostgreSQL)",
        color="primary",
        dark=True
    ),

    # Global overlay (seed loading + graph building)
    html.Div(
        id="global_loading_overlay",
        children=[
            html.Div(id="overlay_msg", children="Working…", style={"fontSize": "18px", "marginBottom": "10px"}),
            dbc.Spinner(size="lg")
        ],
        style=OVERLAY_OFF
    ),

    dbc.Row([
        # -----------------------------
        # Left panel: controls
        # -----------------------------
        dbc.Col(width=3, children=[
            dbc.Card(className="mt-3", children=[
                dbc.CardHeader("Controls"),
                dbc.CardBody([
                    dbc.Label("Seed tissue"),
                    dcc.Dropdown(
                        id="seed_tissue",
                        options=[{"label": t, "value": t} for t in TISSUES],
                        value="otu",
                        clearable=False,
                    ),

                    dbc.Button(
                        "Load seed IDs (top N)",
                        id="btn_load_seeds",
                        color="secondary",
                        className="w-100 mt-2"
                    ),

                    # Message directly above the dropdown (your requirement)
                    html.Div(
                        id="seed_loaded_msg",
                        className="mt-2",
                        style={
                            "fontSize": "12px",
                            "padding": "6px 8px",
                            "borderRadius": "8px",
                            "border": "1px solid #e6e6e6",
                            "background": "#fafafa",
                            "color": "#444"
                        },
                        children="No seeds loaded yet."
                    ),

                    dbc.Label("Seed ID (var2)", className="mt-2"),
                    dcc.Dropdown(
                        id="seed_id",
                        options=[],
                        value=None,
                        placeholder="Select seed id… (type to search)",
                        searchable=True,
                        clearable=True,
                    ),

                    html.Hr(),

                    dbc.Label("Allowed to_tissue"),
                    dcc.Dropdown(
                        id="allowed_to_tissues",
                        options=[{"label": t, "value": t} for t in TISSUES],
                        value=TISSUES,
                        multi=True,
                    ),

                    dbc.Label("TOP_K"),
                    dcc.Slider(
                        id="topk", min=1, max=10, step=1, value=DEFAULT_TOPK,
                        tooltip={"placement": "bottom"}
                    ),

                    dbc.Label("KN (max depth)"),
                    dcc.Slider(
                        id="kn", min=1, max=10, step=1, value=DEFAULT_KN,
                        tooltip={"placement": "bottom"}
                    ),

                    dbc.Label("abs(corr) threshold"),
                    dcc.Slider(
                        id="abs_thr", min=0.0, max=1.0, step=0.01, value=DEFAULT_ABS_THR,
                        tooltip={"placement": "bottom"}
                    ),

                    dbc.Label("accuracy ≥"),
                    dcc.Slider(
                        id="acc_min", min=0.0, max=1.0, step=0.01, value=DEFAULT_ACC_MIN,
                        tooltip={"placement": "bottom"}
                    ),

                    dbc.Label("corr range"),
                    dbc.Row([
                        dbc.Col(dbc.Input(id="corr_min", type="number", value=DEFAULT_CORR_MIN), width=6),
                        dbc.Col(dbc.Input(id="corr_max", type="number", value=DEFAULT_CORR_MAX), width=6),
                    ], className="mb-2"),

                    html.Hr(),

                    dbc.Label("Layout"),
                    dcc.Dropdown(
                        id="layout_name",
                        options=[{"label": k, "value": k} for k in LAYOUTS.keys()],
                        value="cose",
                        clearable=False,
                    ),

                    dbc.Label("ideal edge length"),
                    dcc.Slider(
                        id="ideal_len", min=20, max=200, step=5, value=80,
                        tooltip={"placement": "bottom"}
                    ),

                    dbc.Label("node repulsion"),
                    dcc.Slider(
                        id="repulsion", min=2000, max=20000, step=500, value=8000,
                        tooltip={"placement": "bottom"}
                    ),

                    html.Hr(),

                    dbc.Checklist(
                        id="show_labels",
                        options=[{"label": "Show labels", "value": "on"}],
                        value=["on"],
                        switch=True,
                    ),
                    dbc.Checklist(
                        id="focus_mode",
                        options=[{"label": "Focus mode (dim others)", "value": "on"}],
                        value=["on"],
                        switch=True,
                    ),

                    html.Hr(),

                    dbc.Label("Search / highlight node"),
                    dbc.Input(id="search_node", type="text", placeholder="Format: tissue::id"),
                    dbc.Button("Highlight", id="btn_highlight", color="info", className="w-100 mt-2"),

                    html.Hr(),

                    dbc.Button("Build graph", id="btn_build", color="primary", className="w-100"),
                    html.Div(id="build_status", className="mt-2"),
                ])
            ])
        ]),

        # -----------------------------
        # Right panel: visualization
        # -----------------------------
        dbc.Col(width=9, children=[
            dbc.Card(className="mt-3", children=[
                dbc.CardHeader("Network"),
                dbc.CardBody([
                    cyto.Cytoscape(
                        id="cy",
                        elements=[],
                        stylesheet=BASE_STYLE,
                        layout=LAYOUTS["cose"],
                        style={"width": "100%", "height": "650px"},
                        userPanningEnabled=True,
                        userZoomingEnabled=True,
                        boxSelectionEnabled=True,
                    ),

                    html.Hr(),
                    dbc.Row([
                        dbc.Col([
                            html.H6("Legend (node color = tissue)"),
                            build_legend(),
                        ], width=7),

                        dbc.Col([
                            html.H6("Edge details"),
                            html.Div(
                                id="hover_box",
                                children="Click an edge to see correlation details here.",
                                style={
                                    "border": "1px solid #ddd",
                                    "borderRadius": "10px",
                                    "background": "#fcfcfc",
                                    "padding": "10px",
                                    "fontSize": "12px",
                                    "minHeight": "58px"
                                }
                            ),
                        ], width=5),
                    ]),

                    html.Hr(),
                    html.H6("Correlation edges summary (current graph)"),
                    dash_table.DataTable(
                        id="edges_table",
                        columns=[
                            {"name": "level", "id": "level", "type": "numeric"},
                            {"name": "src_tissue", "id": "src_tissue"},
                            {"name": "src_id", "id": "src_id"},
                            {"name": "dst_tissue", "id": "dst_tissue"},
                            {"name": "dst_id", "id": "dst_id"},
                            {"name": "corr", "id": "corr", "type": "numeric"},
                            {"name": "abs_corr", "id": "abs_corr", "type": "numeric"},
                        ],
                        data=[],
                        page_size=15,
                        sort_action="native",
                        filter_action="native",
                        style_table={"overflowX": "auto"},
                        style_cell={"fontSize": "12px", "padding": "6px", "maxWidth": "420px"},
                        style_header={"fontWeight": "600"},
                    ),
                ])
            ]),

            dbc.Card(className="mt-3", children=[
                dbc.CardHeader("Report"),
                dbc.CardBody([
                    html.Pre(id="report", style={"whiteSpace": "pre-wrap", "margin": 0})
                ])
            ]),

            dbc.Card(className="mt-3", children=[
                dbc.CardHeader("Live activity (what the app is doing)"),
                dbc.CardBody([
                    dcc.Interval(id="log_poll", interval=700, n_intervals=0),
                    html.Pre(
                        id="live_log",
                        style={"whiteSpace": "pre-wrap", "margin": 0, "maxHeight": "220px", "overflowY": "auto"}
                    )
                ])
            ]),
        ])
    ]),

    dcc.Store(id="store_edges"),
    dcc.Store(id="store_layers"),
])


# -----------------------------------------------------------------------------
# Live log viewer
# -----------------------------------------------------------------------------
@app.callback(
    Output("live_log", "children"),
    Input("log_poll", "n_intervals"),
)
def show_live_log(_):
    if not os.path.exists(LOG_PATH):
        return "No logs yet."
    try:
        with open(LOG_PATH, "r", encoding="utf-8", errors="ignore") as f:
            lines = f.readlines()[-200:]
        return "".join(lines)
    except Exception as e:
        return f"Error reading log: {e}"


# -----------------------------------------------------------------------------
# Load TOP-N seeds
# -----------------------------------------------------------------------------
@app.callback(
    Output("seed_id", "options"),
    Output("seed_id", "value"),
    Output("seed_loaded_msg", "children"),
    Input("btn_load_seeds", "n_clicks"),
    State("seed_tissue", "value"),
    running=[
        (Output("global_loading_overlay", "style"), OVERLAY_ON, OVERLAY_OFF),
        (Output("overlay_msg", "children"), "Loading seed IDs…", "Working…"),
        (Output("seed_loaded_msg", "children"), "Loading seed IDs…", "No seeds loaded yet."),
    ],
    prevent_initial_call=True
)
def load_seed_ids(_n, seed_tissue):
    try:
        tbl = table_for(seed_tissue)
        seeds = fetch_seed_candidates(tbl, limit=MAX_SEEDS_LOAD)

        opts = [{"label": s, "value": s} for s in seeds]

        # keep UI lighter: do not auto-select any item
        default = None

        msg = (
            f"✅ Loaded {len(seeds):,} seed IDs from {tbl} (top {MAX_SEEDS_LOAD:,}). "
            "Type in the dropdown to search."
        )
        return opts, default, msg
    except Exception as e:
        return [], None, f"❌ Error loading seeds: {e}"


# -----------------------------------------------------------------------------
# Build graph
# -----------------------------------------------------------------------------
@app.callback(
    Output("store_edges", "data"),
    Output("store_layers", "data"),
    Output("build_status", "children"),
    Input("btn_build", "n_clicks"),
    State("seed_tissue", "value"),
    State("seed_id", "value"),
    State("kn", "value"),
    State("topk", "value"),
    State("acc_min", "value"),
    State("abs_thr", "value"),
    State("corr_min", "value"),
    State("corr_max", "value"),
    State("allowed_to_tissues", "value"),
    running=[
        (Output("global_loading_overlay", "style"), OVERLAY_ON, OVERLAY_OFF),
        (Output("overlay_msg", "children"), "Building graph… please wait", "Working…"),
    ],
    prevent_initial_call=True
)
def build(_n, seed_tissue, seed_id, kn, topk, acc_min, abs_thr, corr_min, corr_max, allowed_to_tissues):
    if not seed_tissue or not seed_id:
        return None, None, "Pick seed tissue + seed id."

    allowed = allowed_to_tissues or []
    if not allowed:
        return None, None, "allowed_to_tissues is empty."

    params = BuildParams(
        kn=int(kn),
        top_k=int(topk),
        acc_min=float(acc_min),
        abs_thr=float(abs_thr),
        corr_min=float(corr_min),
        corr_max=float(corr_max),
        allowed_to_tissues=[str(x) for x in allowed],
    )

    try:
        df_edges, layers = build_graph((str(seed_tissue), str(seed_id)), params)
        edges_data = df_edges.to_dict("records")
        layers_data = {f"{k[0]}::{k[1]}": int(v) for k, v in layers.items()}
        return edges_data, layers_data, f"Built graph: edges={len(df_edges):,}, nodes(layers map)={len(layers):,}"
    except Exception as e:
        return None, None, f"Build error: {e}"


# -----------------------------------------------------------------------------
# Fill summary table (capped)
# -----------------------------------------------------------------------------
@app.callback(
    Output("edges_table", "data"),
    Input("store_edges", "data"),
)
def fill_edges_table(edges_data):
    if not edges_data:
        return []
    edges_data = edges_data[:MAX_TABLE_ROWS]
    out = []
    for r in edges_data:
        out.append({
            "level": int(r.get("level", 0)),
            "src_tissue": r.get("src_tissue"),
            "src_id": r.get("src_id"),
            "dst_tissue": r.get("dst_tissue"),
            "dst_id": r.get("dst_id"),
            "corr": None if r.get("corr") is None else round(float(r["corr"]), 6),
            "abs_corr": None if r.get("abs_corr") is None else round(float(r["abs_corr"]), 6),
        })
    return out


# -----------------------------------------------------------------------------
# Render graph
# -----------------------------------------------------------------------------
@app.callback(
    Output("cy", "elements"),
    Output("cy", "layout"),
    Output("cy", "stylesheet"),
    Output("report", "children"),
    Input("store_edges", "data"),
    Input("store_layers", "data"),
    Input("cy", "tapNodeData"),
    Input("btn_highlight", "n_clicks"),
    State("layout_name", "value"),
    State("ideal_len", "value"),
    State("repulsion", "value"),
    State("search_node", "value"),
    State("show_labels", "value"),
    State("focus_mode", "value"),
    State("seed_tissue", "value"),
    State("seed_id", "value"),
)
def render(edges_data, layers_data, tapped, _h, layout_name, ideal_len, repulsion, search_node, show_labels, focus_mode, seed_tissue, seed_id):
    layout = dict(LAYOUTS.get(layout_name, LAYOUTS["cose"]))
    if layout.get("name") == "cose":
        layout.update({"idealEdgeLength": int(ideal_len), "nodeRepulsion": int(repulsion), "animate": True})

    if not layers_data:
        return [], layout, BASE_STYLE, "No graph built yet."

    layers = {}
    for cyid, d in layers_data.items():
        if "::" in cyid:
            t, nid = cyid.split("::", 1)
            layers[(t.strip(), nid.strip())] = int(d)

    df = pd.DataFrame(edges_data) if edges_data else pd.DataFrame()

    highlight = None
    if isinstance(search_node, str) and search_node.strip():
        highlight = search_node.strip()
    elif isinstance(tapped, dict) and tapped.get("id"):
        highlight = str(tapped["id"]).strip()

    keep_root = (str(seed_tissue).strip(), str(seed_id).strip()) if (seed_tissue and seed_id) else None
    elements = to_cytoscape_elements(df, layers, highlight=highlight, keep_root=keep_root)

    if ("on" in (focus_mode or [])) and highlight:
        elements = apply_focus(elements, highlight)

    style = [dict(x) for x in BASE_STYLE]
    for rule in style:
        if rule.get("selector") == "node":
            rule["style"] = dict(rule["style"])
            rule["style"]["text-opacity"] = 1.0 if ("on" in (show_labels or [])) else 0.0
            break

    used_nodes = set()
    if not df.empty:
        for _, r in df.iterrows():
            used_nodes.add((str(r["src_tissue"]).strip(), str(r["src_id"]).strip()))
            used_nodes.add((str(r["dst_tissue"]).strip(), str(r["dst_id"]).strip()))
    if keep_root:
        used_nodes.add(keep_root)

    max_depth = max((layers.get(n, 0) for n in used_nodes), default=0)
    per_depth = {}
    for n in used_nodes:
        d = layers.get(n, 0)
        per_depth[d] = per_depth.get(d, 0) + 1

    rep = [
        f"Seed: {seed_tissue}::{seed_id}",
        f"Displayed nodes: {len(used_nodes):,}",
        f"Edges: {0 if df.empty else len(df):,}",
        f"Max depth reached: {max_depth}",
        f"Nodes per depth: {dict(sorted(per_depth.items()))}",
        "Rule: global monotone abs(corr_child) > abs(corr_parent)",
        f"Highlight: {highlight}" if highlight else "Highlight: none",
        f"Layout: {layout.get('name')}",
    ]

    return elements, layout, style, "\n".join(rep)


# -----------------------------------------------------------------------------
# Edge click -> details box
# -----------------------------------------------------------------------------
@app.callback(
    Output("hover_box", "children"),
    Input("cy", "tapEdgeData"),
)
def show_edge_details(tap_edge):
    if not tap_edge:
        return "Click an edge to see correlation details here."

    src = tap_edge.get("source", "")
    dst = tap_edge.get("target", "")
    level = tap_edge.get("level", "")
    corr = tap_edge.get("corr", None)
    abs_corr = tap_edge.get("abs_corr", None)

    corr_txt = "n/a" if corr is None else f"{float(corr):.6f}"
    abs_txt = "n/a" if abs_corr is None else f"{float(abs_corr):.6f}"

    return html.Div([
        html.Div(f"Level: {level}"),
        html.Div(f"Source: {src}"),
        html.Div(f"Target: {dst}"),
        html.Div(f"Correlation: {corr_txt}"),
        html.Div(f"|corr|: {abs_txt}"),
    ])


if __name__ == "__main__":
    app.run(debug=True, host="127.0.0.1", port=8050)
