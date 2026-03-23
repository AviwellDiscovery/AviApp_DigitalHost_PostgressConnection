import time
import logging
from typing import List, Tuple, Dict, Any

from sqlalchemy import create_engine, text
from sqlalchemy.engine import Engine

from .config import DB_URL

logger = logging.getLogger(__name__)

# Create engine
engine: Engine = create_engine(DB_URL, pool_pre_ping=True)


def _build_in_clause(prefix: str, items: List[str], params: Dict[str, Any]) -> str:
    """
    Returns SQL "IN (:prefix0, :prefix1,...)" and fills params.
    """
    if not items:
        return "(NULL)"
    keys = []
    for i, v in enumerate(items):
        k = f"{prefix}{i}"
        params[k] = v
        keys.append(f":{k}")
    return "(" + ", ".join(keys) + ")"


def fetch_seed_candidates(table: str, limit: int = 10000) -> list:
    """
    Fetch seed candidates from the database.
    """
    if table == "avapp_tissuecorrelation":
        q = text("""
            SELECT var2
            FROM public.mv_seed_ileum
            ORDER BY var2
            LIMIT :lim
        """)
        src = "public.mv_seed_ileum"
    elif table == "avapp_tissuecorrelation_muscle":
        q = text("""
            SELECT var2
            FROM public.mv_seed_muscle
            ORDER BY var2
            LIMIT :lim
        """)
        src = "public.mv_seed_muscle"
    elif table == "avapp_tissuecorrelation_liver":
        q = text("""
            SELECT var2
            FROM public.mv_seed_liver
            ORDER BY var2
            LIMIT :lim
        """)
        src = "public.mv_seed_liver"
    else:
        q = text(f"""
            SELECT DISTINCT var2
            FROM {table}
            WHERE var2 IS NOT NULL
            ORDER BY var2
            LIMIT :lim
        """)
        src = table

    t0 = time.perf_counter()
    with engine.connect() as conn:
        rows = conn.execute(q, {"lim": int(limit)}).fetchall()
    dt = time.perf_counter() - t0

    logger.info(f"[SQL] fetch_seed_candidates src={src} limit={limit} rows={len(rows)} time={dt:.2f}s")
    return [r[0] for r in rows]


def fetch_neighbors_batch_monotone(
    table: str,
    sources_with_parent_abs: List[Tuple[str, float]],
    top_k: int,
    acc_min: float,
    abs_thr: float,
    corr_min: float,
    corr_max: float,
    allowed_to_tissues: List[str],
):
    """
    For each source var2, fetch TOP_K neighbors (var1) ranked by ABS(correlation) DESC,
    subject to:
      - accuracy >= acc_min
      - corr between corr_min and corr_max
      - ABS(corr) >= abs_thr
      - monotone: ABS(corr_child) > parent_abs
      - to_tissue in allowed_to_tissues (if provided)

    Returns DataFrame columns:
      var2, parent_abs, var1, to_tissue, correlation, pvalue, accuracy, min, max
    """
    import pandas as pd

    if not sources_with_parent_abs:
        return pd.DataFrame(columns=[
            "var2", "parent_abs", "var1", "to_tissue", "correlation", "pvalue", "accuracy", "min", "max"
        ])

    params: Dict[str, Any] = {
        "top_k": int(top_k),
        "acc_min": float(acc_min),
        "abs_thr": float(abs_thr),
        "corr_min": float(corr_min),
        "corr_max": float(corr_max),
    }

    values_rows = []
    for i, (v, pabs) in enumerate(sources_with_parent_abs):
        vk = f"v{i}"
        pk = f"p{i}"
        params[vk] = v
        params[pk] = float(pabs)
        values_rows.append(f"(:{vk}, :{pk})")
    values_sql = ", ".join(values_rows)

    tissue_filter_sql = ""
    if allowed_to_tissues:
        in_sql = _build_in_clause("tiss", allowed_to_tissues, params)
        tissue_filter_sql = f" AND t.to_tissue IN {in_sql} "

    sql = text(f"""
        WITH srcs(var2, parent_abs) AS (
            VALUES {values_sql}
        ),
        ranked AS (
            SELECT
                t.var2,
                s.parent_abs,
                t.var1,
                t.to_tissue,
                t.correlation,
                t.pvalue,
                t.accuracy,
                t.min,
                t.max,
                ROW_NUMBER() OVER (
                    PARTITION BY t.var2
                    ORDER BY ABS(t.correlation) DESC
                ) AS rn
            FROM {table} t
            JOIN srcs s
              ON t.var2 = s.var2
            WHERE
                t.accuracy >= :acc_min
                AND t.correlation >= :corr_min
                AND t.correlation <= :corr_max
                AND ABS(t.correlation) >= :abs_thr
                AND ABS(t.correlation) > s.parent_abs
                {tissue_filter_sql}
        )
        SELECT
            var2, parent_abs, var1, to_tissue, correlation, pvalue, accuracy, min, max
        FROM ranked
        WHERE rn <= :top_k
        ORDER BY var2, rn
    """)

    t0 = time.perf_counter()
    with engine.connect() as conn:
        result = conn.execute(sql, params)
        rows = result.fetchall()
        cols = list(result.keys())
    dt = time.perf_counter() - t0

    logger.info(f"[SQL] fetch_neighbors_batch_monotone table={table} sources={len(sources_with_parent_abs)} rows={len(rows)} time={dt:.2f}s")

    if not rows:
        return pd.DataFrame(columns=[
            "var2", "parent_abs", "var1", "to_tissue", "correlation", "pvalue", "accuracy", "min", "max"
        ])

    return pd.DataFrame(rows, columns=cols)