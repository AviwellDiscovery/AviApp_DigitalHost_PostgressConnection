from .config import TISSUES

TABLE_BY_TISSUE = {
    "otu":   "avapp_tissuecorrelation_otu",
    "ileum": "avapp_tissuecorrelation",
    "muscle": "avapp_tissuecorrelation_muscle",
    "liver": "avapp_tissuecorrelation_liver",
    "metab": "avapp_tissuecorrelation_metab",
}

def table_for(tissue: str) -> str:
    t = (tissue or "").strip().lower()
    if t not in TABLE_BY_TISSUE:
        raise ValueError(f"Unknown tissue '{tissue}'. Allowed: {list(TABLE_BY_TISSUE)}")
    return TABLE_BY_TISSUE[t]

def all_tissues():
    return list(TISSUES)