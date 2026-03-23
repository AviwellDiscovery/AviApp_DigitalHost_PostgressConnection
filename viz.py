from __future__ import annotations

from copy import deepcopy
import pandas as pd
from dash import html


def cy_id(tissue: str, node_id: str) -> str:
    """Typed Cytoscape ID to avoid cross-omic collisions (normalized)."""
    return f"{str(tissue).strip()}::{str(node_id).strip()}"


def cy_label(node_id: str, max_len: int = 36) -> str:
    s = str(node_id)
    return s if len(s) <= max_len else s[: max_len - 1] + "…"


TISSUE_COLOR = {
    "otu":   "#1f77b4",
    "ileum": "#2ca02c",
    "muscle":"#ff7f0e",
    "liver": "#d62728",
    "metab": "#9467bd",
}


def build_legend():
    items = []
    for tissue, color in TISSUE_COLOR.items():
        items.append(
            html.Div(
                [
                    html.Span(
                        style={
                            "display": "inline-block",
                            "width": "12px",
                            "height": "12px",
                            "backgroundColor": color,
                            "border": "1px solid #333",
                            "borderRadius": "2px",
                            "marginRight": "6px",
                        }
                    ),
                    html.Span(tissue, style={"fontSize": "12px"}),
                ],
                style={
                    "display": "inline-flex",
                    "alignItems": "center",
                    "marginRight": "12px",
                    "marginBottom": "6px",
                },
            )
        )

    return html.Div(
        items,
        style={
            "display": "flex",
            "flexWrap": "wrap",
            "alignItems": "center",
            "gap": "4px 8px",
            "padding": "6px 10px",
            "border": "1px solid #ddd",
            "borderRadius": "10px",
            "background": "#fafafa",
        },
    )


BASE_STYLE = [
    {
        "selector": "node",
        "style": {
            "label": "data(label)",
            "text-opacity": 0.0,
            "font-size": 10,
            "background-color": "data(color)",
            "border-width": 1,
            "border-color": "#222",
            "width": "mapData(degree, 1, 50, 18, 42)",
            "height": "mapData(degree, 1, 50, 18, 42)",
        },
    },
    {
        "selector": "edge",
        "style": {
            "curve-style": "bezier",
            "opacity": 0.65,
            "width": "mapData(abs_corr, 0, 1, 1, 7)",
            "line-color": "mapData(corr, -1, 1, #d62828, #1d3557)",
        },
    },
    {"selector": ".highlight", "style": {"border-width": 5, "border-color": "#000", "z-index": 9999}},
    {"selector": ".dim", "style": {"opacity": 0.12}},
    {"selector": ".focusEdge", "style": {"opacity": 0.95, "width": 5}},
]


LAYOUTS = {
    "cose": {"name": "cose", "animate": True},
    "breadthfirst": {"name": "breadthfirst", "directed": True, "animate": True, "spacingFactor": 1.2},
    "concentric": {"name": "concentric", "animate": True},
    "grid": {"name": "grid"},
    "circle": {"name": "circle"},
}


def to_cytoscape_elements(
    df_edges: pd.DataFrame,
    layers: dict,                     # (tissue,id) -> int
    highlight: str | None,
    keep_root: tuple[str, str] | None,
) -> list[dict]:
    elements: list[dict] = []

    if df_edges is None or df_edges.empty:
        if keep_root:
            t, nid = keep_root
            node_cy = cy_id(t, nid)
            elements.append(
                {
                    "data": {
                        "id": node_cy,
                        "label": cy_label(nid),
                        "layer": 0,
                        "degree": 0,
                        "color": TISSUE_COLOR.get(str(t).strip(), "#999"),
                        "tissue": str(t).strip(),
                        "full_id": str(nid).strip(),
                    },
                    "classes": "highlight" if highlight == node_cy else "",
                }
            )
        return elements

    used: set[tuple[str, str]] = set()
    for _, r in df_edges.iterrows():
        used.add((str(r["src_tissue"]).strip(), str(r["src_id"]).strip()))
        used.add((str(r["dst_tissue"]).strip(), str(r["dst_id"]).strip()))

    if keep_root:
        used.add((str(keep_root[0]).strip(), str(keep_root[1]).strip()))

    deg: dict[tuple[str, str], int] = {n: 0 for n in used}
    for _, r in df_edges.iterrows():
        s = (str(r["src_tissue"]).strip(), str(r["src_id"]).strip())
        d = (str(r["dst_tissue"]).strip(), str(r["dst_id"]).strip())
        deg[s] = deg.get(s, 0) + 1
        deg[d] = deg.get(d, 0) + 1

    for (t, nid) in used:
        node_cy = cy_id(t, nid)
        cls = "highlight" if (highlight and node_cy == highlight) else ""
        elements.append(
            {
                "data": {
                    "id": node_cy,
                    "label": cy_label(nid),
                    "tissue": t,
                    "layer": int(layers.get((t, nid), 0)),
                    "degree": int(deg.get((t, nid), 0)),
                    "color": TISSUE_COLOR.get(t, "#999"),
                    "full_id": nid,
                },
                "classes": cls,
            }
        )

    df2 = df_edges.reset_index(drop=True)
    for i, r in df2.iterrows():
        src_t = str(r["src_tissue"]).strip()
        src_id = str(r["src_id"]).strip()
        dst_t = str(r["dst_tissue"]).strip()
        dst_id = str(r["dst_id"]).strip()

        s = cy_id(src_t, src_id)
        d = cy_id(dst_t, dst_id)

        corr = float(r["corr"])
        abs_corr = float(r["abs_corr"])
        level = int(r["level"])

        elements.append(
            {
                "data": {
                    "id": f"e{i}",
                    "source": s,
                    "target": d,
                    "corr": corr,
                    "abs_corr": abs_corr,
                    "level": level,
                    "src_tissue": src_t,
                    "src_id": src_id,
                    "dst_tissue": dst_t,
                    "dst_id": dst_id,
                    "tooltip": f"level={level} | corr={corr:.6f} | abs={abs_corr:.6f}",
                }
            }
        )

    return elements


def apply_focus(elements: list[dict], focus_node_cy: str | None) -> list[dict]:
    if not focus_node_cy:
        return elements

    neigh = {focus_node_cy}
    for el in elements:
        d = el.get("data", {})
        if "source" in d and "target" in d:
            if d["source"] == focus_node_cy:
                neigh.add(d["target"])
            if d["target"] == focus_node_cy:
                neigh.add(d["source"])

    out = []
    for el in elements:
        el2 = deepcopy(el)
        classes = set((el2.get("classes") or "").split())
        d = el2.get("data", {})

        if "source" in d and "target" in d:
            if d["source"] in neigh and d["target"] in neigh:
                classes.add("focusEdge")
            else:
                classes.add("dim")
        else:
            if d.get("id") not in neigh:
                classes.add("dim")

        el2["classes"] = " ".join(sorted(c for c in classes if c))
        out.append(el2)

    return out
