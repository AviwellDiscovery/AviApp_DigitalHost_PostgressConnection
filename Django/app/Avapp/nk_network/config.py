import os
from urllib.parse import quote_plus
from django.conf import settings

# ---- DB Configuration ----
# Keep NK network DB access aligned with Django DB settings.
_db = settings.DATABASES.get("default", {})

PGHOST = os.getenv("PGHOST") or os.getenv("DB_HOST") or _db.get("HOST") or "localhost"
PGPORT = os.getenv("PGPORT") or os.getenv("DB_PORT") or str(_db.get("PORT") or "5432")
PGDATABASE = os.getenv("PGDATABASE") or os.getenv("DB_NAME") or _db.get("NAME") or "devdatabase_16_11"
PGUSER = os.getenv("PGUSER") or os.getenv("DB_USER") or _db.get("USER") or "reda"
PGPASSWORD = os.getenv("PGPASSWORD") or os.getenv("DB_PASSWORD") or (_db.get("PASSWORD") or "")

_db_url_from_env = os.getenv("DATABASE_URL")
if _db_url_from_env:
    DB_URL = _db_url_from_env
else:
    user_enc = quote_plus(str(PGUSER))
    host_enc = str(PGHOST)
    port_enc = str(PGPORT)
    db_enc = quote_plus(str(PGDATABASE))
    if PGPASSWORD:
        pwd_enc = quote_plus(str(PGPASSWORD))
        DB_URL = f"postgresql+psycopg2://{user_enc}:{pwd_enc}@{host_enc}:{port_enc}/{db_enc}"
    else:
        DB_URL = f"postgresql+psycopg2://{user_enc}@{host_enc}:{port_enc}/{db_enc}"

# ---- Tissues supported ----
TISSUES = ["otu", "ileum", "muscle", "liver", "metab"]

# ---- Tissue labels for display ----
TISSUE_LABELS = {
    "otu": "OTU (Microbiome)",
    "ileum": "Ileum",
    "muscle": "Muscle",
    "liver": "Liver",
    "metab": "Metabolic"
}

# ---- Defaults ----
DEFAULT_TOPK = 5
DEFAULT_KN = 3
DEFAULT_ABS_THR = 0.0
DEFAULT_ACC_MIN = 0.0
DEFAULT_CORR_MIN = -5.0
DEFAULT_CORR_MAX = 5.0

# Optional safety caps (avoid huge graphs)
MAX_FRONTIER_PER_LEVEL = 10000     # cap frontier size
MAX_EDGES_TOTAL = 100000          # cap edges total
