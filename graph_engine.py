from __future__ import annotations
from dataclasses import dataclass
from typing import Dict, List, Tuple

import pandas as pd

from config import MAX_FRONTIER_PER_LEVEL, MAX_EDGES_TOTAL
from router import table_for
from repo import fetch_neighbors_batch_monotone
from logger import log

NodeKey = Tuple[str, str]  # (tissue, id)

@dataclass
class BuildParams:
    kn: int
    top_k: int
    acc_min: float
    abs_thr: float
    corr_min: float
    corr_max: float
    allowed_to_tissues: List[str]

def group_frontier_by_tissue(frontier: List[Tuple[NodeKey, float]]) -> Dict[str, List[Tuple[str, float]]]:
    groups: Dict[str, List[Tuple[str, float]]] = {}
    for (tissue, node_id), parent_abs in frontier:
        groups.setdefault(tissue, []).append((node_id, float(parent_abs)))
    return groups

def build_graph(seed: NodeKey, params: BuildParams) -> tuple[pd.DataFrame, Dict[NodeKey, int]]:
    seed_tissue, seed_id = seed

    layers: Dict[NodeKey, int] = {seed: 0}
    visited = {seed}
    frontier: List[Tuple[NodeKey, float]] = [(seed, 0.0)]
    edge_rows: List[dict] = []

    log(f"[GraphEngine] START seed={seed_tissue}::{seed_id} KN={params.kn} TOP_K={params.top_k}")

    for depth in range(1, params.kn + 1):
        if not frontier:
            log(f"[GraphEngine] STOP depth={depth} frontier=0")
            break

        if len(frontier) > MAX_FRONTIER_PER_LEVEL:
            log(f"[GraphEngine] DEPTH={depth} frontier capped {len(frontier)} -> {MAX_FRONTIER_PER_LEVEL}")
            frontier = frontier[:MAX_FRONTIER_PER_LEVEL]

        log(f"[GraphEngine] DEPTH={depth} frontier={len(frontier)}")

        groups = group_frontier_by_tissue(frontier)
        log(f"[GraphEngine] DEPTH={depth} tissues={list(groups.keys())}")

        next_frontier_map: Dict[NodeKey, float] = {}

        for tissue, sources in groups.items():
            table = table_for(tissue)
            log(f"[GraphEngine] DEPTH={depth} tissue={tissue} sources={len(sources)} table={table}")

            df = fetch_neighbors_batch_monotone(
                table=table,
                sources_with_parent_abs=sources,
                top_k=params.top_k,
                acc_min=params.acc_min,
                abs_thr=params.abs_thr,
                corr_min=params.corr_min,
                corr_max=params.corr_max,
                allowed_to_tissues=params.allowed_to_tissues,
            )

            if df.empty:
                log(f"[GraphEngine] DEPTH={depth} tissue={tissue} rows=0")
                continue

            log(f"[GraphEngine] DEPTH={depth} tissue={tissue} rows={len(df)} building edges")

            for _, r in df.iterrows():
                src = (tissue, str(r["var2"]))
                dst = (str(r["to_tissue"]), str(r["var1"]))
                corr = float(r["correlation"])
                abs_corr = abs(corr)

                edge_rows.append({
                    "level": depth,
                    "src_tissue": src[0],
                    "src_id": src[1],
                    "dst_tissue": dst[0],
                    "dst_id": dst[1],
                    "corr": corr,
                    "abs_corr": abs_corr,
                    "accuracy": float(r["accuracy"]) if pd.notna(r["accuracy"]) else None,
                    "pvalue": float(r["pvalue"]) if pd.notna(r["pvalue"]) else None,
                    "parent_abs": float(r["parent_abs"]),
                })

                layers.setdefault(src, depth - 1)
                layers.setdefault(dst, depth)

                if dst not in visited:
                    visited.add(dst)
                    prev = next_frontier_map.get(dst, 0.0)
                    next_frontier_map[dst] = max(prev, abs_corr)

                if len(edge_rows) >= MAX_EDGES_TOTAL:
                    log("[GraphEngine] STOP max edges reached")
                    break

            if len(edge_rows) >= MAX_EDGES_TOTAL:
                break

        frontier = [(nk, next_frontier_map[nk]) for nk in next_frontier_map.keys()]
        log(f"[GraphEngine] DEPTH={depth} next_frontier={len(frontier)}")

    df_edges = pd.DataFrame(edge_rows)
    log(f"[GraphEngine] END edges={len(df_edges)} visited={len(visited)} layers={len(layers)}")
    return df_edges, layers

