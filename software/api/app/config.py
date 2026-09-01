from pathlib import Path


BASE_DIR = Path(__file__).resolve().parent.parent
DATABASE_FILE = BASE_DIR / "safe.sqlite3"

DATABASE_URL = f"sqlite:///{DATABASE_FILE.as_posix()}"