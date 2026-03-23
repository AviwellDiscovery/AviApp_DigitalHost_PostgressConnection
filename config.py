import os

# ---- DB (override with env vars) ----
PGHOST = os.getenv("PGHOST", "localhost")
PGPORT = os.getenv("PGPORT", "5432")
PGDATABASE = os.getenv("PGDATABASE", "devdatabase_16_11")
PGUSER = os.getenv("PGUSER", "reda")
PGPASSWORD = os.getenv("PGPASSWORD", "")

DB_URL = os.getenv(
    "DATABASE_URL",
    f"postgresql+psycopg2://{PGUSER}:{PGPASSWORD}@{PGHOST}:{PGPORT}/{PGDATABASE}"
)

# ---- Tissues supported ----
TISSUES = ["otu", "ileum", "muscle", "liver", "metab"]

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

