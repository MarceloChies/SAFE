import os
from pathlib import Path


BASE_DIR = Path(__file__).resolve().parent.parent
DATABASE_FILE = BASE_DIR / "safe.sqlite3"

DATABASE_URL_PADRAO = (
    f"sqlite:///{DATABASE_FILE.as_posix()}"
)

DATABASE_URL = os.getenv(
    "DATABASE_URL",
    DATABASE_URL_PADRAO,
)